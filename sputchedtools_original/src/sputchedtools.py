from typing import Coroutine, Literal, Any, Callable, Union, Optional, IO
from collections.abc import Iterator, Iterable
from dataclasses import dataclass

ReturnTypes = Literal['ATTRS', 'charset', 'close', 'closed', 'connection', 'content', 'content_disposition', 'content_length', 'content_type', 'cookies', 'get_encoding', 'headers', 'history', 'host', 'json', 'links', 'ok', 'raise_for_status', 'raw_headers', 'read', 'real_url', 'reason', 'release', 'request_info', 'start', 'status', 'text', 'url', 'url_obj', 'version', 'wait_for_close']
Algorithms = Literal['gzip', 'bzip2', 'lzma', 'lzma2', 'deflate', 'lz4', 'zstd', 'brotli']
RequestMethods = Literal['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE']

algorithms = ['gzip', 'bzip2', 'lzma', 'lzma2', 'deflate', 'lz4', 'zstd', 'brotli']

__version__ = '0.30.6'

# ----------------CLASSES-----------------

@dataclass
class TimerLap:
	start: float
	end: float
	name: str = ""

class Timer:
	"""
	Code execution Timer

	Format variables:
		%s  - seconds
		%ms - milliseconds
		%us - microseconds
		%n  - lap name (if using laps)

	"""

	def __init__(
		self,
		echo_fmt: Union[str, Literal[False]] = "Taken time: %s",
		append_fmt: bool = True
	):

		from time import perf_counter

		self.time = perf_counter
		self.echo_fmt = echo_fmt
		self.append_fmt = append_fmt
		self.time_fmts = ['s', 'ms', 'us']
		self.mps = [1] + [1000**i for i in range(1, len(self.time_fmts))]
		self.laps: list[TimerLap] = []

	def __enter__(self) -> 'Timer':
		self._start_time = self._last_lap = self.time()
		return self

	def lap(self, name: str = "") -> float:
		now = self.time()
		lap_time = TimerLap(self._last_lap, now, name)
		self.laps.append(lap_time)
		self._last_lap = now

		return now - self._last_lap

	def format_output(self, seconds: float) -> str:
		fmt = self.echo_fmt

		for mp, unit in zip(self.mps, self.time_fmts):
			fmt = fmt.replace(f"%{unit}", f"{num.decim_round(seconds * mp)}{unit}" if self.append_fmt else '', 1)

		return fmt

	def __exit__(self, *exc):
		end_time = self.time()
		self.diff = end_time - self._start_time

		if self.echo_fmt:
			print(self.format_output(self.diff))

		return self.diff

	async def __aenter__(self) -> 'Timer':
		return self.__enter__()

	async def __aexit__(self, *exc):
		return self.__exit__(*exc)

class NewLiner:

	"""
	Simply adds a new line before and after the block of code

	"""

	def __enter__(self):
		print(flush = True)

	def __exit__(self, *exc):
		print(flush = True)

