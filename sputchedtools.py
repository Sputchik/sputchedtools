class Timer:

	"""

	Code execution Timer, use 'with' keyword

	Accepts:
		txt = '': text after main print message
		decimals = 2: time difference precission

	"""

	def __init__(self, txt = '', decimals = 2):
		from time import time
		self.time = time
		self.txt = txt
		self.decimals = decimals

	def __enter__(self):
		self.was = self.time()

	def __exit__(self, f, u, c):
		self.diff = format((self.time() - self.was), f'.{self.decimals}f')
		print(f'\nTaken time: {self.diff}s {self.txt}')

class prints:

	@staticmethod
	def dashed(text: str, start_newlines: int = 1, end_newlines: int = 1, dash_length: int = 44, print_text: bool = True, return_text: bool = False) -> None:
		#if not isinstance(text, str) or not isinstance(start_newlines, int) or not isinstance(end_newlines, int) or not isinstance(dash_length, int):
		#  return None
		
		text_len = len(text)

		if text_len > dash_length:
			print(text)
			return

		dashes = '-' * ( (dash_length - text_len) // 2 )
		final_text = '\n' * start_newlines + dashes + text + dashes + '\n' * end_newlines

		if print_text: print(final_text)
		if return_text: return final_text
	
	@staticmethod
	def tabled(data, headers, max_str_len_per_row=40, separate_rows=False):
	
		# Filter data to include only rows with length matching headers
		filtered_data = [row for row in data if len(row) == len(headers)]
		
		# Determine the maximum width for each column
		column_widths = {header: len(header) for header in headers}

		for row in filtered_data:
			for header, value in zip(headers, row):
				
				str_value = str(value)
				
				if len(str_value) > max_str_len_per_row:
					column_widths[header] = max(column_widths[header], max_str_len_per_row)
				
				else:
					column_widths[header] = max(column_widths[header], len(str_value))
					
		# Create a horizontal separator
		separator = '+-' + '-+-'.join('-' * column_widths[header] for header in headers) + '-+'
		
		# Print the header
		header_row = '| ' + ' | '.join(header.ljust(column_widths[header]) for header in headers) + ' |'
		
		print(separator)
		print(header_row)
		print(separator)
		
		# Print the table rows
		for row_index, row in enumerate(filtered_data):
			
			# Check if any value exceeds the max_str_len_per_row
			extended_rows = []
			
			for header, value in zip(headers, row):
				
				str_value = str(value)
				
				if len(str_value) > max_str_len_per_row:
					# Break the string into chunks
					chunks = [str_value[i:i+max_str_len_per_row] for i in range(0, len(str_value), max_str_len_per_row)]
					
					extended_rows.append(chunks)
				
				else:
					extended_rows.append([str_value])
					
			# Determine the maximum number of lines required for the current row
			max_lines = max(len(chunks) for chunks in extended_rows)
			
			# Print each line of the row
			for line_index in range(max_lines):
				row_str = '| ' + ' | '.join(
				(extended_rows[i][line_index] if line_index < len(extended_rows[i]) else '').ljust(column_widths[header])
				for i, header in enumerate(headers)
				) + ' |'
				
				print(row_str)
				
			# Print a separator between rows if separate_rows is True
			if separate_rows and row_index < len(filtered_data) - 1:
				
				print(separator)
				
		# Print the bottom border
		print(separator)

class aio:
	"""
	Methods:
		aio.request() - aiohttp.ClientSession.get() request
		aio.post() - aiohttp.ClientSession.post() request
		aio.open() - aiofiles.open() method
		aio.sem_task() - uses received semaphore to return function execution result

	"""

	@staticmethod
	async def request(
		url: str,
		toreturn: str = 'text',
		session = None,
		**kwargs,

		) -> tuple:

		"""
		Accepts:
			Args:
				url
			Kwargs:
				toreturn: read, text, json
				session: aiohttp.ClientSession
				any other session.get() argument

		Returns:
			Valid response: (data, response.status)
			status == 403: (-2, status)
			status == 521: (-1, status)
			status not in range(200, 400): (None, status)

			Request Timeout: (0, None)
			Cancelled Error: (None, None)
			Exception: (-3, Exception as e)

		"""

		import aiohttp, asyncio
		created_session = False
		if session is None:
			session = aiohttp.ClientSession()
			created_session = True

		try:
			async with session.get(url, **kwargs) as response:

				status = response.status

				if 200 <= response.status < 300 and str(response.url)[-5:] !=  '/404/':

					if toreturn == 'text':
						data = await response.text()
					elif toreturn == 'read':
						data = await response.read()
					elif toreturn == 'json':
						data = await response.json()
					else:
						data = None

					return data, status

				elif status == 403:
					# print('\nToo many requests...')
					return -2, status

				elif status == 521:
					return -1, status

				else: return None, status

		except asyncio.TimeoutError:
			return 0, None

		except asyncio.CancelledError:
			return None, None

		except Exception as e:
			# print(f'\nFailed to get response from {url}')
			return -3, e

		finally:
			if created_session is True:
				await session.close()

	@staticmethod
	async def post(url, toreturn = 'json', session = None, **kwargs) -> tuple:

		"""
		Accepts:
			Args:
				url
			Kwargs:
				toreturn: read, text, json
				session: aiohttp.ClientSession
				any other session.get() argument

		Returns:
			Valid response: (data, response.status)
			status not in range(200, 400): (None, status)

			Request Timeout: (0, None)
			Cancelled Error: (None, None)
			Exception: (-3, Exception as e)

		"""

		import aiohttp, asyncio
		created_session = False
		if session is None:
			session = aiohttp.ClientSession()
			created_session = True

		try:

			async with session.post(url, **kwargs) as response:
				status = response.status

				if 200 <= status < 300 and str(response.url)[-5:] !=  '/404/':

					if toreturn == 'text':
						data = await response.text()
					elif toreturn == 'read':
						data = await response.read()
					elif toreturn == 'json':
						data = await response.json()
					else:
						data = None

					return data, status

				else:
					return None, status

		except asyncio.TimeoutError:
			return 0, None

		except asyncio.CancelledError:
			return None, None

		except Exception as e:
			# print(f'\nFailed to get response from {url}')
			return -3, e

		finally:
			if created_session is True:
				await session.close()

	@staticmethod
	async def open(file: str, action: str = 'read', mode: str = 'r', content = None, **kwargs):
		"""
		Accepts:
			Args:
				file: str:. file path
				action: str = 'read' | 'write': read/write file content
				mode: str = 'r': aiofiles.open() mode

			Kwargs:
				content = None: content that will be used for file write action
				**kwargs: other arguments added to aiofiles.open() method

		Returns:
			mode = 'read': file content
			mode = 'write': content write to file status

		"""

		import aiofiles

		async with aiofiles.open(file, mode, **kwargs) as f:

			if action == 'read': return await f.read()

			elif action == 'write': return await f.write(content)

			else: return None

	@staticmethod
	async def sem_task(
		semaphore,
		func: callable,
		*args, **kwargs
		):

		async with semaphore:
			return await func(*args, **kwargs)

def enhance_loop():
	from sys import platform
	import asyncio
	
	try:

		if 'win' in platform:
			import winloop # type: ignore
			winloop.install()

		else:
			import uvloop # type: ignore
			asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

		return True

	except ImportError:
		return False

class num:
	"""
	Methods:
		num.shorten() - Shortens float | int value, using expandable / editable num.suffixes dictionary
			Example: num.shorten(10_000_000, 0) -> '10m'

		num.unshorten() - Unshortens str, using expandable / editable num.multipliers dictionary
			Example: num.unshorten('1.63k', round = False) -> 1630.0

		num.decim_round() - Safely rounds decimals in float
			Example: num.decim_round(2.000127493, 2) -> '2.00013'

		num.beautify() - returns decimal-rounded, shortened float-like string
			Example: num.beautify(4349.567, 3) -> 4.35k

	"""

	suffixes: list[str] = ['', 'k', 'm', 'b', 't']
	multipliers: dict[str, int] = {'k': 10**3, 'm': 10**6, 'b': 10**9, 't': 10**12}

	@staticmethod
	def shorten(value: int | float, decimals: int = 2) -> str:
		"""
		Accepts:
			value: str: int-like value with shortener at the end: 'k', 'm', 'b', 't'
			decimals: int = 2: digit amount

		Returns:
			Accepted value:
				if not isinstance(float(value[:-1]), float)
				if value[-1] not in multipliers: 'k', 'm', 'b', 't'

			Shortened float or int-like str

		"""

		if not isinstance(value, (int, float)) or decimals < 0:
				return str(value)

		sign = '-' if value < 0 else ''
		value = abs(value)
		magnitude = 1000.0

		for i, suffix in enumerate(num.suffixes):
				unit = magnitude ** i
				if value < unit * magnitude or i == len(num.suffixes) - 1:
						value /= unit
						formatted = num.decim_round(value, decimals)
						return f"{sign}{formatted}{suffix}" # .rstrip('0').rstrip('.')

	@staticmethod
	def unshorten(value: str, round: bool = False, decimals: int = 2) -> float | int:
		"""
		Accepts:
			value: str: int-like value with shortener at the end: 'k', 'm', 'b', 't'
			round: bool = False | True: wether returned value should be rounded to integer

		Returns:
			Accepted value:
				if not isinstance(float(value[:-1]), float)
				if value[-1] not in multipliers: 'k', 'm', 'b', 't'

			Unshortened float or int

		"""

		if not isinstance(value, str) or not isinstance(decimals, int) or decimals < 0:
			return value

		mp = value[-1].lower()
		digit = value[:-1]

		try:
			digit = float(digit)
			mp = num.multipliers[mp]

			if round is True:
				unshortened = num.decim_round(digit * mp, decimals)

			else:
				unshortened = digit * mp

			return unshortened

		except (ValueError, KeyError):
			return value

	@staticmethod
	def decim_round(value: float, decimals: int = 2, precission: int = 20) -> str:
		"""
		Accepts:
			value: float: usually with medium-big decimal length
			decimals: int: determines amount of digits (+2 for rounding, after decimal point) that will be used in 'calculations'
			precission: int: determines precission level (format(value, f'.->{precission}<-f'

		Returns:
			Accepted value:
				if value == 0,
				not isinstance(value & (decimals, precission), float & int)
				decimals & value < 1

			float-like str

		"""

		if value == 0:
			return value
		elif not isinstance(decimals, int) or not isinstance(precission, int):
			return value
		elif decimals < 0 or precission < 0:
			return value

		str_val = format(value, f'.{precission}f')

		integer = str_val.split('.')[0]
		decim = str_val.split('.')[1]

		if integer != '0':
			i = 0

		else:
			for i in range(len(decim)):
				if decim[i] != '0': break

		decim = decim[i:i + decimals + 2].rstrip('0')

		if decim == '':
			return integer

		if len(decim) > decimals:
			round_part = decim[:decimals] + '.' + decim[decimals:]
			rounded = str(round(float(round_part))).rstrip('0')
			decim = '0' * i + rounded

		else: decim = '0' * i + str(decim)

		return integer + '.' + decim

	@staticmethod
	def beautify(value: int | float, decimals: int = 2, precission: int = 20):
		return num.shorten(float(num.decim_round(value, decimals, precission)), decimals)

class web3_misc:
	"""
	Methos: _gas, _gasPrice, nonce
	Declare web3_misc.web3 to be able to use them

	"""

	web3 = None
	gas = None
	gasPrice = None
	
	@staticmethod
	def _gas(period: float | int = 10) -> None:
		import time
		global gas

		while True:
			web3_misc.gas = web3_misc.web3.eth.gas_price
			time.sleep(period)

	@staticmethod
	def _gasPrice(tx: dict, period: float | int = 10) -> None:
		import time
		global gasPrice

		while True:
			web3_misc.gasPrice = web3_misc.web3.eth.estimate_gas(tx)
			time.sleep(period)

	@staticmethod
	def nonce(address: str) -> int:
		return web3_misc.web3.eth.get_transaction_count(address)