from typing import Literal
from collections.abc import Iterator, Iterable

ReturnTypes = Literal['ATTRS', 'charset', 'close', 'closed', 'connection', 'content', 'content_disposition', 'content_length', 'content_type', 'cookies', 'get_encoding', 'headers', 'history', 'host', 'json', 'links', 'ok', 'raise_for_status', 'raw_headers', 'read', 'real_url', 'reason', 'release', 'request_info', 'start', 'status', 'text', 'url', 'url_obj', 'version', 'wait_for_close']
Algorithms = Literal['gzip', 'bzip2', 'lzma', 'zlib', 'lz4', 'zstd', 'brotli']
algorithms = ['gzip', 'bzip2', 'lzma', 'zlib', 'lz4', 'zstd', 'brotli']

class Anim:
	def __init__(
		self,
		prepend_text = '', append_text = '',
		just_clear_char = True,
		clear_on_exit = False,
		delay = 0.03,
		chars = None
	):
		from threading import Thread
		from shutil import get_terminal_size
		from time import sleep

		self.Thread = Thread
		self.get_terminal_size = get_terminal_size
		self.sleep = sleep

		self.chars = chars or ('⠙', '⠘', '⠰', '⠴', '⠤', '⠦', '⠆', '⠃', '⠋', '⠉')
		self._prepend_text = prepend_text
		if len(self._prepend_text) != 0 and not self._prepend_text.endswith(' '):
			self._prepend_text += ' '
		self._append_text = append_text
		self.just_clear_char = just_clear_char
		self.clear_on_exit = clear_on_exit
		self.delay = delay

		self.terminal_size = self.get_terminal_size().columns
		self.max_char_len = len(max(self.chars, key=len))
		self.max_line_length = len(self._prepend_text + self._append_text) + self.max_char_len
		self.done = False

	def set_text(self, set_text: str, prepended: bool = True):
		if prepended:
			attr = '_prepend_text'
		else:
			attr = '_append_text'

		new_len = len(set_text)
		len_diff = abs(self.max_line_length - new_len - 1)

		if self.max_line_length < new_len:
			self.max_line_length = new_len

		setattr(self, attr, set_text)

		spaces = ' ' * len_diff
		if spaces: self._append_text += spaces

	def safe_line_echo(self, text: str):

		if len(text) > self.terminal_size:
			text = text[:self.terminal_size - 1]

		print(text, end='', flush=True)

	def anim(self):
		while not self.done:
			# self.terminal_size = self.get_terminal_size().columns

			for text in self.chars:

				line = '\r' + self._prepend_text + text + self._append_text
				self.safe_line_echo(line)
				self.sleep(self.delay)

		if self.clear_on_exit:
			self.safe_line_echo('\r' + ' ' * (len(self._prepend_text + self._append_text) + self.max_char_len))

		elif self.just_clear_char:
			self.safe_line_echo('\r' + self._prepend_text + ' ' * self.max_char_len + self._append_text)

	def __enter__(self):
		self.thread = self.Thread(target=self.anim)
		self.thread.start()
		return self

	def __exit__(self, *args):
		self.done = True
		self.thread.join()

class NewLiner:
	"""
	Simply adds a newline before and after the block of code.
	Use with 'with' keyword.
	"""

	def __init__(self):
		self.out = __import__('sys').stdout

	def __enter__(self):
		self.out.write('\n')
		self.out.flush()

	def __exit__(self, *args):
		self.out.write('\n')
		self.out.flush()

class Timer:

	"""

	Code execution Timer, use 'with' keyword

	Accepts (order doesn't matter from 0.16.2):
		txt: str = '': text after main print message
		decimals: int = 2: time difference precission

	"""

	def __init__(self, txt = '', echo = True):
		from time import perf_counter
		self.time = perf_counter
		self.echo = echo

		if isinstance(txt, bool):
			self.echo = txt
			self.txt = echo if isinstance(echo, str) else ''

		else:
			self.txt = txt
			self.echo = echo

	def __enter__(self):
		self.was = self.time()
		return self

	def __exit__(self, *args):
		self.diff = self.time() - self.was
		formatted = num.decim_round(self.diff, -1)
		if self.echo: print(f'\nTaken time: {formatted}s {self.txt}')
		return formatted

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