class ProgressBar:
	def __init__(
		self,
		iterator: Optional[Union[Iterator[Any], Iterable[Any]]] = None,
		text: str = 'Processing...',
		task_amount: Optional[int] = None,
		final_text: str = "Done\n",
		tasks: Optional[Iterable[Any]] = None
	):

		if iterator and not isinstance(iterator, Iterator):
			if not hasattr(iterator, '__iter__'):
				raise AttributeError(f"Provided object is not Iterable\n\nType: {type(iterator)}\nAttrs: {dir(iterator)}")
			self.iterator = iterator.__iter__()
		else:
			self.iterator = iterator

		if task_amount is None:
			if iterator and not hasattr(iterator, '__len__'):
				raise AttributeError(f"You didn't provide task_amount for Iterator or object with no __len__ attribute")
			elif tasks and not hasattr(tasks, '__len__'):
				raise AttributeError(f"You didn't provide task_amount for Async Iterator\n\nType: {type(tasks)}\nAttrs: {dir(tasks)}")
			elif iterator:
				self.task_amount = iterator.__len__()
			elif tasks:
				self.task_amount = tasks.__len__()
		else:
			self.task_amount = task_amount

		import asyncio
		from sys import stdout

		self.asyncio = asyncio
		self.flush = lambda k: stdout.write(k); stdout.flush()
		self._text = text
		self.completed_tasks = 0
		self.final_text = final_text

		if tasks:
			if hasattr(tasks, '__aiter__'):
				self.tasks = tasks
			else:
				raise ValueError("tasks must be an async iterator or None")

	@property
	def text(self) -> str:
		return self._text

	@text.setter
	def text(self, value: str):
		val_len = len(value)
		text_len = len(self.__text)
		self._text = value + ' ' * (text_len - val_len if text_len > val_len else 0)

	def __iter__(self) -> 'ProgressBar':
		self.update(0)
		return self

	def __next__(self) -> Any:
		try:
			item = next(self.iterator)
			self.update()
			return item
		except StopIteration:
			self.finish()
			raise

	async def __aiter__(self) -> 'ProgressBar':
		if not hasattr(self, 'tasks'):
			raise ValueError("You didn't specify coroutine iterator")
		self.update(0)
		return self

	async def __anext__(self) -> Any:
		try:
			task = await self.tasks.__anext__()
			await self.update()
			return task
		except StopAsyncIteration:
			await self.finish()
			raise

	def __enter__(self) -> 'ProgressBar':
		self.update(0)
		return self

	async def __aenter__(self) -> 'ProgressBar':
		self.update(0)
		return self

	def update(self, increment: int = 1):
		self.completed_tasks += increment
		self.print_progress()

	async def aupdate(self, increment: int = 1):
		self.completed_tasks += increment
		self.print_progress()

	def print_progress(self):
		self.flush(f'\r{self._text} {self.completed_tasks}/{self.task_amount}')

	async def gather(self, tasks: Iterable[Coroutine]) -> list[Any]:
		self.update(0)
		results = []

		for task in self.asyncio.as_completed(tasks):
			result = await task
			await self.aupdate()
			results.append(result)

		self.finish()
		return results

	async def as_completed(self, tasks: Iterable[Coroutine]):
		self.update(0)

		for task in self.asyncio.as_completed(tasks):
			result = await task
			await self.aupdate()
			yield result

		self.finish()

	def finish(self):
		self.finish_message = f'\r{self._text} {self.completed_tasks}/{self.task_amount} {self.final_text}'
		self.flush(self.finish_message)

	def __exit__(self, *exc):
		self.finish()

	async def __aexit__(self, *exc):
		self.finish()

