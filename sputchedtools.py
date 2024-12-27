from typing import Literal
from collections.abc import Iterator, Iterable

ReturnTypes = Literal['ATTRS', 'charset', 'close', 'closed', 'connection', 'content', 'content_disposition', 'content_length', 'content_type', 'cookies', 'get_encoding', 'headers', 'history', 'host', 'json', 'links', 'ok', 'raise_for_status', 'raw_headers', 'read', 'real_url', 'reason', 'release', 'request_info', 'start', 'status', 'text', 'url', 'url_obj', 'version', 'wait_for_close']
Algorithms = Literal['gzip', 'bzip2', 'lzma', 'deflate', 'lz4', 'zstd', 'brotli']
algorithms = ['gzip', 'bzip2', 'lzma', 'deflate', 'lz4', 'zstd', 'brotli']

class Anim:
	def __init__(
		self,
		prepend_text = '', append_text = '',
		just_clear_char = True,
		clear_on_exit = False,
		delay = 0.03,
		manual_update = False,
		chars = None
	):
		from threading import Thread
		from shutil import get_terminal_size
		from time import sleep

		self.Thread = Thread
		self.get_terminal_size = get_terminal_size
		self.sleep = sleep

		self.chars = chars or  ('⠉', '⠙', '⠘', '⠰', '⠴', '⠤', '⠦', '⠆', '⠃', '⠋')
		self.prepend_text = prepend_text

		if len(self.prepend_text) != 0 and not self.prepend_text.endswith(' '):
			self.prepend_text += ' '

		self.append_text = append_text
		self.just_clear_char = just_clear_char
		self.clear_on_exit = clear_on_exit
		self.delay = delay
		self.manual_update = manual_update

		self.terminal_size = self.get_terminal_size().columns
		self.chars = self.adapt_chars_spaces(self.chars)
		self.char = self.chars[0]
		self.done = False

	def get_line(self):
		return f'\r{self.prepend_text}{self.char}{self.append_text}'

	@classmethod
	def get_max_char_len(cls, chars) -> int:
		if not all(hasattr(char, '__len__') for char in chars):
			last_char = chars[-1]

			if hasattr(last_char, '__str__'):
				return len(
					str(chars[-1])
				)
			else:
				raise TypeError(f'Provided char list has neither `__len__` nor `__str__` attribute')

		return len(
			max(chars, key = len)
		)

	@classmethod
	def adapt_chars_spaces(cls, chars) -> list | tuple:
		mcl = cls.get_max_char_len(chars)
		if mcl <= 1:
			return chars

		new_chars = []

		for char in chars:
			char_len = len(char)
			len_diff = mcl - char_len

			if len_diff:
				char += ' ' * len_diff

			new_chars.append(char)

		return new_chars

	def set_chars(self, new_chars: tuple | list):
		self.chars = self.adapt_chars_spaces(new_chars)

	def set_text(self, new_text: str, prepended: bool = True):
		new_len = len(new_text)
		if new_len > self.terminal_size:
			return

		if prepended:
			attr = 'prepend_text'
		else:
			attr = 'append_text'

		old_len = len(getattr(self, attr))
		setattr(self, attr, new_text)

		if new_len < old_len:
			diff = abs(old_len - new_len)
			spaces = ' ' * diff
			self.safe_line_echo(self.get_line() + spaces)

	def safe_line_echo(self, text: str):
		if len(text) > self.terminal_size:
			text = text[:self.terminal_size]

		print(text, end = '', flush = True)

	def update(self):
		line = self.get_line()
		self.safe_line_echo(line)

	def anim(self):
		while not self.done:
			for self.char in self.chars:
				if self.done: break

				self.update()
				self.sleep(self.delay)

		if self.clear_on_exit:
			self.safe_line_echo('\r' + ' ' * len(self.get_line()) + '\r')

		elif self.just_clear_char:
			self.safe_line_echo('\r' + self.prepend_text + ' ' * len(self.char) + self.append_text)

	def __enter__(self):
		if self.manual_update:
			self.update()

		else:
			self.thread = self.Thread(target=self.anim)
			self.thread.start()

		return self

	def __exit__(self, exc_type, exc_value, exc_traceback):
		if exc_type:
			raise exc_value.with_traceback(exc_traceback)

		if not self.manual_update:
			self.done = True
			self.thread.join()

