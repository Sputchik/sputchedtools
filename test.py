from sputchedtools import *
import asyncio, random, aiohttp

async def aio_test():
	response = await aio.request(
		'https://example.com',
		toreturn = [
			val for val in dir(aiohttp.ClientResponse) if not val.startswith('_')
		]
	)

	for data in ProgressBar(response, text = 'Processing aio data...'):
		...
		# print('\n', data if not isinstance(data, str) else data[:30], sep = '')

def num_test():
	iters = 15
	with Timer(f'num, {num.shorten(iters)}'):
		for i in range(iters):
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
	num_test()
	MC_Versions_test()