class Anim:
	def __init__(
		self,
		prepend_text: str = '', append_text: str = '',
		just_clear_char: bool = True,
		clear_on_exit: bool = False,
		delay: float = 0.03,
		manual_update: bool = False,
		chars: Optional[Iterable[Any]] = None
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

	def get_line(self) -> str:
		return f'\r{self.prepend_text}{self.char}{self.append_text}'.encode('utf-8').decode('utf-8')

	@classmethod
	def get_max_char_len(cls, chars: Iterable[Any]) -> int:
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
	def adapt_chars_spaces(cls, chars: Iterable[Any]) -> Iterable[Any]:
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

	def set_chars(self, new_chars: Iterable[Any]):
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

	def __enter__(self) -> 'Anim':
		if self.manual_update:
			self.update()

		else:
			self.thread = self.Thread(target=self.anim)
			self.thread.daemon = True
			self.thread.start()

		return self

	def __exit__(self, *exc):
		if not self.manual_update:
			self.done = True
			self.thread.join()

class Callbacks:
	direct = 1
	toggle = 2
	callable = 3

class Option:
	def __init__(
		self,
		name: str,
		value: str,
		required: bool = False,
		callback: Callbacks = Callbacks.direct,
		toggled: bool = False
	):
		self.name = name
		self.value = value
		self.required = required
		self.callback = callback
		self.toggled = toggled

class Config:
	def __init__(
		self,
		options: list[Option],
		per_page: int = 9,
		callback_option_name: bool = True
	):
		self.per_page = per_page
		self.cbname = callback_option_name
		self.oplen = len(options)

		self.orig_options = options
		self.options = [options[i : i + per_page] for i in range(0, self.oplen, per_page)]
		self.page_amount = len(self.options)

		from sys import platform
		if 'win' in platform or 'nt' in platform:
			self.cli = self.win_cli
		elif platform == 'linux' or 'darwin' in platform:
			self.cli = self.unix_cli
		else:
			self.cli = self.custom_cli

	def set_page(self, index: int):
		self.index = index % self.page_amount

	def add_page(self, amount: int = 1):
		new_index = self.index + amount
		self.index = new_index % self.page_amount

	def win_cli(self) -> dict[str, str]:
		import msvcrt
		self.index = 0
		selected_option = 0
		editing = False
		new_value = ''
		cursor_pos = 0

		while True:
			page = self.index + 1
			options = self.options[self.index]
			options_repr = []

			for i, option in enumerate(options):
				prefix = '>' if i == selected_option else ' '
				toggle = f" [{'*' if option.toggled else ' '}]" if option.callback == Callbacks.toggle else " *" if option.required else ""

				if editing and i == selected_option:
					value = new_value[:cursor_pos] + '█' + new_value[cursor_pos:]
				else:
					value = option.value

				options_repr.append(f'{prefix} [{i + 1}]{toggle} {option.name} - {value}')

			options_repr = '\n'.join(options_repr)
			options_repr += f'\n\nPage {page}/{self.page_amount}'

			print('\033[2J\033[H' + options_repr, flush = True)  # Clear screen and print options

			if editing:
				key = msvcrt.getch()
				if key == b'\r':  # Enter - save value
					options[selected_option].value = new_value
					editing = False
				elif key == b'\x1b':  # Escape - cancel editing
					editing = False
					new_value = ''
					cursor_pos = 0
				elif key == b'\xe0':  # Special keys
					key = msvcrt.getch()
					if key == b'K':  # Left arrow
						cursor_pos = max(0, cursor_pos - 1)
					elif key == b'M':  # Right arrow
						cursor_pos = min(len(new_value), cursor_pos + 1)
					elif key == b'G':  # Home
						cursor_pos = 0
					elif key == b'O':  # End
						cursor_pos = len(new_value)
				elif key == b'\x08':  # Backspace
					if cursor_pos > 0:
						new_value = new_value[:cursor_pos-1] + new_value[cursor_pos:]
						cursor_pos -= 1
				else:
					try:
						char = key.decode('utf-8')
						new_value = new_value[:cursor_pos] + char + new_value[cursor_pos:]
						cursor_pos += 1
					except UnicodeDecodeError:
						pass
				continue

			key = msvcrt.getch()

			if key == b'\xe0':  # Special keys prefix
				key = msvcrt.getch()
				if key == b'H':  # Up arrow
					selected_option = (selected_option - 1) % len(options)
				elif key == b'P':  # Down arrow
					selected_option = (selected_option + 1) % len(options)
				elif key == b'M':  # Right arrow
					self.add_page(1)
					selected_option = 0
				elif key == b'K':  # Left arrow
					self.add_page(-1)
					selected_option = 0

			elif key == b'\r':  # Enter key
				option = options[selected_option]
				if option.callback == Callbacks.toggle:
					option.toggled = not option.toggled
				elif option.callback == Callbacks.callable:
					if self.cbname:
						option.callback(option.name)
					else:
						option.callback(self.index * self.per_page + selected_option)
				elif option.callback == Callbacks.direct:
					editing = True
					new_value = option.value
					cursor_pos = len(new_value)

			elif key == b'p':
				inp = input('Page: ')

				try:
					page = int(inp) - 1
					self.set_page(page)
					selected_option = 0

				except ValueError:
					pass

			elif key.isdigit():  # Number keys
				num = int(key.decode()) - 1
				if 0 <= num < len(options):
					selected_option = num

			elif key == b'w': # Move up
				selected_option = (selected_option - 1) % len(options)

			elif key == b's': # Move down
				selected_option = (selected_option + 1) % len(options)

			elif key == b'a': # Previous page
				self.add_page(-1)
				selected_option = 0

			elif key == b'd': # Next page
				self.add_page(1)
				selected_option = 0

			elif key == b'q':  # Quit
				break

			elif key == b'\x1b':  # Escape key
				break

		# Return all options
		print('\033[2J\033[H', flush = True, end = '')
		return {option.name: option.value for option in self.orig_options}

	def unix_cli(self) -> dict[str, str]:

		import sys, tty, termios, os

		def getch():
			fd = sys.stdin.fileno()
			old_settings = termios.tcgetattr(fd)
			try:
				tty.setraw(sys.stdin.fileno())
				ch = sys.stdin.read(1)
				if ch == '\x1b':  # escape sequences
					ch2 = sys.stdin.read(1)
					if ch2 == '[':
						ch3 = sys.stdin.read(1)
						return f'\x1b[{ch3}'
				return ch
			finally:
				termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

		clear = lambda: os.system('clear')
		self.index = 0
		selected_option = 0
		editing = False
		new_value = ''
		cursor_pos = 0

		while True:
			clear()
			page = self.index + 1
			options = self.options[self.index]
			options_repr = []

			for i, option in enumerate(options):
				prefix = '>' if i == selected_option else ' '
				toggle = f" [{'*' if option.toggled else ' '}]" if option.callback == Callbacks.toggle else " *" if option.required else ""

				if editing and i == selected_option:
					value = new_value[:cursor_pos] + '█' + new_value[cursor_pos:]
				else:
					value = option.value

				options_repr.append(f'{prefix} [{i + 1}]{toggle} {option.name} - {value}')

			options_repr = '\n'.join(options_repr)
			options_repr += f'\n\nPage {page}/{self.page_amount}'
			print(options_repr)

			key = getch()

			if editing:
				if key == '\r':  # Enter
					options[selected_option].value = new_value
					editing = False
				elif key == '\x1b':  # Escape
					editing = False
					new_value = ''
					cursor_pos = 0
				elif key == '\x1b[D':  # Left arrow
					cursor_pos = max(0, cursor_pos - 1)
				elif key == '\x1b[C':  # Right arrow
					cursor_pos = min(len(new_value), cursor_pos + 1)
				elif key == '\x7f':  # Backspace
					if cursor_pos > 0:
						new_value = new_value[:cursor_pos-1] + new_value[cursor_pos:]
						cursor_pos -= 1
				elif len(key) == 1 and 32 <= ord(key) <= 126:  # Printable chars
					new_value = new_value[:cursor_pos] + key + new_value[cursor_pos:]
					cursor_pos += 1
				continue

			if key == '\x1b[A':  # Up arrow
				selected_option = (selected_option - 1) % len(options)
			elif key == '\x1b[B':  # Down arrow
				selected_option = (selected_option + 1) % len(options)
			elif key == '\x1b[C':  # Right arrow
				self.add_page(1)
				selected_option = 0
			elif key == '\x1b[D':  # Left arrow
				self.add_page(-1)
				selected_option = 0
			elif key == '\r':  # Enter
				option = options[selected_option]
				if option.callback == Callbacks.toggle:
					option.toggled = not option.toggled
				elif option.callback == Callbacks.callable:
					if self.cbname:
						option.callback(option.name)
					else:
						option.callback(self.index * self.per_page + selected_option)
				elif option.callback == Callbacks.direct:
					editing = True
					new_value = option.value
					cursor_pos = len(new_value)
			elif key in ('q', '\x1b'):  # q or Escape
				break
			elif key == 'p':  # Page select
				print("\nPage: ", end='', flush=True)
				try:
					page = int(input()) - 1
					self.set_page(page)
					selected_option = 0
				except ValueError:
					pass
			elif key.isdigit():  # Number selection
				num = int(key) - 1
				if 0 <= num < len(options):
					selected_option = num
			elif key == 'w':  # Alternative up
				selected_option = (selected_option - 1) % len(options)
			elif key == 's':  # Alternative down
				selected_option = (selected_option + 1) % len(options)
			elif key == 'a':  # Alternative left
				self.add_page(-1)
			elif key == 'd':  # Alternative right
				self.add_page(1)

		# Return all options
		clear()
		return {option.name: option.value for option in self.orig_options}

	def custom_cli(self) -> dict[str, str]:
		self.index = 0

		while True:
			page = self.index + 1
			options = self.options[self.index]
			options_repr = '\n'.join(f'[{i + 1}]{f" [{'*' if option.toggled else ' '}]" if option.callback == Callbacks.toggle else " *" if option.required else ""} {option.name} - {option.value}' for i, option in enumerate(options))
			options_repr += f'\n\nPage {page}/{self.page_amount}'
			options_repr += '\nOption: '

			with NewLiner():
				inp = input(options_repr)

			if inp.isdigit():
				num = int(inp) - 1
				if 0 <= num < len(options):
					option = options[num]
					if option.callback == Callbacks.toggle:
						option.toggled = not option.toggled
					elif option.callback == Callbacks.callable:
						if self.cbname:
							option.callback(option.name)
						else:
							option.callback(self.index * self.per_page + num)
					elif option.callback == Callbacks.direct:
						new_value = input(f"New value for {option.name}: ")
						option.value = new_value

			elif inp == 'p':
				page = input("Page: ")
				try:
					page = int(page) - 1
					self.set_page(page)
				except ValueError:
					pass

			elif inp == 'a':
				self.add_page(-1)

			elif inp == 'd':
				self.add_page(1)

			elif inp == 'q':
				break

		# Return all options
		print()
		return {option.name: option.value for option in self.orig_options}

class aio:

	"""
	Methods:
		- aio.get() - 'GET' wrapper for aio.request
		- aio.post() - 'POST' wrapper for aio.request
		- aio.request() - ikyk
		- aio.open() - aiofiles.open() method
		- aio.sem_task() - uses received semaphore to return function execution result
	"""

	@staticmethod
	async def request(
		method: RequestMethods,
		url: str,
		toreturn: Union[ReturnTypes, Iterable[ReturnTypes]] = 'text',
		session: Optional[Any] = None,
		raise_exceptions: bool = False,
		httpx: bool = False,
		niquests: bool = False,
		**kwargs,
	) -> list[Any]:

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

			elif niquests:
				import niquests
				ses = niquests.AsyncSession()

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
					if raise_exceptions:
						raise

					result = None

				return_items.append(result)

		except asyncio.TimeoutError:
			return_items.insert(0, 0)

		except BaseException:
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
	async def get(
		url: str,
		toreturn: Union[ReturnTypes, Iterable[ReturnTypes]] = 'text',
		session: Optional[Any] = None,
		raise_exceptions: bool = False,
		httpx: bool = False,
		niquests: bool = False,
		**kwargs,
	) -> list[Any]:
		return await aio.request('GET', url, toreturn, session, raise_exceptions, httpx, niquests, **kwargs)

	@staticmethod
	async def post(
		url: str,
		toreturn: Union[ReturnTypes, Iterable[ReturnTypes]] = 'text',
		session: Optional[Any] = None,
		raise_exceptions: bool = False,
		httpx: bool = False,
		niquests: bool = False,
		**kwargs,
	) -> list[Any]:
		return await aio.request('POST', url, toreturn, session, raise_exceptions, httpx, niquests, **kwargs)

	@staticmethod
	async def open(
		file: str,
		action: str = 'read',
		mode: str = 'r',
		content: Optional[Any] = None,
		**kwargs
	) -> Union[int, str, bytes]:

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
		func: Callable[..., Any],
		*args, **kwargs
	) -> Any:
		async with semaphore:
			return await func(*args, **kwargs)

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

	suffixes: list[Union[str, int]] = ['', 'K', 'M', 'B', 'T', 1000]
	fileSize_suffixes: list[Union[str, int]] = [' B', ' KB', ' MB', ' GB', ' TB', 1024]
	sfx = fileSize_suffixes

	deshorteners: dict[str, int] = {'k': 10**3, 'm': 10**6, 'b': 10**9, 't': 10**12}
	decims: list[int] = [1000, 100, 10, 5] # List is iterated using enumerate(), so by each iter. decimal amount increases by 1 (starting from 0)

	@staticmethod
	def shorten(
		value: Union[int, float],
		decimals: int = -1,
		suffixes: Optional[list[Union[str, int]]] = None
	) -> str:

		"""
		Accepts:

			- value: int - big value
			- decimals: int = -1 - round digit amount

			- suffixes: list[str] - Use case: File Size calculation: pass num.fileSize_suffixes

		Returns:
			Shortened float or int-like str

		"""

		absvalue = abs(value)
		suffixes: list[str] = suffixes or num.suffixes
		magnitude = suffixes[-1]

		for i, suffix in enumerate(suffixes[:-1]):
			unit = magnitude ** i
			if absvalue < unit * magnitude or i == len(suffixes) - 1:
				value /= unit
				formatted: str = num.decim_round(value, decimals, decims = [100, 10, 1])
				return formatted + suffix

	@staticmethod
	def unshorten(
		value: str,
		_round: bool = True
	) -> Union[float, str]:

		"""
		Accepts:

			- value: str - int-like value with shortener at the end
			- _round: bool - wether returned value should be rounded to integer

		Returns:
			Unshortened float

		"""

		mp = value[-1].lower()
		number = value[:-1]

		try:
			number = float(number)
			mp = num.deshorteners[mp]

			if _round:
				unshortened = round(number * mp)

			else:
				unshortened = number * mp

			return unshortened

		except (ValueError, KeyError):
			return float(value) # Raises ValueError if value is not a number

	@staticmethod
	def decim_round(
		value: float,
		decimals: int = -1,
		round_if_num_gt_1: bool = True,
		precission: int = 20,
		decims: Optional[list[int]] = None
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
	def beautify(value: Union[int, float], decimals: int = -1, precission: int = 20) -> str:
		return num.shorten(float(num.decim_round(value, decimals, precission = precission)), decimals)

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
		token_contract,
		sender: str,
		period: Union[float, int] = 10,
		multiply_by: float = 1.0
	):
		dead = '0x000000000000000000000000000000000000dEaD'

		while True:
			self.gas = round(token_contract.functions.transfer(dead, 0).estimate_gas({'from': sender}) * multiply_by)
			self.sleep(period)

	def gas_price_monitor(
		self,
		period: Union[float, int] = 10,
		multiply_by: float = 1.0
	):

		while True:
			self.gas_price = round(self.web3.eth.gas_price * multiply_by)
			self.sleep(period)

	def nonce_monitor(
		self,
		address: str,
		period: Union[float, int] = 10
	):

		while True:
			self.nonce = self.web3.eth.get_transaction_count(address)
			self.sleep(period)

	def get_nonce(self, address: str) -> int:
		return self.web3.eth.get_transaction_count(address)

