from setuptools import setup, find_packages

readme = open('README.md', 'r').read()

setup(
	name = 'sputchedtools',
	version = '0.25.10',
	packages = find_packages(),
	py_modules = ['sputchedtools', 'sptz'],
	install_requires = [
		'aiohttp>=3.11.11',
		'httpx[http2]>=0.28.1',
		'aiofiles>=24.1.0',
		# uvloop/winloop
	],
	author = 'Sputchik',
	author_email = 'sputchik@gmail.com',
	url = 'https://github.com/Sputchik/sputchedtools',
	long_description=readme,
	long_description_content_type='text/markdown',
	python_requires = '>=3.8',
)