class NewLiner:

	"""

	Simply adds a new line before and after the block of code.

	"""

	def __init__(self):
		self.out = __import__('sys').stdout

	def __enter__(self):
		self.out.write('\n')
		self.out.flush()

	def __exit__(self, exc_type, exc_value, exc_traceback):
		if exc_type:
			raise exc_value.with_traceback(exc_traceback)

		self.out.write('\n')
		self.out.flush()

class Timer:

	"""

	Accepts (order doesn't matter from 0.16.2):

		txt: str = '': text after main print message

		echo: bool = True: wether to print taken time

	At enter - returns created instance, at exit - formatted time difference. Original difference is stored at self.diff

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

	def __exit__(self, exc_type, exc_value, exc_traceback):
		if exc_type:
			raise exc_value.with_traceback(exc_traceback)

		self.diff = self.time() - self.was
		self.formatted_diff = num.decim_round(self.diff, -1)
		if self.echo: print(f'\nTaken time: {self.formatted_diff}s {self.txt}')

		return self.formatted_diff

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
				raise AttributeError(f"You didn't provide task amount for Iterator or object with no __len__ attribute\n\nType: {type(iterator)}\nAttrs: {dir(iterator)}")

			self.task_amount = iterator.__len__()

		else: self.task_amount = task_amount

		from sys import stdout
		self._text = text
		self.completed_tasks = 0
		self.final_text = final_text
		self.swrite = stdout.write
		self.sflush = stdout.flush

	@property
	def text(self):
		return self._text

	@text.setter
	def text(self, value: str):
		val_len = len(value)
		text_len = len(self._text)
		self._text = value + ' ' * (text_len - val_len if text_len > val_len else 0)

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
		self.completed_tasks += increment
		self.print_progress()

	def print_progress(self):
		self.swrite(f'\r{self._text} {self.completed_tasks}/{self.task_amount}')
		self.sflush()

	def finish(self):
		self.finish_message = f'\r{self._text} {self.completed_tasks}/{self.task_amount} {self.final_text}\n'
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
				raise AttributeError(f"You didn't provide task amount for Async Iterator\n\nType: {type(tasks)}\nAttrs: {dir(tasks)}")

			else:
				self.task_amount = tasks.__len__()

		else: self.task_amount = task_amount

		self.text = text
		self.final_text = final_text
		self.completed_tasks = 0

		if tasks:
			if hasattr(tasks, '__aiter__'):
				self.tasks = tasks

			else:
				raise ValueError("tasks must be an async iterator or None")

	async def update(self, increment: int = 1):
		self.completed_tasks += increment
		self.print_progress()

	def print_progress(self):
		self.swrite(f'\r{self.text} {self.completed_tasks}/{self.task_amount}')
		self.sflush()

	async def _finish(self):

		if self.task_amount is not None:
			self.finish_message = f'\r{self.text} {self.completed_tasks}/{self.task_amount} {self.final_text}\n'

		else:
			self.finish_message = f'\r{self.text} {self.completed_tasks} {self.final_text}\n'

		self.swrite(self.finish_message)
		self.sflush()
		self.completed_tasks = 0

	async def as_completed(self, tasks):

		for task in self.asyncio.as_completed(tasks):
			result = await task
			await self.update()
			yield result

		await self._finish()

	async def gather(self, tasks):
		results = []

		for task in self.asyncio.as_completed(tasks):
			result = await task
			await self.update()
			results.append(result)

		await self._finish()
		return results

	async def __aiter__(self):
		if not hasattr(self, 'tasks'):
			raise ValueError("You didn't specify coroutine iterator")

		async for task in self.tasks:
			await self.update()
			yield task

		await self._finish()

class aio:

	"""

	Methods:
		- aio.request() - 'GET' wrapper for aio._request
		- aio.post() - 'POST' wrapper for aio._request
		- aio.open() - aiofiles.open() method
		- aio.sem_task() - uses received semaphore to return function execution result

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

			- method: `GET` or `POST` request type
			- url: str

			- toreturn: ReturnTypes - List or Str separated by `+` of response object methods/properties paths

			- session: httpx/aiohttp Client Session

			- raise_exceptions: bool - Wether to raise occurred exceptions while making request or return list of None (or append to existing items) with same `toreturn` length

			- any other session.request() argument

		Returns:
			- Valid response: [data]

			- Request Timeout: [0, *toreturn]
			- Cancelled Error: [None, *toreturn]
			- Exception: Raise if raise_exceptions else return_items + None * ( len(toreturn) - len(existing_items) )

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
					result = getattr(response, item)

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

		except (Exception, asyncio.CancelledError):
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

		Accepts:

			- file: str - File path

			- action: str - Operation to perform ('read' or 'write')

			- mode: str - File open mode ('r', 'w', 'rb', 'wb', etc.)

			- content: Any - Content to write (required for write operation)

			- Any other arguments for aiofiles.open()

		Returns:
			- str | bytes: File content if action != 'write'
			- int: Number of bytes written if action == 'write'

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
		async with semaphore:
			return await func(*args, **kwargs)

