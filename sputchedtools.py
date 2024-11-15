from typing import Literal
from collections.abc import Iterator, Iterable

ReturnTypes = Literal['url', 'real_url', 'status', 'reason', 'encoding', 'history', 'text', 'read', 'json', 'raw', 'content_type', 'charset', 'headers', 'cookies', 'request_info', 'version', 'release', 'raise_for_status']

class Timer:

	"""

	Code execution Timer, use 'with' keyword

	Accepts (order doesn't matter from 0.16.2):
		txt: str = '': text after main print message
		decimals: int = 2: time difference precission

	"""

	def __init__(self, txt = '', decimals = 2):
		from time import perf_counter
		self.time = perf_counter

		if isinstance(txt, (int)):
			self.decimals = txt
			self.txt = decimals if isinstance(decimals, str) else ''

		else:
			self.decimals = decimals
			self.txt = txt

	def __enter__(self):
		self.was = self.time()

	def __exit__(self, f, u, c):
		self.diff = format((self.time() - self.was), f'.{self.decimals}f')
		print(f'\nTaken time: {self.diff}s {self.txt}')

class ProgressBar:
	def __init__(
		self,
		iterator: Iterator | Iterable,
		text: str = 'Processing...',
		task_amount: int = None,
		final_text: str = "Done"
	):

		if iterator and not isinstance(iterator, Iterator):
			if not hasattr(iterator, '__iter__'):
				raise AttributeError(f"Provided object is not Iterable\n\nType: {type(iterator)}\nAttrs: {dir(iterator)}")
			self.iterator = iterator.__iter__()

		else: self.iterator = iterator

		if task_amount is None:
			if not hasattr(iterator, '__len__'):
				raise AttributeError(f"You did not provide task amount for Iterator or object with no __len__ attribute\n\nType: {type(iterator)}\nAttrs: {dir(iterator)}")
			self._task_amount = iterator.__len__()

		else: self._task_amount = task_amount

		from sys import stdout
		self._text = text
		self._completed_tasks = 0
		self.final_text = final_text
		self.swrite = stdout.write
		self.sflush = stdout.flush

	@property
	def text(self):
		"""Get the overall task amount."""
		return self._text

	@text.setter
	def text(self, value: str):
		"""Safely change bar text."""
		val_len = len(value)
		text_len = len(self._text)
		self._text = value + ' ' * (text_len - val_len if text_len > val_len else 0)

	@property
	def task_amount(self):
		"""Get the overall task amount."""
		return self._task_amount

	@task_amount.setter
	def task_amount(self, value: int):
		"""Set the overall task amount."""
		self._task_amount = value

	@property
	def completed_tasks(self):
		"""Get the number of completed tasks."""
		return self._completed_tasks

	def __iter__(self):
		self.update(0)
		return self

	def __next__(self):
		try:
			item = next(self.iterator)
			self.update()
			return item

		except StopIteration:
			self.finish()
			raise

	def update(self, increment: int = 1):
		self._completed_tasks += increment
		self._print_progress()

	def _print_progress(self):
		self.swrite(f'\r{self._text} {self._completed_tasks}/{self._task_amount}')
		self.sflush()

	def finish(self):
		self.finish_message = f'\r{self._text} {self._completed_tasks}/{self._task_amount} {self.final_text}\n'
		self.swrite(self.finish_message)
		self.sflush()

