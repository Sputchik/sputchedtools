from sputchedtools import *
import asyncio, random, aiohttp, httpx, os, shutil

async def aio_test():
	response = await aio.request(
		'https://example.com',
		toreturn = [
			val for val in dir(aiohttp.ClientResponse) if not val.startswith('_')
		],
		raise_exceptions = True
	)

	for data in ProgressBar(response, text = 'Processing aio data...'):
		...
		# print('\n', data if not isinstance(data, str) else data[:30], sep = '')

async def aiox_test():
	response = await aio.request(
		'https://example.com',
		toreturn = [
			val for val in dir(httpx.Response) if not val.startswith('_')
		],
		httpx = True,
		raise_exceptions = True
	)

	for data in ProgressBar(response, text = 'Processing httpx data...'):
		...
		# print('\n', data if not isinstance(data, str) else data[:30], sep = '')

def num_test():
	with Timer(f'num, {num.shorten(num_test_iters)}'):
		for i in range(num_test_iters):
			d = random.uniform(-100000, 100000)
			e = num.beautify(d, -1)
			print(d, e, num.unshorten(e), sep = ' - ')

def MC_Versions_test():
	mc = MC_Versions()
	versions = mc.release_versions
	with Timer('(Sorting)'): sorted_versions = mc.sort(versions)
	with Timer('(Range)'): print(mc.get_range(sorted_versions))
	print('Latest Minecraft version:', mc.latest)

def compress_test():
	for algo in algorithms:
		compress('__pycache__', algorithm = algo)
		compress('sputchedtools.py', algorithm = algo)
		print(f'`{algo}`: Compressed')

def decompress_test():
	for algo in algorithms:
		ar_folder = f'__pycache__.{algo}'
		de_folder = f'de.__pycache__.{algo}'
		ar_file = f'sputchedtools.py.{algo}'
		de_file = f'de.sputchedtools.py.{algo}'
		
		decompress(ar_folder, algorithm = algo, output = de_folder)
		decompress(ar_file, algorithm = algo, output = de_file)

		os.remove(ar_file)
		os.remove(ar_folder)
		try: shutil.rmtree(de_file); shutil.rmtree(de_folder)
		except: pass

		print(f'`{algo}`: Decompressed')

with Timer('Test completed?'):
	enhance_loop()
	loop = asyncio.new_event_loop()

	loop.run_until_complete(aio_test())
	loop.run_until_complete(aiox_test())
	print()

	num_test_iters = 100
	num_test()
	MC_Versions_test()
	compress_test()
	decompress_test()