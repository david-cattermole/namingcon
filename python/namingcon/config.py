"""
Functions to read config files.
"""

import os
import os.path
import json


from namingcon.cache import memoized


@memoized
def __readData(filePath):
    """
    Read file path as JSON data format.

    :param filePath: File path to .json file.
    :return: Contents of the .json file.
    """
    f = open(filePath, 'rb')
    data = json.load(f)
    f.close()
    return data


def getProjectRoot(*args):
    baseDir = os.path.dirname(__file__)
    path = os.path.join(baseDir, '..', '..', *args)
    path = os.path.abspath(path)
    return path


def getConfigPath(*args):
    return getProjectRoot('config', *args)


def readConfig(path):
    assert os.path.isfile(path)
    data = __readData(path)
    return data
