from sputchedtools import *
import asyncio, random, aiohttp, httpx

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

with Timer('Test completed?'):
	enhance_loop()
	loop = asyncio.new_event_loop()

	loop.run_until_complete(aio_test())
	loop.run_until_complete(aiox_test())
	print()

	num_test_iters = 100
	num_test()
	MC_Versions_test()