# from Cython.Build import cythonize
from setuptools import setup
# import os

# is_cythonized = os.environ.get('CYTHONIZE') == '1'
# ext_modules = []
py_modules = ['sptz', 'sputchedtools']

# if is_cythonized:
# 	compiler_directives = {'language_level': 3}
# 	ext_modules = cythonize('src/sputchedtools.py', compiler_directives=compiler_directives)
# 	open('MANIFEST.in', 'w').write('exclude *.c')
# else:
# 	py_modules.append('sputchedtools')

setup(
	py_modules = py_modules,
	# ext_modules = ext_modules,
	package_dir = {'': 'src'},
	# has_ext_modules = lambda: bool(ext_modules)
)