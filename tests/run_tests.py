"""
Sets up and runs tests for the 'assetQC' API.

To be run with:
$ env ASSETQC_CONFIG_PATH='/home/davidc/dev/mayaScripts/trunk/assetQC/test/config/config_linux.json' python runTests.py
"""

import os
import sys

# Ensure that '<root>/python' and '<root>/tests' is on the PYTHONPATH
path = os.path.dirname(__file__)
test_path = os.path.abspath(os.path.join(path, '.'))
package_path = os.path.abspath(os.path.join(path, '..', 'python'))
sys.path.insert(0, test_path)
sys.path.insert(0, package_path)
print 'test_path', test_path
print 'package_path', package_path


if __name__ == '__main__':
    import coverage
    import nose

    cov = None
    ver = str(coverage.__version__).split('.')
    msg = 'version:' + repr(ver)
    print msg
    if int(ver[0]) == 3:
        cov = coverage.coverage()
        cov.exclude('*python*site-packages*')
    elif int(ver[0]) >= 4:
        cov = coverage.Coverage(omit='*test*')
    else:
        pass
    cov.erase()
    cov.start()

    nose.core.run()

    cov.stop()
    cov.save()
    cov.report()
    cov.html_report()

