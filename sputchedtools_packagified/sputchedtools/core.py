from typing import Literal, Union, Optional, IO

__all__ = ['enhance_loop', 'get_content', 'write_content']

# ----------------METHODS----------------

def enhance_loop() -> bool:
	from sys import platform
	import asyncio

	try:

		if 'win' in platform:
			import winloop # type: ignore
			asyncio.set_event_loop_policy(winloop.EventLoopPolicy())

		else:
			import uvloop # type: ignore
			asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

		return True

	except ImportError:
		return False

def get_content(source: Union[str, bytes, IO[bytes]]) -> tuple[Optional[int], Optional[bytes]]:

	"""
	Returns source byte content
	Source can be either a file_path, readable buffer or just bytes

	First tuple object is source type:
		1 - bytes
		2 - readable buffer
		3 - file path
		4 - folder path (str)
		None - unknown
		...

	"""

	if isinstance(source, bytes):
		return 1, source

	elif hasattr(source, 'read'):
		return 2, source.read()

	else:
		import os

		if os.path.isfile(source):
			return 3, open(source, 'rb').read()

		elif os.path.isdir(source):
			return 4, source

		return None, None

def write_content(content: Union[str, bytes], output: Union[Literal[False], str, IO[bytes]]) -> Union[int, bytes]:
	_, content = get_content(content)

	if hasattr(output, 'write'):
		return output.write(content)

	elif output is False:
		return content

	else:
		with open(output, 'wb') as f:
			return f.write(content)