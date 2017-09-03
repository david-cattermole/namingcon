"""
Base class for test cases.
"""

import os
import shutil
import unittest


class BaseCase(unittest.TestCase):
    def setUp(self):
        root = self.rootPath()
        if not os.path.isdir(root):
            os.makedirs(root)
        return

    def tearDown(self):
        root = self.rootPath()
        if os.path.isdir(root):
            shutil.rmtree(root)
        return

    def rootPath(self):
        path = '/tmp/namingcon'
        if os.name == 'nt':
            path = 'C:\\tmp\\namingcon'
        return os.path.abspath(path)

    
