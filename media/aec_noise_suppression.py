"""回声消除（AEC）与噪声抑制的核心处理工具。

对应十个修复点：
1. 参考延迟对齐 —— delay_index
2. 时钟漂移补偿 —— drift_count
3. 双讲检测 —— double_talk
4. 非线性残差抑制 —— residual
5. 统一采样率 —— resample_count
6. 欠载保护 —— underrun
7. AEC 先于降噪 —— pipeline_order
8. 增益在 AEC 之后 —— apply_gain
9. 场景变化重置 —— reset_on_change
10. 参考信号限幅 —— limit_reference

其余函数为滤波器收敛/发散与回声抑制量（ERLE）的度量辅助。
"""

import math


def delay_index(index, delay, length):
    """参考延迟对齐。

    参考信号比麦克风晚到（例如 200ms），自适应滤波器需要沿环形参考缓冲
    回退 ``delay`` 个采样取对齐样本。索引按 ``length`` 取模回绕。
    """
    return (index - delay) % length


def drift_count(samples, ppm):
    """时钟漂移补偿。

    声卡与采集时钟存在偏差（ppm，百万分之一），按漂移率修正参考侧的
    采样计数，避免参考与采集每十分钟累积出几十毫秒偏差导致滤波器发散。
    负 ppm 表示参考时钟偏慢。返回四舍五入后的整数采样数。
    """
    return round(samples * (1.0 + ppm / 1_000_000.0))


def double_talk(near, far, threshold):
    """双讲检测。

    近端（麦克风）能量相对远端（参考）能量超过 ``threshold`` 倍即判定为
    双讲，此时应冻结自适应滤波器系数，避免把近端语音当成回声削掉。
    用乘法比较，避免远端能量为 0 时除零。
    """
    return bool(near > far * threshold)


def residual(linear, nonlinear):
    """非线性残差抑制。

    线性 AEC 输出中仍残留扬声器非线性失真等无法线性建模的回声，
    残差抑制量为线性残差与非线性残差两部分之和，交给非线性处理器（NLP）压制。
    """
    return linear + nonlinear


def resample_count(count, source_rate, target_rate):
    """统一采样率后的重采样长度。

    48k 与 44.1k 混用会使重采样后的参考信号相位不一致，必须先统一到
    同一采样率；返回 ``count`` 个源采样在目标采样率下对应的（整数）采样数。
    """
    return round(count * target_rate / source_rate)


def underrun(frames, needed):
    """欠载保护。

    缓冲欠载时返回需要补齐的帧数（插零/静音），并由调用方据此暂停自适应，
    防止滤波器把静音段误判成双讲。帧数充足时返回 0。
    """
    return max(0, needed - frames)


def pipeline_order(denoise_first):
    """处理顺序。

    噪声抑制必须在 AEC 之后执行：先降噪会破坏回声路径估计所需的参考相关性。
    ``denoise_first`` 为 False（正确顺序）时返回 ``"aec-first"``。
    """
    return "denoise-first" if denoise_first else "aec-first"


def apply_gain(gain, aec):
    """增益位置。

    自动增益控制放在 AEC 之后，对已消除回声的信号施加增益，
    避免 AEC 之前的音量变化迫使滤波器反复重新收敛。
    """
    return aec * gain


def reset_on_change(room_changed):
    """场景变化重置。

    房间声学特性变化（换房间、移动设备）后旧的滤波器系数不再匹配，
    检测到变化时返回 True，触发系数重置与重新收敛。
    """
    return bool(room_changed)


def limit_reference(value, ceiling):
    """参考信号限幅。

    播放端音量拉满会削波，削波后的参考无法被线性回声路径建模。
    在送入 AEC 前把参考样本限制在 [-ceiling, ceiling] 区间。
    """
    if value > ceiling:
        return ceiling
    if value < -ceiling:
        return -ceiling
    return value


def erle(near, residual_value):
    """回声抑制量（功率域差值）。

    ERLE = 近端回声功率 - 残差功率，单位与输入一致（通常为 dB 或线性功率），
    差值越大说明回声消除得越干净。
    """
    return near - residual_value


def converge(error, step):
    """滤波器收敛步进。

    每帧按步长 ``step`` 收窄估计误差，残差按 ``(1 - step)`` 比例衰减；
    双讲或欠载期间应冻结步进，不调用本函数。
    """
    return error * (1.0 - step)


def erle_db(ratio):
    """ERLE 分贝换算。

    输入为近端功率与残差功率之比（线性），返回 10*log10 的分贝值。
    例如 ratio=10 对应 10 dB 的回声抑制。
    """
    return 10.0 * math.log10(ratio)


def diverged(coefficient):
    """发散判定。

    滤波器系数幅值超过稳定边界（1.0）说明自适应已发散
    （典型于时钟漂移累积或参考失配），应重置系数重新收敛。
    """
    return bool(abs(coefficient) > 1.0)


def aec_id(seed, index):
    """AEC 会话标识。

    用随机种子与帧序号组合生成稳定的流内标识，便于对齐参考帧与采集帧、
    排查延迟与漂移问题。
    """
    return f"{seed}:{index}"
