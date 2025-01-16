import tarfile
import os
import io
from ..core import get_content, write_content

from typing import Literal, Union, Optional, IO

Algorithms = Literal['gzip', 'bzip2', 'lzma', 'lzma2', 'deflate', 'lz4', 'zstd', 'brotli']
algorithms = ['gzip', 'bzip2', 'lzma', 'lzma2', 'deflate', 'lz4', 'zstd', 'brotli']

__all__ = ['Algorithms', 'algorithms', 'make_tar', 'compress', 'decompress']

def is_brotli(data: bytes) -> bool:
	'''
	Don't use this
	'''

	if not isinstance(data, bytes):
		return False

	if len(data) < 4:
		return False

	first_byte = data[0]

	wbits = first_byte & 0x0F
	header_bits = (first_byte >> 4) & 0x0F

	if 10 >= wbits >= 24:
		return False

	if header_bits > 0x0D:
		return False

	return True

compress_map = {
	'gzip': (lambda: __import__('gzip').compress, {}, {'compression_level': 'compresslevel'}),
	'bzip2': (lambda: __import__('bz2').compress, {}, {'compression_level': 'compresslevel'}),
	'lzma': (lambda: __import__('lzma').compress, {}, {'compression_level': 'preset'}),
	'lzma2': (lambda: __import__('lzma').compress, lambda: {'format': __import__('lzma').FORMAT_XZ}, {'compression_level': 'preset'}),
	'deflate': (lambda: __import__('zlib').compress, {}, {'compression_level': 'level'}),
	'lz4': (lambda: __import__('lz4.frame').frame.compress, {}, {'compression_level': 'compression_level'}),
	'zstd': (lambda: __import__('zstandard').compress, {}, {'compression_level': 'level'}),
	'brotli': (lambda: __import__('brotli').compress, lambda: {'mode': __import__('brotli').MODE_GENERIC}, {'compression_level': 'quality'}),
}

decompress_map = {
	'gzip': (lambda: __import__('gzip').decompress, b'\x1f\x8b\x08'),
	'bzip2': (lambda: __import__('bz2').decompress, b'BZh'),
	'lzma': (lambda: __import__('lzma').decompress, b'\xfd7zXZ'),
	'deflate': (lambda: __import__('zlib').decompress, b'x'),
	'lz4': (lambda: __import__('lz4.frame').frame.decompress, b'\x04\x22\x4d\x18'),
	'zstd': (lambda: __import__('zstandard').decompress, b'\x28\xb5\x2f\xfd'),
	'brotli': (lambda: __import__('brotli').decompress, is_brotli),
}

def make_tar(
	source: str,
	output: str,
	ignore_errors: Union[type, tuple[type]] = PermissionError,
	in_memory: bool = False
) -> Union[str, bytes]:

	if in_memory:
		stream = io.BytesIO()

	with tarfile.open(
		output, "w",
		fileobj = None if not in_memory else stream
	) as tar:

		if os.path.isfile(source):
			tar.add(source, arcname = os.path.basename(source))

		else:
			for root, _, files in os.walk(source):
				for file in files:

					file_path = os.path.join(root, file)
					file_rel_path = os.path.relpath(file_path, source)

					try:
						with open(file_path, 'rb') as file_buffer:
							file_buffer.peek()

							info = tar.gettarinfo(arcname=file_rel_path, fileobj=file_buffer)
							tar.addfile(info, file_buffer)

					except ignore_errors:
						continue

	if in_memory:
		stream.seek(0)
		return stream.read()

	return output

def compress(
	source: Union[bytes, str, IO[bytes]],
	algorithm: Algorithms = 'gzip',
	output: Union[Literal[False], str, IO[bytes]] = None,
	ignored_exceptions: Union[type, tuple[type]] = (PermissionError, OSError),
	tar_in_memory: bool = True,
	tar_if_file: bool = False,
	compression_level: Optional[int] = None,
	check_algorithm_support: bool = False,
	**kwargs
) -> Union[int, bytes]:

	

	a_compress, additional_args, slug_map = compress_map[algorithm]

	if check_algorithm_support:
		if not algorithm: return

		try:
			a_compress()
			return True

		except:# ImportError
			return False

	a_compress = a_compress()

	if callable(additional_args):
		additional_args = additional_args()

	if compression_level:
		compression_slug = slug_map.get('compression_level')

		if compression_slug:
			additional_args[compression_slug] = compression_level

	additional_args.update(kwargs)

	is_out_buffer = hasattr(output, 'write')
	tar_in_memory = is_out_buffer or tar_in_memory

	if not output:
		if isinstance(source, str) and os.path.exists(source):
			output = os.path.basename(os.path.abspath(source)) + f'.{algorithm}'
		else:
			output = False

	if isinstance(source, bytes):
		compressed = a_compress(
			source, **additional_args
		)

	else:
		if not tar_if_file and os.path.isfile(source):
			with open(source, 'rb') as f:
				compressed = a_compress(f.read(), **additional_args)

		else:
			tar_path = '' if tar_in_memory else output + '.tar'
			if isinstance(output, str) and os.path.exists(output):
				os.remove(output)

			stream = make_tar(source, tar_path, ignored_exceptions, tar_in_memory)
			compressed = a_compress(stream if tar_in_memory else tar_path, **additional_args)

			if not tar_in_memory:
				os.remove(tar_path)

	return write_content(compressed, output)

def decompress(
	source: Union[bytes, str, IO[bytes]],
	algorithm: Optional[Algorithms] = None,
	output: Optional[Union[Literal[False], str, IO[bytes]]] = None,
	**kwargs
) -> Union[int, str, bytes]:

	type, content = get_content(source)

	if not algorithm:
		for algo, (a_decompress, start_bytes) in decompress_map.items():
			if callable(start_bytes):
				algorithm = algo if start_bytes(content) else None

			elif content.startswith(start_bytes):
				algorithm = algo
				break

		if not algorithm:
			raise ValueError(f"Couldn't detect algorithm for decompression, start bytes: {content[:10]}")

	a_decompress = compress_map[algorithm][0]()
	decompressed = a_decompress(content, **kwargs)

	if output is None:
		output = source.rsplit('.', 1)[0] if isinstance(source, str) else False

	if output is False:
		return decompressed

	elif hasattr(output, 'write'):
		return output.write(decompressed)

	# Assuming output is a path
	stream = io.BytesIO(decompressed)

	if tarfile.is_tarfile(stream):
		tarfile.open(fileobj=stream).extractall(output, filter = 'data')

	else:
		with open(output, 'wb') as f:
			f.write(decompressed)

	return output