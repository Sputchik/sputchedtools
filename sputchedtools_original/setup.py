from setuptools import setup, Extension
from Cython.Build import cythonize

import os
import sys

is_cythonized = os.environ.get('CYTHONIZE') == '1'
if is_cythonized:
    compiler_directives = {
        # Language and type handling
        'language_level': 3,
        'infer_types': True,        # Enable type inference for better performance
        'annotation_typing': False,  # Disable since you use runtime typing
        
        # Performance optimizations
        'boundscheck': False,       # Safe for your list operations
        'wraparound': True,         # Keep True as you use negative indexing in num class
        'initializedcheck': False,  # Safe as you handle None checks explicitly
        'cdivision': True,         # Safe for your numeric operations
        
        # Method call optimizations
        'optimize.use_switch': True,
        'optimize.unpack_method_calls': True,
        
        # String handling
        'c_string_type': 'str',    # You work with Python strings mostly
        'c_string_encoding': 'utf8',
        
        # Debug/Build options
        'embedsignature': False,
        'profile': False,
        'linetrace': False,
    }
    
    ext_modules = cythonize(
        'src/sputchedtools.py',
        nthreads=4,
        quiet=True,
        compiler_directives=compiler_directives,
        annotate=False,
    )
    
    # Platform-specific optimizations
    for e in ext_modules:
        if sys.platform == 'win32':
            e.extra_compile_args = ['/O2', '/arch:AVX2']
        else:
            e.extra_compile_args = ['-O3', '-march=native']

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