import sys

from pkg_resources import VersionConflict, require
from setuptools import setup

try:
    require('setuptools>=66.0')
except VersionConflict:
    print('Error: version of setuptools is too old (<66.0)!')
    sys.exit(1)

if __name__ == '__main__':
    setup(use_pyscaffold=True)
