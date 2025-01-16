from setuptools import setup, Extension
from Cython.Build import cythonize

import os
import sys

is_cythonized = os.environ.get('CYTHONIZE') == '1'

if is_cythonized:
    compiler_directives = {'language_level': 3}
    ext_modules = cythonize('src/sputchedtools.py')
    
    open('MANIFEST.in', 'w').write('exclude *.c')
    py_modules = ['sptz']

else:
    ext_modules = []
    py_modules = ['sputchedtools', 'sptz']

setup(
    py_modules=py_modules,
    ext_modules=ext_modules,
    has_ext_modules=lambda: is_cythonized,
    package_dir={'': 'src'}
)