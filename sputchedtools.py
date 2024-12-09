from typing import Literal
from collections.abc import Iterator, Iterable

ReturnTypes = Literal['ATTRS', 'charset', 'close', 'closed', 'connection', 'content', 'content_disposition', 'content_length', 'content_type', 'cookies', 'get_encoding', 'headers', 'history', 'host', 'json', 'links', 'ok', 'raise_for_status', 'raw_headers', 'read', 'real_url', 'reason', 'release', 'request_info', 'start', 'status', 'text', 'url', 'url_obj', 'version', 'wait_for_close']

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
		aio.request() - aiohttp.ClientSession.get() request
		aio.post() - aiohttp.ClientSession.post() request
		aio.open() - aiofiles.open() method
		aio.sem_task() - uses received semaphore to return function execution result

	"""

	@staticmethod
	async def _request(
		method: callable,
		url: str,
		toreturn: ReturnTypes = ('text'),
		session = None,
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

		import aiohttp, asyncio, inspect

		return_items = []
		ses = session or aiohttp.ClientSession()

		if isinstance(toreturn, str):
			toreturn = toreturn.split('+') # Previous

		try:
			async with ses.request(method, url, **kwargs) as response:

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

		finally:
			if not session: await ses.close()
			return return_items

	@staticmethod
	async def request(
		url: str,
		toreturn: ReturnTypes = ('text'),
		session = None,
		**kwargs
	):
		return await aio._request('GET', url, toreturn, session, **kwargs)

	@staticmethod
	async def post(
		url: str,
		toreturn: ReturnTypes = ('text'),
		session = None,
		**kwargs
	):

		return await aio._request('POST', url, toreturn, session, **kwargs)

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
			Example: num.shorten(10_000_000, 0) -> '10m'

		num.unshorten() - Unshortens str, using expandable / editable num.multipliers dictionary
			Example: num.unshorten('1.63k', round = False) -> 1630.0

		num.decim_round() - Safely rounds decimals in float
			Example: num.decim_round(2.000127493, 2) -> '2.00013'

		num.beautify() - returns decimal-rounded, shortened float-like string
			Example: num.beautify(4349.567, 3) -> 4.35k

	"""

	suffixes = ['', 'K', 'M', 'B', 'T', 1000]
	fileSize_suffixes = [' B', ' KB', ' MB', ' GB', ' TB', 1024]

	multipliers: dict[str, int] = {'k': 10**3, 'm': 10**6, 'b': 10**9, 't': 10**12}
	decims: list[int] = [1000, 100, 10, 5] # List is iterated using enumerate(), so by each iter. decimal amount increases by 1 (starting from 0)

	@staticmethod
	def shorten(value: int | float, decimals: int = 2, suffixes = None) -> str:
		"""
		Accepts:
			value: int - big value
			decimals: int = 2: digit amount

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
				unshortened = num.decim_round(number * mp, decimals)

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
			decimals: int: determines amount of digits (+2 for rounding, after decimal point) that will be used in 'calculations'
			precission: int: determines precission level (format(value, f'.->{precission}<-f'

		Returns:
			Accepted value:
				if value == 0,
				not isinstance(value & (decimals, precission), float & int)
				decimals & value < 1

			float-like str

		"""

		if isinstance(value, int): return value
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
					return str(round(value, None or decim_amount))

				decimals = decim_amount
				break

		if round_if_num_gt_1:
			return str(round(value, None or decimals))

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
