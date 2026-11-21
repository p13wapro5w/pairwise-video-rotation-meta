import math

# 旋转元数据的合法取值：容器 display matrix 只会给出这四个角度。
VALID_ROTATIONS = (0, 90, 180, 270)


def _as_rotation(rotation):
    """把任意角度规整到 0/90/180/270，非法输入按 0 处理。"""
    if rotation is None:
        return 0
    try:
        value = int(round(float(rotation)))
    except (TypeError, ValueError):
        return 0
    value %= 360
    return value if value in VALID_ROTATIONS else 0


def normalize_rotation(degrees):
    """旋转归一。

    读取 display matrix 后先把角度折回 [0, 360)，保证 -90 与 270 等价，
    后续所有判断都基于归一化后的值，避免累计旋转漂移。
    """
    return _as_rotation(degrees)


def swap_dims(width, height, rotation):
    """宽高交换。

    旋转元数据为 90/270 时，存储方向与显示方向正交，显示宽高必须交换；
    0/180 时保持原样。
    """
    if _as_rotation(rotation) in (90, 270):
        return (height, width)
    return (width, height)


def rotate_rect(rect, rotation):
    """裁剪旋转。

    裁剪应当在旋转之后进行，返回裁剪框在显示方向下的 (x, y, w, h)。
    90/270 时裁剪框自己转置，宽高互换；0/180 时不变。
    """
    x, y, w, h = rect
    if _as_rotation(rotation) in (90, 270):
        return (x, y, h, w)
    return (x, y, w, h)


def double_rotate(auto, manual):
    """双重旋转。

    把自动旋转（autorotate）与手动旋转合并成一个最终角度：
    先归一化再相加取模，调用方只应用一次旋转，避免重复应用。
    """
    return _as_rotation(_as_rotation(auto) + _as_rotation(manual))


def keep_hdr(flag):
    """HDR 保留。

    旋转只改变几何信息，不改变色彩元数据；HDR 标记必须原样带到输出流。
    """
    return bool(flag)


def thumbnail_rotation(exif, container):
    """缩略图方向。

    缩略图优先读取容器内的 display matrix；容器没有矩阵时才回退到 EXIF。
    """
    source = container if container is not None else exif
    return _as_rotation(source)


def display_dims(width, height, rotation):
    """显示尺寸。

    按 display matrix 换算播放器实际看到的宽高，旋转 90/270 时交换。
    """
    return swap_dims(width, height, rotation)


def clear_old(rotation):
    """清除旧矩阵。

    重新写入旋转前必须清掉旧的 display matrix，否则每次转码都会在旧角度上
    再累加一次。清除后的值固定为 0。
    """
    return 0


def subtitle_coord(x, y, rotation):
    """字幕坐标。

    字幕使用归一化坐标（原点在左上角，x 向右、y 向下），需要跟随画面一起
    旋转到显示坐标系。旋转 90 时 (x, y) -> (y, 1 - x)。
    """
    rotation = _as_rotation(rotation)
    if rotation == 90:
        return (y, 1.0 - x)
    if rotation == 180:
        return (1.0 - x, 1.0 - y)
    if rotation == 270:
        return (1.0 - y, x)
    return (x, y)


def rotation_key(seed, index):
    """旋转键。

    生成稳定的旋转缓存键，种子与序号用冒号连接。
    """
    return f"{seed}:{index}"


def is_portrait(rotation):
    """竖屏判定。

    旋转 90/270 后画面为竖向（高大于宽）。
    """
    return _as_rotation(rotation) in (90, 270)


def sample_aspect(aspect, rotation):
    """宽高比。

    交换宽高后样本宽高比（SAR）需要取倒数重新计算，否则像素会变成非方形；
    0/180 时保持不变。
    """
    if _as_rotation(rotation) in (90, 270):
        return 1 / aspect if aspect else aspect
    return aspect


def valid_matrix(rotation):
    """矩阵合法。

    容器 display matrix 只接受 0/90/180/270 这四个角度。
    """
    if rotation is None:
        return False
    try:
        value = int(round(float(rotation)))
    except (TypeError, ValueError):
        return False
    return value % 360 in VALID_ROTATIONS


def transpose_rect(rect):
    """矩形转置。

    交换矩形的宽高、保持左上角坐标不变，用于旋转后的裁剪框换算。
    """
    x, y, w, h = rect
    return (x, y, h, w)


def is_rotated(rotation):
    """旋转判定。

    归一化后角度非 0 即表示画面需要旋转。
    """
    return _as_rotation(rotation) != 0
