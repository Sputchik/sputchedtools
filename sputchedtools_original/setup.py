from setuptools import setup, Extension
from Cython.Build import cythonize
import os

is_cythonized = os.environ.get('CYTHONIZE') == '1'

# Define C extension
num_module = Extension(
    'sputchedtools.num_c',
    sources=['src/num.c'],
    include_dirs=['.'],
    extra_compile_args=['-O3']  # Optimize for performance
)

if is_cythonized:
    compiler_directives = {'language_level': 3}
    cython_extensions = cythonize('src/sputchedtools.py', compiler_directives=compiler_directives)
    all_extensions = cython_extensions + [num_module]
    
    open('MANIFEST.in', 'w').write('exclude *.c')
    py_modules = ['sptz']
else:
    all_extensions = [num_module]
    py_modules = ['sputchedtools', 'sptz']

setup(
    py_modules=py_modules,
    ext_modules=all_extensions,
    has_ext_modules=lambda: True,
    package_dir={'': 'src'}
)