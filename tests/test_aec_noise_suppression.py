import pytest
import math
from media import aec_noise_suppression as mod

CASES = [
    ("delay", 'm.delay_index(2, 1, 8) == 1'),
    ("drift", 'm.drift_count(1000, 0) == 1000'),
    ("double", 'm.double_talk(10, 1, 2) is True'),
    ("residual", 'm.residual(1, 2) == 3'),
    ("resample", 'm.resample_count(480, 48000, 24000) == 240'),
    ("underrun", 'm.underrun(10, 12) == 2'),
    ("order", 'm.pipeline_order(False) == "aec-first"'),
    ("gain", 'm.apply_gain(2, 0.5) == approx(1.0)'),
    ("reset", 'm.reset_on_change(True) is True'),
    ("limit", 'm.limit_reference(2, 1) == 1'),
    ("erle", 'm.erle(4, 1) == 3'),
    ("converge", 'm.converge(10, 0.5) == approx(5.0)'),
    ("db", 'm.erle_db(10) == approx(10.0)'),
    ("diverged", 'm.diverged(1.2) is True'),
    ("id", 'm.aec_id(3, 2) == "3:2"')
]

@pytest.mark.parametrize("name,expr", CASES, ids=[c[0] for c in CASES])
def test_contract(name, expr):
    assert eval(expr, {"m": mod, "approx": pytest.approx, "math": math})