# -------------MINECRAFT-VERSIONING-LOL-------------

class MC_VersionList:
	def __init__(self, versions: list[str], indices: list[int]):
		self.length = len(versions)

		if self.length != len(indices):
			raise ValueError

		self.versions = versions
		self.indices = indices
		# self.map = {version: index for version, index in zip(versions, indices)}

class MC_Versions:
	def __init__(self):
		from re import findall
		self.findall = findall
		self.manifest_url = 'https://launchermeta.mojang.com/mc/game/version_manifest.json'

		# Pattern for a single version
		version_pattern = r'1\.\d+(?:\.\d+){0,1}'
		# Pattern for a single version or a version range
		item_pattern = rf'{version_pattern}(?:\s*-\s*{version_pattern})*'
		# Full pattern allowing multiple items separated by commas
		self.full_pattern = rf'{item_pattern}(?:,\s*{item_pattern})*'

		self.release_versions = []

	@classmethod
	async def init(cls):
		self = cls()
		await self.fetch_version_manifest()
		self.latest = self.release_versions[-1]
		return self

	def sort(self, mc_vers: Iterable[str]) -> MC_VersionList:
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

	def get_range(self, mc_vers: Union[MC_VersionList, Iterable[str]]) -> str:
		if isinstance(mc_vers, Iterable):
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

	def get_list(self, mc_vers: str) -> list[str]:
		return self.findall(self.full_pattern, mc_vers)

	async def fetch_version_manifest(self):
		response = await aio.get(self.manifest_url, toreturn = ['json', 'status'])
		manifest_data, status = response

		if status != 200 or not isinstance(manifest_data, dict):
			raise ConnectionError(f"Couldn't fetch minecraft versions manifest from `{self.manifest_url}`\nStatus: {status}")

		self.release_versions: list[str] = []

		for version in manifest_data['versions']:
			if version['type'] == 'release':
				self.release_versions.append(version['id'])

		self.release_versions.reverse() # Ascending

	def is_version(self, version: str) -> bool:
		try:
			self.release_versions.index(version)
			return True
		except ValueError:
			return False