class aio:
	"""
	Methods:
		aio.request() - 'GET' request object for aio._request (httpx / aiohttp)
		aio.post() - 'POST' request object for aio._request (httpx / aiohttp)
		aio.open() - aiofiles.open() method
		aio.sem_task() - uses received semaphore to return function execution result

	"""

	@staticmethod
	async def _request(
		method: Literal['GET', 'POST'],
		url: str,
		toreturn: ReturnTypes = 'text',
		session = None,
		raise_exceptions = False,
		httpx = False,
		**kwargs,

	):

		"""
		Accepts:

			Args:
				method: str - `GET` or `POST` Client Session request callable
				url: str

			Kwargs:
				toreturn: ReturnTypes - List or Str separated by `+` of response object methods/properties paths
				session: httpx/aiohttp Client Session
				raise_exceptions: bool - Wether to raise occurred exceptions while making request or return list of None (or append to existing items) with same `toreturn` length

				any other session.request() argument

		Returns:
			Valid response: [data]

			Request Timeout: [0] + toreturn
			Cancelled Error: [None] + toreturn
			Exception: Raise if raise_exceptions else return_items + None * ( len( toreturn ) - len( existing_items ) )

		"""
		import asyncio, inspect

		if not session:
			if httpx:
				import httpx
				ses = httpx.AsyncClient(http2 = True, follow_redirects = True)

			else:
				import aiohttp
				ses = aiohttp.ClientSession()

			# ses = CreateSession()

		else:
			ses = session

		if isinstance(toreturn, str):
			toreturn = toreturn.split('+') # Previous data return method

		return_items = []

		try:
			response = await ses.request(method, url, **kwargs)

			for item in toreturn:

				try:
					result = eval(f'response.{item}')

					if inspect.isfunction(result):
						result = result()
					elif inspect.iscoroutinefunction(result):
						result = await result()
					elif inspect.iscoroutine(result):
						result = await result

				except:
					result = None

				return_items.append(result)

		except asyncio.TimeoutError:
			return_items.insert(0, 0)

		except asyncio.CancelledError:
			return

		except:
			if raise_exceptions:
				raise

			items_length = len(return_items)
			return_length = len(toreturn)

			for _ in range(items_length, return_length):
				return_items.append(None)

		if not session:
			if httpx: await ses.aclose()
			else: await ses.close()

		return return_items

	@staticmethod
	async def request(
		url: str = 'https://example.com/',
		toreturn: ReturnTypes = 'text',
		session = None,
		raise_exceptions = False,
		httpx = False,
		**kwargs,
	):
		return await aio._request('GET', url, toreturn, session, raise_exceptions, httpx, **kwargs)

	@staticmethod
	async def post(
		url: str = 'https://example.com/',
		toreturn: ReturnTypes = 'text',
		session = None,
		raise_exceptions = False,
		httpx = False,
		**kwargs,
	):
		return await aio._request('POST', url, toreturn, session, raise_exceptions, httpx, **kwargs)

	@staticmethod
	async def open(
		file: str,
		action: str = 'read',
		mode: str = 'r',
		content = None,
		**kwargs
	):
		"""
		Asynchronously read from or write to a file using aiofiles.

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
			Example: num.shorten(10_000_000, 0) -> '10M'

		num.unshorten() - Unshortens str, using expandable / editable num.multipliers dictionary
			Example: num.unshorten('1.63k', round = False) -> 1630.0

		num.decim_round() - Safely rounds decimals in float
			Example: num.decim_round(2.000127493, 2, round_if_num_gt_1 = False) -> '2.00013'

		num.beautify() - returns decimal-rounded, shortened float-like string
			Example: num.beautify(4349.567, -1) -> 4.35K

	"""

	suffixes = ['', 'K', 'M', 'B', 'T', 1000]
	fileSize_suffixes = [' B', ' KB', ' MB', ' GB', ' TB', 1024]

	multipliers: dict[str, int] = {'k': 10**3, 'm': 10**6, 'b': 10**9, 't': 10**12}
	decims: list[int] = [1000, 100, 10, 5] # List is iterated using enumerate(), so by each iter. decimal amount increases by 1 (starting from 0)

	@staticmethod
	def shorten(value: int | float, decimals: int = 2, suffixes: list[str] = None) -> str:
		"""
		Accepts:
			value: int - big value
			decimals: int = 2: digit amount
			suffixes: list[str] - Use case: File Size calculation: pass `[' B', ' KB', ' MB', ' GB', ' TB', 1024]` or num.fileSize_suffixes

		Returns:
			Shortened float or int-like str

		"""

		absvalue = abs(value)
		suffixes = suffixes or num.suffixes
		magnitude = suffixes[-1]

		for i, suffix in enumerate(suffixes[:-1]):
			unit = magnitude ** i
			if absvalue < unit * magnitude or i == len(suffixes) - 1:
				value /= unit
				formatted = num.decim_round(value, decimals, decims = [100, 10, 1])
				return f"{formatted}{suffix}"

	@staticmethod
	def unshorten(value: str, round: bool = True, decimals: int = 2) -> float | int:
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
		number = value[:-1]

		try:
			number = float(number)
			mp = num.multipliers[mp]

			if round:
				unshortened = num.decim_round(number * mp, 0)

			else:
				unshortened = number * mp

			return unshortened

		except (ValueError, KeyError):
			return value

	@staticmethod
	def decim_round(value: float, decimals: int = 2, round_if_num_gt_1: bool = True, precission: int = 20, decims: list[int] = None) -> str:
		"""
		Accepts:
			value: float: usually with medium-big decimal length
			round_if_num_gt_1: bool - Wether to use built-in round() method to round received value to received decimals (None if 0)
			decimals: int: determines amount of digits (+2 for rounding, after decimal point) that will be used in 'calculations'
			precission: int: determines precission level (format(value, f'.->{precission}<-f'

		Returns:
			if isinstance(value, int): str(value)
			float-like str

		"""

		if isinstance(value, int): return str(value)

		str_val = format(value, f'.{precission}f')

		integer, decim = str_val.split('.')
		round_if_num_gt_1 = abs(value) > 1 and round_if_num_gt_1

		if decimals == -1:
			absvalue = abs(value)
			decims = decims or num.decims
			decimals = len(decims)

			for decim_amount, min_num in enumerate(decims):
				if absvalue < min_num: continue

				elif round_if_num_gt_1:
					return str(round(value, decim_amount or None))

				decimals = decim_amount
				break

		if round_if_num_gt_1:
			return str(round(value, decimals or None))

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
		return self._web3

	@web3.setter
	def web3(self, value):
		self._web3 = value

	@property
	def gas(self):
		return self._gas

	@gas.setter
	def gas(self, value):
		self._gas = value

	@property
	def gas_price(self):
		return self._gas_price

	@gas_price.setter
	def gas_price(self, value):
		self._gas_price = value

	@property
	def nonce(self):
		return self._nonce

	@nonce.setter
	def nonce(self, value):
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

