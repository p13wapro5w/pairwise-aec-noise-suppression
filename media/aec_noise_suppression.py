import math

def delay_index(index, delay, length):
    """参考延迟对齐。"""
    raise NotImplementedError("TODO: delay_index")

def drift_count(samples, ppm):
    """时钟漂移。"""
    raise NotImplementedError("TODO: drift_count")

def double_talk(near, far, threshold):
    """双讲检测。"""
    raise NotImplementedError("TODO: double_talk")

def residual(linear, nonlinear):
    """非线性残差。"""
    raise NotImplementedError("TODO: residual")

def resample_count(count, source_rate, target_rate):
    """重采样长度。"""
    raise NotImplementedError("TODO: resample_count")

def underrun(frames, needed):
    """欠载补齐。"""
    raise NotImplementedError("TODO: underrun")

def pipeline_order(denoise_first):
    """处理顺序。"""
    raise NotImplementedError("TODO: pipeline_order")

def apply_gain(gain, aec):
    """增益位置。"""
    raise NotImplementedError("TODO: apply_gain")

def reset_on_change(room_changed):
    """场景重置。"""
    raise NotImplementedError("TODO: reset_on_change")

def limit_reference(value, ceiling):
    """参考限幅。"""
    raise NotImplementedError("TODO: limit_reference")

def erle(near, residual_value):
    """回声抑制量。"""
    raise NotImplementedError("TODO: erle")

def converge(error, step):
    """滤波器收敛。"""
    raise NotImplementedError("TODO: converge")

def erle_db(ratio):
    """ERLE 分贝。"""
    raise NotImplementedError("TODO: erle_db")

def diverged(coefficient):
    """发散判定。"""
    raise NotImplementedError("TODO: diverged")

def aec_id(seed, index):
    """AEC id。"""
    raise NotImplementedError("TODO: aec_id")