# ----------------METHODS----------------

def enhance_loop() -> bool:
	from sys import platform
	import asyncio

	try:

		if 'win' in platform:
			import winloop # type: ignore
			asyncio.set_event_loop_policy(winloop.EventLoopPolicy())

		else:
			import uvloop # type: ignore
			asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

		return True

	except ImportError:
		return False

def get_content(source: Union[str, bytes, IO[bytes]]) -> tuple[Optional[int], Optional[bytes]]:
	"""
	Returns source byte content
	Source can be either a file_path, readable buffer or just bytes

	First tuple object is source type:
		1 - bytes
		2 - readable buffer
		3 - file path
		4 - folder path (str)
		None - unknown
		...

	"""

	if isinstance(source, bytes):
		return 1, source

	elif hasattr(source, 'read'):
		return 2, source.read()

	else:
		import os

		if os.path.isfile(source):
			return 3, open(source, 'rb').read()

		elif os.path.isdir(source):
			return 4, source

		return None, None

def write_content(content: Union[str, bytes], output: Union[Literal[False], str, IO[bytes]]) -> Union[int, bytes]:
	_, content = get_content(content)

	if hasattr(output, 'write'):
		return output.write(content)

	elif output is False:
		return content

	else:
		with open(output, 'wb') as f:
			return f.write(content)

