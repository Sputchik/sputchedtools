from setuptools import setup, find_packages
from Cython.Build import cythonize
import os

is_cythonized = os.environ.get('CYTHONIZE') == '1'
if is_cythonized:
    open('MANIFEST.in', 'w').write('exclude *.c')
    ext_modules = cythonize([
        'sputchedtools/core.py',
        'sputchedtools/modules/*.py'
    ], compiler_directives={
        'language_level': '3',
        'annotation_typing': True,
        'embedsignature': True,
    })
else:
    ext_modules = []

setup(
    packages=find_packages(),
    py_modules=['sptz'],
    ext_modules=ext_modules,
    has_ext_modules=lambda: is_cythonized,
    package_data={
        'sputchedtools': ['*.pyi', 'modules/*.pyi']
    }
)