class AsyncProgressBar:
	def __init__(
		self,
		text: str,
		task_amount: int = None,
		final_text: str = "Done",
		tasks = None
	):
		import asyncio
		from sys import stdout

		self.asyncio = asyncio
		self.swrite = stdout.write
		self.sflush = stdout.flush

		if task_amount is None and tasks:
			if not hasattr(tasks, '__len__'):
				raise AttributeError(f"You did not provide task amount for Async Iterator\n\nType: {type(tasks)}\nAttrs: {dir(tasks)}")
			else:
				self.task_amount = tasks.__len__()

		else: self.task_amount = task_amount

		self.text = text
		self.final_text = final_text
		self._completed_tasks = 0

		if tasks is not None:
			if hasattr(tasks, '__aiter__'):
				self.tasks = tasks
			else:
				raise ValueError("tasks must be an async iterator or None")

	async def _update(self, increment: int = 1):
		self._completed_tasks += increment
		self._print_progress()

	def _print_progress(self):
		self.swrite(f'\r{self.text} {self._completed_tasks}/{self.task_amount}')
		self.sflush()

	async def _finish(self):
		if self.task_amount is not None:
			self.finish_message = f'\r{self.text} {self._completed_tasks}/{self.task_amount} {self.final_text}\n'
		else:
			self.finish_message = f'\r{self.text} {self._completed_tasks} {self.final_text}\n'
		self.swrite(self.finish_message)
		self.sflush()
		self._completed_tasks = 0

	async def as_completed(self, tasks):
		for task in self.asyncio.as_completed(tasks):
			result = await task
			await self._update()
			yield result
		await self._finish()

	async def gather(self, tasks):
		results = []
		for task in self.asyncio.as_completed(tasks):
			result = await task
			await self._update()
			results.append(result)
		await self._finish()
		return results

	async def __aiter__(self):
		if not hasattr(self, 'tasks'):
			raise ValueError("AsyncProgressBar object was not initialized with an async iterator")

		async for task in self.tasks:
			await self._update()
			yield task
		await self._finish()

class prints:

	@staticmethod
	def dashed(text: str, start_newlines: int = 1, end_newlines: int = 1, width: int = 44, char = '-') -> None:
		print('\n' * start_newlines + text.center(width, char) + '\n' * end_newlines)

	@staticmethod
	def tabled(data, headers, max_str_len_per_row=40, separate_rows=False):

		filtered_data = [row for row in data if len(row) == len(headers)]

		column_widths = {header: len(header) for header in headers}

		for row in filtered_data:
			for header, value in zip(headers, row):

				str_value = str(value)

				if len(str_value) > max_str_len_per_row:
					column_widths[header] = max(column_widths[header], max_str_len_per_row)

				else:
					column_widths[header] = max(column_widths[header], len(str_value))

		separator = '+-' + '-+-'.join('-' * column_widths[header] for header in headers) + '-+'

		header_row = '| ' + ' | '.join(header.ljust(column_widths[header]) for header in headers) + ' |'

		print(separator)
		print(header_row)
		print(separator)

		for row_index, row in enumerate(filtered_data):
			extended_rows = []

			for header, value in zip(headers, row):

				str_value = str(value)

				if len(str_value) > max_str_len_per_row:
					chunks = [str_value[i:i+max_str_len_per_row] for i in range(0, len(str_value), max_str_len_per_row)]
					extended_rows.append(chunks)

				else:
					extended_rows.append([str_value])

			max_lines = max(len(chunks) for chunks in extended_rows)

			for line_index in range(max_lines):
				row_str = '| ' + ' | '.join(
				(extended_rows[i][line_index] if line_index < len(extended_rows[i]) else '').ljust(column_widths[header])
				for i, header in enumerate(headers)
				) + ' |'

				print(row_str)

			if separate_rows and row_index < len(filtered_data) - 1:

				print(separator)

		print(separator)