def enhance_loop() -> bool:
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

		- num.shorten() - Shortens float | int value, using expandable / editable num.suffixes dictionary
			Example: num.shorten(10_000_000, 0) -> '10M'

		- num.unshorten() - Unshortens str, using expandable / editable num.multipliers dictionary
			Example: num.unshorten('1.63k', _round = False) -> 1630.0

		- num.decim_round() - Safely rounds decimals in float
			Example: num.decim_round(2.000127493, 2, round_if_num_gt_1 = False) -> '2.00013'

		- num.beautify() - returns decimal-rounded, shortened float-like string
			Example: num.beautify(4349.567, -1) -> 4.35K

	"""

	suffixes = ['', 'K', 'M', 'B', 'T', 1000]
	fileSize_suffixes = [' B', ' KB', ' MB', ' GB', ' TB', 1024]

	multipliers: dict[str, int] = {'k': 10**3, 'm': 10**6, 'b': 10**9, 't': 10**12}
	decims: list[int] = [1000, 100, 10, 5] # List is iterated using enumerate(), so by each iter. decimal amount increases by 1 (starting from 0)

	@staticmethod
	def shorten(
		value: int | float,
		decimals: int = 2,
		suffixes: list[str] = None
	) -> str:

		"""

		Accepts:

			- value: int - big value
			- decimals: int = 2 - round digit amount

			- suffixes: list[str] - Use case: File Size calculation: pass num.fileSize_suffixes

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
	def unshorten(
		value: str,
		_round: bool = True
	) -> float | int:

		"""

		Accepts:

			- value: str - int-like value with shortener at the end

			- _round: bool - wether returned value should be rounded to integer

		Returns:
			Unshortened float or int

		"""

		mp = value[-1].lower()
		number = value[:-1]

		try:
			number = float(number)
			mp = num.multipliers[mp]

			if _round:
				unshortened = round(number * mp)

			else:
				unshortened = number * mp

			return unshortened

		except (ValueError, KeyError):
			return value

	@staticmethod
	def decim_round(
		value: float,
		decimals: int = 2,
		round_if_num_gt_1: bool = True,
		precission: int = 20,
		decims: list[int] = None
	) -> str:

		"""

		Accepts:

			- value: float - usually with medium-big decimal length

			- round_if_num_gt_1: bool - Wether to use built-in round() method to round received value to received decimals (None if 0)

			- decimals: int - amount of digits (+2 for rounding, after decimal point) that will be used in 'calculations'

			- precission: int - precission level (format(value, f'.->{precission}<-f'

			- decims: list[int] - if decimals argument is -1, this can be passed to change how many decimals to leave: default list is [1000, 100, 10, 5], List is iterated using enumerate(), so by each iter. decimal amount increases by 1 (starting from 0)

		Returns:
			- float-like str
			- str(value): if isinstance(value, int)

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

		for i, char in enumerate(decim):
			if char != '0': break

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

	Methods:
		- gas_monitor()
		- gas_price_monitor()
		- nonce_monitor()
		- get_nonce()

	Attributes:
		- web3: web3.Web3 instance

	"""

	def __init__(self, web3):

		self.web3 = web3
		self.gas = None
		self.gas_price = None
		self.nonce = None

		from time import sleep
		self.sleep = sleep

	def gas_monitor(
		self,
		token_contract: str,
		sender: str,
		period: float | int = 10,
		multiply_by: float = 1.0
	) -> None:
		dead = '0x000000000000000000000000000000000000dEaD'

		while True:
			self.gas = round(token_contract.functions.transfer(dead, 0).estimate_gas({'from': sender}) * multiply_by)
			self.sleep(period)

	def gas_price_monitor(
		self,
		period: float | int = 10,
		multiply_by: float = 1.0
	) -> None:

		while True:
			self.gas_price = round(self.web3.eth.gas_price * multiply_by)
			self.sleep(period)

	def nonce_monitor(
		self,
		address: str,
		period: float | int = 10
	) -> None:

		while True:
			self.nonce = self.web3.eth.get_transaction_count(address)
			self.sleep(period)

	def get_nonce(self, address: str) -> int:
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
		from re import findall

		self.manifest_url = 'https://launchermeta.mojang.com/mc/game/version_manifest.json'

		self.findall = findall
		# Pattern for a single version
		version_pattern = r'1\.\d+(?:\.\d+){0,1}'
		# Pattern for a single version or a version range
		item_pattern = rf'{version_pattern}(?:\s*-\s*{version_pattern})*'
		# Full pattern allowing multiple items separated by commas
		self.full_pattern = rf'{item_pattern}(?:,\s*{item_pattern})*'

		try:
			loop = asyncio.get_event_loop()
		except RuntimeError:
			enhance_loop()
			loop = asyncio.new_event_loop()
			asyncio.set_event_loop(loop)

		loop.run_until_complete(self.fetch_version_manifest())
		self.latest = self.release_versions[-1]

	def sort(self, mc_vers: list[str]) -> list[str]:
		filtered_vers = set()

		for ver in mc_vers:
			if not ver: continue

			try:
				filtered_vers.add(
					self.release_versions.index(ver)
				)

			except ValueError:
				continue

		sorted_indices = sorted(filtered_vers)

		return MC_VersionList([self.release_versions[index] for index in sorted_indices], sorted_indices)

	def get_range(self, mc_vers: MC_VersionList | list | tuple) -> str:
		if isinstance(mc_vers, (list, tuple)):
			mc_vers = self.sort(mc_vers)

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

	def get_list(self, mc_vers: str):
		return self.findall(self.full_pattern, mc_vers)

	async def fetch_version_manifest(self):
		response = await aio.request(self.manifest_url, toreturn = ['json', 'status'])
		manifest_data, status = response

		if status != 200 or not isinstance(manifest_data, dict):
			raise ConnectionError(f"Couldn't fetch minecraft versions manifest from `{self.manifest_url}`\nStatus: {status}")

		self.release_versions: list[str] = []

		for version in manifest_data['versions']:
			if version['type'] == 'release':
				self.release_versions.append(version['id'])

		self.release_versions.reverse() # Ascending

	def is_version(self, version: str):
		try:
			self.release_versions.index(version)
			return True
		except ValueError:
			return False

