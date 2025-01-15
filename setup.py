from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import os

readme = open('README.md', 'r', encoding='utf-8').read()

# Check if we should Cythonize
is_cythonized = os.environ.get('CYTHONIZE') == '1'
if is_cythonized: open('MANIFEST.in', 'w').write('exclude sputchedtools.c')

ext_modules = cythonize('sputchedtools.py') if is_cythonized else []
py_modules = ['sptz'] if is_cythonized else ['sputchedtools', 'sptz']

setup(
	name='sputchedtools',
	version='0.30.0pre1',
	packages=find_packages(),
	py_modules=py_modules,
	install_requires=[
		'aiohttp>=3.11.11',
		'aiofiles>=24.1.0',
	],
	ext_modules=ext_modules,
	author='Sputchik',
	author_email='sputchik@gmail.com',
	url='https://github.com/Sputchik/sputchedtools',
	long_description=readme,
	long_description_content_type='text/markdown',
	python_requires='>=3.8',
)