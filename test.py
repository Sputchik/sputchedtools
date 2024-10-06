from sputchedtools import *

with Timer('Test completed?', 4):
	import asyncio
	enhance_loop()

	print(asyncio.run(aio.request('https://example.com')))

	with Timer('calcs', 4):
		print(num.shorten(4309.389, 2), num.unshorten('56b', True), num.decim_round(2.124002567, 6))

	print(num.beautify(4349.567, 3))