def make_tar(
	source: str,
	output: str,
	ignore_errors: Union[type, tuple[type]] = PermissionError,
	in_memory: bool = False
) -> Union[str, bytes]:

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

					try:
						with open(file_path, 'rb') as file_buffer:
							file_buffer.peek()

							info = tar.gettarinfo(arcname=file_rel_path, fileobj=file_buffer)
							tar.addfile(info, file_buffer)

					except ignore_errors:
						continue

	if in_memory:
		stream.seek(0)
		return stream.read()

	return output

def compress(
	source: Union[bytes, str, IO[bytes]],
	algorithm: Algorithms = 'gzip',
	output: Union[Literal[False], str, IO[bytes]] = None,
	ignored_exceptions: Union[type, tuple[type]] = (PermissionError, OSError),
	tar_in_memory: bool = True,
	tar_if_file: bool = False,
	compression_level: Optional[int] = None,
	check_algorithm_support: bool = False,
	**kwargs
) -> Union[int, bytes]:

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

		except:# ImportError
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
	import os

	if not output:
		if isinstance(source, str) and os.path.exists(source):
			output = os.path.basename(os.path.abspath(source)) + f'.{algorithm}'
		else:
			output = False

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
			if isinstance(output, str) and os.path.exists(output):
				os.remove(output)

			stream = make_tar(source, tar_path, ignored_exceptions, tar_in_memory)
			compressed = a_compress(stream if tar_in_memory else tar_path, **additional_args)

			if not tar_in_memory:
				os.remove(tar_path)

	return write_content(compressed, output)

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
	source: Union[bytes, str, IO[bytes]],
	algorithm: Optional[Algorithms] = None,
	output: Optional[Union[Literal[False], str, IO[bytes]]] = None,
	**kwargs
) -> Union[int, str, bytes]:

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

	if output is None:
		output = source.rsplit('.', 1)[0] if isinstance(source, str) else False

	if output is False:
		return decompressed

	elif hasattr(output, 'write'):
		return output.write(decompressed)

	# Assuming output is a path
	import tarfile, io

	stream = io.BytesIO(decompressed)

	if tarfile.is_tarfile(stream):
		import sys

		if sys.version_info >= (3, 12):
			tarfile.open(fileobj=stream).extractall(output, filter = 'data')
		else:
			tarfile.open(fileobj=stream).extractall(output)

	else:
		with open(output, 'wb') as f:
			f.write(decompressed)

	return output