def get_content(source: str | bytes) -> tuple[int, bytes]:
	"""
	Returns source byte content
	Source can be either a file_path, readable buffer or just bytes
	First tuple object is source type:
		1 - bytes
		2 - buffer
		3 - file path
		...
	"""

	if isinstance(source, bytes):
		return 1, source

	elif hasattr(source, 'read'):
		return 2, source.read()

	else:
		return 3, open(source, 'rb').read()

def write_content(content: str | bytes, output) -> int:
	_, content = get_content(content)

	if hasattr(output, 'write'):
		return output.write(content)
	
	else:
		with open(output, 'wb') as f:
			f.write(content)

def make_tar(
	source,
	output,
	ignore_errors = PermissionError,
	in_memory = False
) -> str | bytes:

	import tarfile, os

	if in_memory:
		import io
		stream = io.BytesIO()

	with tarfile.open(
		output, "w",
		fileobj = None if not in_memory else stream
	) as tar:

		if os.path.isfile(source):
			tar.add(source, arcname = os.path.basename(source))

		else:
			for root, _, files in os.walk(source):
				for file in files:

					file_path = os.path.join(root, file)
					file_rel_path = os.path.relpath(file_path, source)

					with open(file_path, 'rb') as file_buffer:
						try:
							file_buffer.peek()

						except ignore_errors:
							continue

						info = tar.gettarinfo(arcname=file_rel_path, fileobj=file_buffer)
						tar.addfile(info, file_buffer)

	if in_memory:
		stream.seek(0)
		return stream.read()

	return output

