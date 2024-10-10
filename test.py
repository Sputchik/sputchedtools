from sputchedtools import *

with Timer('Test completed?', 4):
	import asyncio
	enhance_loop()

	response = asyncio.run(aio.request('https://duckduckgo.com/123', 'ok+url+status', ssl = False, handle_status=True))

	print(response)

	with Timer('calcs', 4):
		print(num.shorten(4309.389, 2), num.unshorten('56b', True), num.decim_round(2.124002567, 6))

	print(num.beautify(4349.567, 3))

headers = ['Name', 'Age', 'City']
data = [
		['John', 25, 'New York'],
		['Alice', 30, 'London'],
		['Bob', 35, 'Petrosyan'],  # This row will be skipped due to mismatching length
		['Sarah', 28, 'Paris'],
		['David', 32, 'Sydney']
]

prints.tabled(data, headers, max_str_len_per_row=30, separate_rows=True)