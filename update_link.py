from src.sputchedtools import __version__
import re

def update_pyproject_dependency(version):
	with open('sptz/pyproject.toml', 'r') as f:
		content = f.read()
	
	# Update the dependencies line
	content = re.sub(
		r'dependencies = \["sputchedtools[^"]*"\]',
		f'dependencies = ["sputchedtools>={version}"]',
		content
	)
	content = re.sub(
		r'version = ".*"',
		f'version = "{version}"',
		content
	)
	
	with open('sptz/pyproject.toml', 'w') as f:
		f.write(content)

if __name__ == '__main__':
	update_pyproject_dependency(__version__)