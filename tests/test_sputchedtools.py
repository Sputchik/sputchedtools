import pytest
from sputchedtools import *
import asyncio
import aiohttp
import random
import os
import shutil

async def aio_test(**kwargs):
	response = await aio.get(
		url,
		**kwargs
	)

	for data in ProgressBar(response, text = 'Processing response data...'):
		...
		# print('\n', data if not isinstance(data, str) else data[:30], sep = '')

def num_test():
	with Timer():
		for i in range(num_test_iters):
			d = random.uniform(-100000, 100000)
			e = num.beautify(d, -1)
			print(d, e, num.unshorten(e), sep = ' - ')

def MC_Versions_test():
	mc = MC_Versions()
	versions = mc.release_versions
	with Timer('MC Sorting: %ms'): sorted_versions = mc.sort(versions)
	with Timer('MC Range: %ms'): print(mc.get_range(sorted_versions))
	print('Latest Minecraft version:', mc.latest)

def compress_test():
	files = (_compress_file, compress_folder)

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

def decompress_test():
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

def anim_test():
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

with Timer() as t:
	enhance_loop()

	url = 'https://cloudflare-quic.com/'
	asyncio.run(aio_test(toreturn = [k for k in dir(aiohttp.ClientResponse) if not k.startswith('_')], httpx = True))
	# asyncio.run(aio_test(toreturn = [k for k in dir(httpx.Response) if not k.startswith('_')], httpx = True))
	# asyncio.run(aio_test(toreturn = [k for k in dir(niquests.AsyncResponse) if not k.startswith('_')], niquests = True))

	num_test_iters = 15
	with NewLiner(): num_test()
	MC_Versions_test()

	_compress_file = 'sputchedtools.py'
	compress_folder = '__pycache__'
	num.suffixes = num.fileSize_suffixes

	compress_test()
	decompress_test()

	sl = 0.001
	start, end = 20, 100
	anim_test()