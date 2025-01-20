from setuptools import setup
from Cython.Build import cythonize
import os

is_cythonized = os.environ.get('CYTHONIZE') == '1'

if is_cythonized:
    compiler_directives = {'language_level': 3}
    cython_extensions = cythonize('src/sputchedtools.py', compiler_directives = compiler_directives)
    open('MANIFEST.in', 'w').write('exclude *.c')
    py_modules = ['sptz']

else:
    cython_extensions = []
    py_modules = ['sputchedtools', 'sptz']

setup(
    py_modules = py_modules,
    ext_modules = cython_extensions,
    has_ext_modules = lambda: True,
    package_dir = {'': 'src'}
)