# -------------MINECRAFT-VERSIONING-LOL-------------

class MC_VersionList:
	def __init__(self, versions, indices) -> None:
		self.length = len(versions)

		if self.length != len(indices):
			raise ValueError

		self.versions = versions
		self.indices = indices
		self.map = {version: index for version, index in zip(versions, indices)}

class MC_Versions:
	def __init__(self) -> None:
		import asyncio
		self.manifest_url = 'https://launchermeta.mojang.com/mc/game/version_manifest.json'

		try:
			loop = asyncio.get_event_loop()
		except RuntimeError:
			enhance_loop()
			loop = asyncio.new_event_loop()
			asyncio.set_event_loop(loop)

		loop.run_until_complete(self.fetch_version_manifest())

	def sort(self, mc_vers: list[str]) -> list[str]:
		filtered_vers = set()

		for ver in mc_vers:
			if not ver: continue

			try:
				filtered_vers.add(self.release_versions.index(ver))
			except ValueError:
				continue

		sorted_indices = sorted(filtered_vers)

		return MC_VersionList([self.release_versions[index] for index in sorted_indices], sorted_indices)

	def get_range(self, mc_vers: MC_VersionList) -> str:
		version_range = ''
		start = mc_vers.versions[0]  # Start of a potential range
		end = start  # End of the current range

		for i in range(1, mc_vers.length):
			# Check if the current index is a successor of the previous one
			if mc_vers.indices[i] == mc_vers.indices[i - 1] + 1:
				end = mc_vers.versions[i]  # Extend the range
			else:
				# Add the completed range or single version to the result
				if start == end:
					version_range += f'{start}, '
				else:
					version_range += f'{start} - {end}, '
				start = mc_vers.versions[i]  # Start a new range
				end = start

		# Add the final range or single version
		if start == end:
			version_range += start
		else:
			version_range += f'{start} - {end}'

		return version_range

	async def fetch_version_manifest(self):
		response = await aio.request(self.manifest_url, toreturn = ['json', 'status'])
		manifest_data, status = response

		if status != 200 or not isinstance(manifest_data, dict):
			raise TypeError(f"Couldn't fetch minecraft versions manifest from `{self.manifest_url}`\nStatus: {status}")

		self.release_versions: list[str] = []

		for version in manifest_data['versions']:
			if version['type'] == 'release':
				self.release_versions.append(version['id'])

		self.release_versions.reverse() # Ascending

	@property
	def latest(self):
		return self.release_versions[-1]

	def is_version(self, version):
		try:
			self.release_versions.index(version)
			return True
		except ValueError:
			return False

