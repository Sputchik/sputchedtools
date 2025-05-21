import pytest
import asyncio
import aiohttp
import random
import os
import shutil

from src.sputchedtools import *
enhance_loop()

url = 'https://cloudflare-quic.com/'
num_test_iters = 15
_compress_file = 'sputchedtools.py'
compress_folder = '__pycache__'
num.suffixes = num.fileSize_suffixes
sl = 0.003
start, end = 20, 80

@pytest.mark.asyncio
async def test_aio(**kwargs):
	response = await aio.get(
		url,
		toreturn = 'response',
		**kwargs
	)

	attrs = [attr for attr in dir(response) if not attr.startswith('_')]
	attrs.sort()
	for data in ProgressBar(attrs, text = 'Processing response data...'):
		...
		# print('\n', data if not isinstance(data, str) else data[:30], sep = '')

	literals = ', '.join(f"'{attr}'" for attr in attrs)
	print(f'ReturnTypes = Literal[{literals}]')

def test_num():
	num.suffixes = ['', 'K', 'M', 'B', 'T', 1000]

	with NewLiner(), Timer():
		for i in range(num_test_iters):
			d = random.randint(-100000, 100000)
			e = num.beautify(d, -1)
			print(d, e, num.unshorten(e), sep = ' | ')

@pytest.mark.asyncio
async def test_MC_Versions():
	mc = await MC_Versions.init()
	versions = mc.release_versions
	with Timer('MC Sorting: %ms'): sorted_versions = mc.sort(versions)
	with Timer('MC Range: %ms'): print(mc.get_range(sorted_versions))
	print('Latest Minecraft version:', mc.latest)

def test_compress():
	files = (_compress_file, compress_folder)
	num.suffixes = num.fileSize_suffixes

	with NewLiner():
		for file in files:
			for algo in algorithms:
				out = os.path.basename(file) + f'.{algo}'

				with Timer(False) as t:
					compress(file, algorithm = algo, output = out, compression_level=1)

				diff = t.diff * 1000
				size = os.path.getsize(out)
				formatted_size = num.shorten(size)

				print(f'{algo}: Compressed {file}: {formatted_size}, {diff:.2f}ms')

def test_decompress():
	files = (_compress_file, compress_folder)

	with NewLiner():
		for file in files:
			for algo in algorithms:
				source = file + f'.{algo}'
				out = 'de-' + source

				if os.path.exists(out):
					shutil.rmtree(out)

				with Timer(False) as t:
					decompress(source, output = out)

				diff = t.diff * 1000
				print(f'{algo}: Decompressed {source}, {diff:.2f}ms')
				os.remove(source)

				if os.path.isfile(out):
					os.remove(out)

				else:
					try: shutil.rmtree(out)
					except: pass

def test_anim():
	import time

	with Anim('Loading ', clear_on_exit = True) as anim:
		for i in (True, False):
			for _ in range(start, end):
				time.sleep(sl)
				anim.set_text('Loading' + '.' * _ + ' ', i)

			for _ in range(end, 3, -1):
				time.sleep(sl)
				anim.set_text('Loading' + '.' * _ + ' ', i)

		for _ in range(start, end):
			time.sleep(sl)
			anim.set_text('Loading' + '.' * _ + ' ')
			anim.set_text(' Loading' + '.' * _ + ' ', False)

		for _ in range(end, 3, -1):
			time.sleep(sl)
			anim.set_text('Loading' + '.' * _ + ' ')
			anim.set_text(' Loading' + '.' * _ + ' ', False)

		anim.set_text(' Done! ', False)

	print('Was there text before????')

def test_page_comp():
	i1 = {
		'jpg': [1]
	}
	i2 = {
		'jpg': list(range(1, 13, 2)), # 1 - 11
		'png': list(range(2, 13, 2)), # 2 - 12
		'gif': list(range(10, 151)) # 10 - 150
	}

	ci1 = compress_images(i1)
	ci2 = compress_images(i2, repetitive = True)

	di1 = decompress_images(ci1)
	di2 = decompress_images(ci2)
	assert di1 == i1, 'Failed to compress single extension!'
	assert i2.keys() == di2.keys() and all(i2[k] == di2[k] for k in i2.keys()), f'Decompressed images do not match original images!\nCompressed: {ci2}\nDecompressed: {di2}'
	print('\nImage compression and decompression test passed\n')

if __name__ == '__main__':
	test_num()
	test_compress()
	test_decompress()
	test_page_comp()
	test_anim()

	asyncio.run(test_MC_Versions())
	asyncio.run(test_aio())