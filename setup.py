from setuptools import setup, find_packages

setup(
	name = 'sputchedtools',
	version = '0.10.0',
	packages = find_packages(),
	install_requires = [
		'aiohttp>=3.10.6',
		'aiofiles>=24.1.0',
		# uvloop / winloop
	],
)