def make_tarball(source, output):
	import tarfile, os

	with tarfile.open(output, "w") as tar:
		tar.add(source, arcname=os.path.basename(source))
	return output

def compress_file(source, output, algorithm_func, additional_args):
	with open(source, "rb") as f:
		data = f.read()
	compressed_data = algorithm_func(data, **additional_args)
	with open(output, "wb") as f:
		f.write(compressed_data)
	return output

def compress(source: str | bytes, algorithm: Algorithms = 'gzip', output=None, compression_level=1, **kwargs):
	import os

	algorithm_map = {
		'gzip': (lambda: __import__('gzip').compress, {'compresslevel': compression_level}),
		'bzip2': (lambda: __import__('bz2').compress, {'compresslevel': compression_level}),
		'lzma': (lambda: __import__('lzma').compress, {'preset': compression_level}),
		'lzma2': (lambda: __import__('lzma').compress, lambda: {'format': __import__('lzma').FORMAT_XZ, 'preset': compression_level}),
		'zlib': (lambda: __import__('zlib').compress, {'level': compression_level}),
		'lz4': (lambda: __import__('lz4.frame').frame.compress, {}),
		'zstd': (lambda: __import__('zstandard').compress, {}),
		'brotli': (lambda: __import__('brotli').compress, lambda: {'mode': __import__('brotli').MODE_GENERIC, 'quality': compression_level}),
	}

	# tar_required = True
	a_compress, additional_args = algorithm_map[algorithm]
	a_compress = a_compress()

	# if isinstance(a_compress, tuple):
	# 	# tar_required = False
	# 	a_compress, a_open = a_compress

	if callable(additional_args):
		additional_args = additional_args()

	if isinstance(source, bytes):
		return a_compress(
			source, **additional_args
		)

	if not output:
		output = os.path.basename(os.path.abspath(source)) + f".{algorithm}"

	# if tar_required:
	tar_path = output + ".tar"
	make_tarball(source, tar_path)
	source = tar_path

	compress_file(source, output, a_compress, additional_args)

	# if tar_required:
	os.remove(source)

	return output

def decompress(source: str | bytes, algorithm: Algorithms = None, output: str = None):
	algorithm_map = {
		'gzip': (lambda: __import__('gzip').decompress, b'\x1f\x8b\x08'),
		'bzip2': (lambda: __import__('bz2').decompress, b'BZh'),
		'lzma': (lambda: __import__('lzma').decompress, b'\xfd7zXZ\x00'),
		'zlib': (lambda: __import__('zlib').decompress, b'\x78\x01'),
		'lz4': (lambda: __import__('lz4.frame').frame.decompress, b'\x04\x22\x4d\x18'),
		'zstd': (lambda: __import__('zstandard').decompress, b'\x28\xb5\x2f\xfd'),
		'brotli': (lambda: __import__('brotli').decompress, (b'\x8b', b'\x0b', b'\x1a', b'\x02')),
	}

	is_bytes = isinstance(source, bytes)
	if not is_bytes:
		content = open(source, 'rb').read()
	else: content = source

	if not algorithm:
		for algorithm, (a_decompress, start_bytes) in algorithm_map.items():
			if content.startswith(start_bytes):
				break

	if not algorithm:
		raise ValueError(f"Could not detect algorithm for decompression, start bytes: {content[:10]}")

	a_decompress = algorithm_map[algorithm][0]()

	if is_bytes:
		return a_decompress(source)

	if not output:
		output = source.split('.', 1)[0]

	import tarfile, io

	decompressed = a_decompress(content)
	stream = io.BytesIO(decompressed)

	if tarfile.is_tarfile(stream):
		with tarfile.open(fileobj=stream) as tar:
			tar.extractall(output)
	else:
		with open(output, 'wb') as f:
			f.write(decompressed)

	return output