class aio:
	"""
	Methods:
		aio.request() - aiohttp.ClientSession.get() request
		aio.post() - aiohttp.ClientSession.post() request
		aio.open() - aiofiles.open() method
		aio.sem_task() - uses received semaphore to return function execution result

	"""

	data_map = {
		'url': lambda response: response.url,
		'real_url': lambda response: response.real_url,
		'status': lambda response: response.status,
		'reason': lambda response: response.reason,
		'encoding': lambda response: response.get_encoding(),
		'history': lambda response: response.history,

		'text': lambda response: response.text(),
		'read': lambda response: response.read(),
		'json': lambda response: response.json(),
		'raw': lambda response: response.content.read(),

		'content_type': lambda response: response.content_type,
		'charset': lambda response: response.charset,
		'headers': lambda response: response.headers,
		'cookies': lambda response: response.cookies,

		'request_info': lambda response: response.request_info,
		'version': lambda response: response.version,
		'release': lambda response: response.release(),
		'raise_for_status': lambda response: response.raise_for_status(),
	}
	response_status_map = {
		403: -2,
		521: -1,
	}

	@staticmethod
	async def _request(
		method: callable,
		url: str,
		toreturn: ReturnTypes = 'text',
		session = None,
		handle_status = True,
		**kwargs,

	):

		"""
		Accepts:

			Args:
				method: callable - aiohttp.ClientSession request method (get and post supported)
				url: str

			Kwargs:
				toreturn: ReturnTypes or any other ClientResponse full-path (for eval) attribute
				session
				handle_status: bool - Wether to insert corresponding status id to first index. Ensures compatibilty with old scripts
				any other session.get() argument

		Returns:
			Valid response: [data]

			if handle_status:
				status == 403: [-2] + toreturn
				status == 521: [-1] + toreturn

			status not in range(200, 400): [None] + toreturn

			Request Timeout: [0] + toreturn
			Cancelled Error: [None] + toreturn
			Exception: [-3] + toreturn

		"""

		import aiohttp, asyncio
		return_items = []
		ses = session or aiohttp.ClientSession()

		try:
			async with ses.request(method, url, **kwargs) as response:

				if handle_status and not response.ok:
					status = aio.response_status_map.get(response.status, None)
					return_items.append(status)

				for item in toreturn.split('+'):
					value = aio.data_map.get(item)

					try:
						if value is None:
							result = eval(f'response.{item}')
							if callable(result):
								result = result()
							elif asyncio.iscoroutinefunction(result):
								result = await result()
						else:
							result = value(response)
							if asyncio.iscoroutine(result):
								result = await result
					except:
						result = None

					return_items.append(result)

		except asyncio.TimeoutError:
			return_items.insert(0, 0)

		except asyncio.CancelledError:
			return_items.insert(0, None)

		except:
			return_items.insert(0, -3)

		finally:
			if not session: await ses.close()
			return return_items

	@staticmethod
	async def request(
		url: str,
		toreturn: ReturnTypes = 'text',
		session = None,
		handle_status: bool = True,
		**kwargs
	):
		return await aio._request('GET', url, toreturn, session, handle_status, **kwargs)

	@staticmethod
	async def post(
		url: str,
		toreturn: ReturnTypes = 'text',
		session = None,
		handle_status: bool = True,
		**kwargs
	):

		return await aio._request('POST', url, toreturn, session, handle_status, **kwargs)

	@staticmethod
	async def open(
		file: str,
		action: str = 'read',
		mode: str = 'r',
		content = None,
		**kwargs
	):
		"""
		Asynchronously read from or write to a file using aiofile.

		Args:
			file (str): File path
			action (str): Operation to perform ('read' or 'write')
			mode (str): File open mode ('r', 'w', 'rb', 'wb', etc.)
			content: Content to write (required for write operation)

		Kwargs:
			**kwargs: Additional arguments for aiofiles.open()

		Returns:
			- str|bytes: File content when action != 'write'
			- int: Number of bytes written when action = 'write'

		Raises:
			ValueError: If trying to write without content
		"""
		import aiofiles

		async with aiofiles.open(file, mode, **kwargs) as f:
			if action == 'write':
				return await f.write(content)
			else:
				return await f.read()

	@staticmethod
	async def sem_task(
		semaphore,
		func: callable,
		*args, **kwargs
	):
		async with semaphore: return await func(*args, **kwargs)

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

	suffixes: list[str] = ['', 'K', 'M', 'B', 'T', 1000]
	fileSize_suffixes: list[str] = [' B', ' KB', ' MB', ' GB', ' TB', 1024]
	multipliers: dict[str, int] = {'k': 10**3, 'm': 10**6, 'b': 10**9, 't': 10**12}
	decim_map: dict[callable, int] = {
		lambda x: x > 1000: 0,
		lambda x: x > 100: 1,
		lambda x: x > 10: 2,
		lambda x: x > 5: 3,
		lambda x: True: 4
	}

	@staticmethod
	def shorten(value: int | float, decimals: int = 2, suffixes = None) -> str:
		"""
		Accepts:
			value: int - big value
			decimals: int = 2: digit amount

		Returns:
			Shortened float or int-like str

		"""

		sign = '-' if value < 0 else ''
		value = abs(value)
		suffixes = suffixes or num.suffixes
		magnitude = suffixes[-1]

		for i, suffix in enumerate(suffixes[:-1]):
			unit = magnitude ** i
			if value < unit * magnitude or i == len(suffixes) - 1:
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
	def decim_round(value: float, decimals: int = 2, round_with_numbers_higher_1: bool = True, precission: int = 20) -> str:
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

		str_val = format(value, f'.{precission}f')

		integer = str_val.split('.')[0]
		decim = str_val.split('.')[1]

		if decimals == -1:
			for condition, decim_amount in num.decim_map.items():
				if condition(abs(value)):

					if decim_amount != 4:

						if round_with_numbers_higher_1:
							return str(round(value, decim_amount if decim_amount != 0 else None))

						else:
							decimals = decim_amount
							break

					else:
						decimals = 4
						break

		for i in range(len(decim)):
			if decim[i] != '0': break

		if integer != '0' and round_with_numbers_higher_1:
			return str(round(value, decimals if decimals != 0 else None))

		decim = decim[i:i + decimals + 2].rstrip('0')

		if decim == '':
			return integer

		if len(decim) > decimals:
			round_part = decim[:decimals] + '.' + decim[decimals:]
			rounded = str(round(float(round_part))).rstrip('0')
			decim = '0' * i + rounded

		else: decim = '0' * i + str(decim)

		return (integer + '.' + decim).rstrip('.')

	@staticmethod
	def beautify(value: int | float, decimals: int = 2, precission: int = 20):
		return num.shorten(float(num.decim_round(value, decimals, precission)), decimals)

