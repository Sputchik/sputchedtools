from sputchedtools import Timer, aio, enhance_loop, num

with Timer('Test completed?', 4):
	import asyncio
	enhance_loop()

	print(asyncio.run(aio.request('https://example.com')))

	print(num.shorten(34523453.5242240013, 3), num.unshorten('52352.32k'), num.decim_round(2.124002148, 6))
