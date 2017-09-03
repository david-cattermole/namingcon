"""
Example functions that return hard-coded values. 
"""


def get_asset_names():
    return [
        'asset', 'john', 'character', 'jane'
    ]


def get_shot_names():
    return [
        'shot',
        'sh001', 'sh002', 'sh003',
        'sh005', 'sh010', 'sh015', 'sh020',
        'sh0100', 'sh0110', 'sh0120', 'sh0130'
    ]


def get_sequence_names():
    return [
        'sequence', 'sh', 'fin', 'sg', 'pb'
    ]


def get_project_names():
    return [
        'project', 'babydriver', 'proj', 'car'
    ]


def get_department_names():
    return [
        'department',
        'layout', 'matchmove', 'tracking',
        'light', 'shader', 'effects',
        'rigging', 'modelling', 'animation'
    ]


def get_image_file_extensions():
    ext = [
        "hdr",
        "exr",
        "jpg",
        "png",
        "tga",
        "tif",
        "tiff",
        "tex"
    ]
    return sorted(ext)


def get_geometry_file_extensions():
    ext = [
        "fbx",
        "abc",
        "obj",
        "usd",
        "ma",
        "mb",
    ]
    return sorted(ext)


def get_maya_scene_file_extensions():
    ext = [
        "ma",
        "mb"
    ]
    return sorted(ext)


def get_all_file_extensions():
    ext = [
        "fbx", "abc", "obj", "usd",
        "exr", "jpg", "png", "tga", "tif", "tiff", "tex", "hdr",
        "3dlut", "lut",
        "anim", "atom", "chan",
        "ma", "mb",
        "mov", "webm", "avi", "mp4", "mkv"
        "3de", "hip", "nk", "otl",
        "wav", "mp3", "acc", "m4a", "flac",
        "mel", "py",
        "xml", "json", "yaml",
    ]
    return sorted(ext)


def get_separator_chars():
    return ['.', '_']