class Web3Misc:
	"""
	A utility class for managing Ethereum-related tasks such as gas price, gas estimation, and nonce retrieval.

	Methods:
		- start_gas_monitor(period: float | int = 10) -> None
		- start_gas_price_monitor(tx: dict, period: float | int = 10) -> None
		- start_nonce_monitor(address: str, period: float | int = 10) -> None
		- get_nonce(address: str) -> int

	Properties:
		- gas: The current gas price.
		- gas_price: The estimated gas price for a transaction.
		- nonce: The current nonce for an address.

	Attributes:
		- web3: The Web3 instance to interact with the Ethereum network.
	"""

	def __init__(self, web3):
		"""
		Initializes the Web3Misc instance with a Web3 instance.

		:param web3: The Web3 instance to interact with the Ethereum network.
		:type web3: Web3
		"""
		self._web3 = web3
		self._gas = None
		self._gas_price = None
		self._nonce = None

		from time import sleep
		self.sleep = sleep

	@property
	def web3(self):
		"""The Web3 instance to interact with the Ethereum network."""
		return self._web3

	@web3.setter
	def web3(self, value):
		"""Set the Web3 instance."""
		self._web3 = value

	@property
	def gas(self):
		"""The current gas price."""
		return self._gas

	@gas.setter
	def gas(self, value):
		"""Set the current gas price."""
		self._gas = value

	@property
	def gas_price(self):
		"""The estimated gas price for a transaction."""
		return self._gas_price

	@gas_price.setter
	def gas_price(self, value):
		"""Set the estimated gas price for a transaction."""
		self._gas_price = value

	@property
	def nonce(self):
		"""The current nonce for an address."""
		return self._nonce

	@nonce.setter
	def nonce(self, value):
		"""Set the current nonce for an address."""
		self._nonce = value

	def gas_monitor(self, token_contract, sender: str, period: float | int = 10, multiply_by: float = 1.0) -> None:
		"""
		Continuously updates the estimated required gas for a transaction at a specified interval.

		:param token_contact: Token contract with 'transfer' function
		:param sender: Sender address (checksumed, make sure)
		:type sender: str
		:param period: The interval in seconds between updates.
		:type period: float | int
		"""
		dead = '0x000000000000000000000000000000000000dEaD'

		while True:
			self._gas = round(token_contract.functions.transfer(dead, 0).estimate_gas({'from': sender}) * multiply_by)
			self.sleep(period)

	def gas_price_monitor(self, period: float | int = 10, multiply_by: float = 1.0) -> None:
		"""
		Continuously updates the gas price at a specified interval.

		:param period: The interval in seconds between updates.
		:type period: float | int
		"""
		while True:
			self._gas_price = round(self.web3.eth.gas_price * multiply_by)
			self.sleep(period)

	def nonce_monitor(self, address: str, period: float | int = 10) -> None:
		"""
		Continuously updates the nonce for a given address at a specified interval.

		:param address: The Ethereum address to monitor.
		:type address: str
		:param period: The interval in seconds between updates.
		:type period: float | int
		"""
		while True:
			self._nonce = self.web3.eth.get_transaction_count(address)
			self.sleep(period)

	def get_nonce(self, address: str) -> int:
		"""
		Retrieves the current nonce for a given address.

		:param address: The Ethereum address.
		:type address: str
		:return: The current nonce for the address.
		:rtype: int
		"""
		return self.web3.eth.get_transaction_count(address)