def compress(
	source: bytes | str,
	algorithm: Algorithms = 'gzip',
	output = None,
	ignored_exceptions: type | tuple[type] = PermissionError,
	tar_in_memory = True,
	tar_if_file = False,
	compression_level = None,
	check_algorithm_support = False,
	**kwargs
) -> int:
	
	import os

	algorithm_map = {
		'gzip': (lambda: __import__('gzip').compress, {}, {'compression_level': 'compresslevel'}),
		'bzip2': (lambda: __import__('bz2').compress, {}, {'compression_level': 'compresslevel'}),
		'lzma': (lambda: __import__('lzma').compress, {}, {'compression_level': 'preset'}),
		'lzma2': (lambda: __import__('lzma').compress, lambda: {'format': __import__('lzma').FORMAT_XZ}, {'compression_level': 'preset'}),
		'deflate': (lambda: __import__('zlib').compress, {}, {'compression_level': 'level'}),
		'lz4': (lambda: __import__('lz4.frame').frame.compress, {}, {'compression_level': 'compression_level'}),
		'zstd': (lambda: __import__('zstandard').compress, {}, {'compression_level': 'level'}),
		'brotli': (lambda: __import__('brotli').compress, lambda: {'mode': __import__('brotli').MODE_GENERIC}, {'compression_level': 'quality'}),
	}

	a_compress, additional_args, slug_map = algorithm_map[algorithm]

	if check_algorithm_support:
		if not algorithm: return

		try:
			a_compress()
			return True

		except ImportError:
			return False

	a_compress = a_compress()

	if callable(additional_args):
		additional_args = additional_args()

	if compression_level:
		compression_slug = slug_map.get('compression_level')

		if compression_slug:
			additional_args[compression_slug] = compression_level

	additional_args.update(kwargs)

	is_out_buffer = hasattr(output, 'write')
	tar_in_memory = is_out_buffer or tar_in_memory

	if not output:
		output = os.path.basename(os.path.abspath(source)) + f'.{algorithm}'

	if isinstance(source, bytes):
		compressed = a_compress(
			source, **additional_args
		)

	else:
		if not tar_if_file and os.path.isfile(source):
			with open(source, 'rb') as f:
				compressed = a_compress(f.read(), **additional_args)

		else:
			tar_path = '' if tar_in_memory else output + '.tar'
			stream = make_tar(source, tar_path, ignored_exceptions, tar_in_memory)
			compressed = a_compress(stream if tar_in_memory else tar_path, **additional_args)

			if not tar_in_memory:
				os.remove(tar_path)

	if is_out_buffer:
		return output.write(compressed)

	with open(output, 'wb') as f:
		return f.write(compressed)

def is_brotli(data: bytes) -> bool:
	'''
	Don't use this
	'''

	if not isinstance(data, bytes):
		return False

	if len(data) < 4:
		return False

	first_byte = data[0]

	wbits = first_byte & 0x0F
	header_bits = (first_byte >> 4) & 0x0F

	if 10 >= wbits >= 24:
		return False

	if header_bits > 0x0D:
		return False

	return True

def decompress(
	source: bytes | str,
	algorithm: Algorithms = None,
	output = None,
	**kwargs
):
	algorithm_map = {
		'gzip': (lambda: __import__('gzip').decompress, b'\x1f\x8b\x08'),
		'bzip2': (lambda: __import__('bz2').decompress, b'BZh'),
		'lzma': (lambda: __import__('lzma').decompress, b'\xfd7zXZ'),
		'deflate': (lambda: __import__('zlib').decompress, b'x'),
		'lz4': (lambda: __import__('lz4.frame').frame.decompress, b'\x04\x22\x4d\x18'),
		'zstd': (lambda: __import__('zstandard').decompress, b'\x28\xb5\x2f\xfd'),
		'brotli': (lambda: __import__('brotli').decompress, is_brotli),
	}

	type, content = get_content(source)

	if not algorithm:
		for algo, (a_decompress, start_bytes) in algorithm_map.items():
			if callable(start_bytes):
				algorithm = algo if start_bytes(content) else None

			elif content.startswith(start_bytes):
				algorithm = algo
				break

	if not algorithm:
		raise ValueError(f"Couldn't detect algorithm for decompression, start bytes: {content[:10]}")

	a_decompress = algorithm_map[algorithm][0]()
	decompressed = a_decompress(content, **kwargs)

	if hasattr(output, 'write'):
		return output.write(decompressed)
	
	if not output:
		output = source.rsplit('.', 1)[0]
	
	import tarfile, io
	stream = io.BytesIO(decompressed)

	if tarfile.is_tarfile(stream):
		with tarfile.open(fileobj=stream) as tar:
			tar.extractall(output)
	
	else:
		with open(output, 'wb') as f:
			f.write(decompressed)

	return output