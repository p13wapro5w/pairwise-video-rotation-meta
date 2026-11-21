import pytest
import math
from media import video_rotation_meta as mod

CASES = [
    ("norm", 'm.normalize_rotation(-90) == 270'),
    ("swap", 'm.swap_dims(1920, 1080, 90) == (1080, 1920)'),
    ("rect", 'm.rotate_rect((0, 0, 4, 2), 90) == (0, 0, 2, 4)'),
    ("double", 'm.double_rotate(90, 90) == 180'),
    ("hdr", 'm.keep_hdr(True) is True'),
    ("thumb", 'm.thumbnail_rotation(90, 0) == 0'),
    ("dims", 'm.display_dims(1920, 1080, 0) == (1920, 1080)'),
    ("clear", 'm.clear_old(90) == 0'),
    ("subtitle", 'm.subtitle_coord(0, 0, 90) == approx((0.0, 1.0))'),
    ("key", 'm.rotation_key(3, 2) == "3:2"'),
    ("portrait", 'm.is_portrait(90) is True'),
    ("sar", 'm.sample_aspect(1, 90) == 1'),
    ("valid", 'm.valid_matrix(180) is True'),
    ("transpose", 'm.transpose_rect((1, 2, 3, 4)) == (1, 2, 4, 3)'),
    ("rotated", 'm.is_rotated(0) is False')
]

@pytest.mark.parametrize("name,expr", CASES, ids=[c[0] for c in CASES])
def test_contract(name, expr):
    assert eval(expr, {"m": mod, "approx": pytest.approx, "math": math})