# format_mc_versions() Helper function to determine if one version is the direct successor of another
def is_direct_successor(v1, v2):
	if (v1.startswith('1.') and not v2.startswith('1.')) or (not v1.startswith('1.') and v2.startswith('1.')) or (not v1.startswith('1.') and not v2.startswith('1.')) or '-pre' in v1.lower() or '-rc' in v1.lower() or '-pre' in v2.lower() or '-rc' in v2.lower():
		return True

	try:
		parts1 = [int(part) for part in v1.split('.')]
		parts2 = [int(part) for part in v2.split('.')]

		if len(parts1) == 2:
			parts1.append(0)
		if len(parts2) == 2:
			parts2.append(0)

		if parts1[0] == parts2[0]:

			if parts1[1] == parts2[1]:
				return parts1[2] + 1 == parts2[2]
			elif parts1[1] + 1 == parts2[1]:
				return parts2[2] == 0

		return False

	except ValueError:
		return False

def format_mc_versions(mc_vers):
	if not mc_vers:
		return ''

	# Initialize the message and the starting point for a range of consecutive versions
	msg = ''
	start_ver = None
	last_ver = None

	for i in range(len(mc_vers)):
		ver = mc_vers[i]

		# Check if current version follows the last version directly
		if last_ver is not None and is_direct_successor(last_ver, ver):
			last_ver = ver
			continue

		# If not, handle the end of a version range and reset
		if last_ver is not None:
			if start_ver != last_ver:
				msg += f'{start_ver}-{last_ver}, '
			else:
				msg += f'{last_ver}, '

		# Set new start and last versions
		start_ver = ver
		last_ver = ver

	# Add the last processed version or range
	if last_ver is not None:

		if start_ver != last_ver:
			msg += f'{start_ver}-{last_ver}'
		else:
			msg += f'{last_ver}'

	return msg.strip(', ')