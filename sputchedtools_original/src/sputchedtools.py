from typing import Coroutine, Literal, Iterable, Iterator, Any, Callable, Union, Optional, IO, TYPE_CHECKING, Protocol, TypeVar

if TYPE_CHECKING:
	from _typeshed import OpenTextMode

ReturnTypes = Literal['response', 'content', 'text', 'json', 'read', 'status', 'real_url', 'ATTRS', 'charset', 'close', 'closed', 'connection', 'content_disposition', 'content_length', 'content_type', 'cookies', 'get_encoding', 'headers', 'history', 'host', 'links', 'method', 'ok', 'raise_for_status', 'raw_headers', 'reason', 'release', 'request_info', 'start', 'url', 'url_obj', 'version', 'wait_for_close']
Algorithms = Literal['gzip', 'bzip2', 'lzma', 'lzma2', 'deflate', 'lz4', 'zstd', 'brotli']
RequestMethods = Literal['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE']
Formattable = str
ActionModes = Literal['write', 'read']
Number = Union[int, float]

T = TypeVar('T')
class Falsy(Protocol[T]):
	def __bool__(self) -> bool: ...

algorithms = ['gzip', 'bzip2', 'lzma', 'lzma2', 'deflate', 'lz4', 'zstd', 'brotli']

__version__ = '0.37.0'

# ----------------CLASSES-----------------
class JSON:
	"""
	Unifies json and orjson libraries
	If `orjson` not installed, `ordumps` and `orloads` will be replaced with json's
	Ensure you properly handle JSON.DUMP_TYPE / JSON.BYTE_SUFFIX (for non-write modes)
	"""

	def __init__(self):
		import json

		try:
			import orjson
			self.orjson = orjson

			def ordumps(obj: dict, indent: bool = False, **kwargs) -> bytes:
				return orjson.dumps(obj, option = orjson.OPT_INDENT_2 if indent else None, **kwargs)
			def orloads(data: bytes, **kwargs) -> dict:
				return orjson.loads(data, **kwargs)

			self.ordumps = ordumps
			self.orloads = orloads

		except ImportError:
			self.orjson = None

			def ordumps(obj: dict, indent: bool = False, **kwargs) -> bytes:
				return json.dumps(obj, indent = 2 if indent else None, **kwargs).encode('utf-8')
			def orloads(data: str, **kwargs) -> dict:
				return json.loads(data, **kwargs)

			self.ordumps = ordumps
			self.orloads = orloads

		self.json = json
		self.dumps = json.dumps
		self.loads = json.loads
		self.detect_encoding = json.detect_encoding

		self.DecodeError = json.JSONDecodeError
		self.EncodeError = TypeError # orjson.JSONEncodeError

		self.Decoder = json.JSONDecoder
		self.Encoder = json.JSONEncoder

		self.stringify = self.dumps
		self.parse = self.orloads

class TimerLap:
	def __init__(self,
		start: float,
		end: float,
		name: Optional[str]
	):
		self.start = start
		self.end = end
		self.diff = self.elapsed = end - start
		self.name = name

	def __repr__(self) -> str:
		return f'TimerLap(start={self.start}, end={self.end}, diff={self.diff}, name={self.name})'

class Timer:
	time_fmts = ['s', 'ms', 'us']
	diff: float
	elapsed: float

	"""
	Code execution Timer

	Format variables:
		%a - auto, best-suited format
		%s  - seconds
		%ms - milliseconds
		%us - microseconds

	"""

	def __init__(
		self,
		fmt: Optional[Formattable] = "Taken time: %a",
		echo: bool = True,
		time_fmts: Optional[list[str]] = None,
	):

		from time import perf_counter

		self.time = perf_counter
		self.fmt = fmt
		self.echo = echo
		self.laps: list[TimerLap] = []
		if time_fmts:
			self.time_fmts = time_fmts

	def __enter__(self) -> 'Timer':
		self.start_time = self.last_lap = self.time()
		return self

	def lap(self, name: str = None):
		now = self.time()
		self.laps.append(TimerLap(self.last_lap, now, name))
		self.last_lap = now

	@classmethod
	def format_output(cls, seconds: Number, fmt: Formattable = '%a') -> str:

		# Handle auto format first
		if '%a' in fmt:
			val = seconds
			if seconds >= 1:
				unit = 's'
			elif seconds >= 0.001:
				val *= 1000
				unit = 'ms'
			else:
				val *= 1000000
				unit = 'us'

			fmt = fmt.replace('%a', f'{num.decim_round(val)}{unit}', 1)

		# Handle remaining formats
		for mp, unit in zip([1, 1000, 1000000], cls.time_fmts):
			fmt = fmt.replace(f"%{unit}", f"{num.decim_round(seconds * mp)}{unit}", 1)

		return fmt

	def format(self) -> str:
		return self.format_output(self.diff, self.fmt)

	def __exit__(self, *exc):
		self.end_time = self.time()
		self.diff = self.elapsed = self.end_time - self.start_time

		if self.fmt and self.echo:
			print(self.format())

	async def __aenter__(self) -> 'Timer':
		return self.__enter__()

	async def __aexit__(self, *exc):
		self.__exit__(*exc)

class QTimer(Timer):
	"""Quiet Timer variant, with `fmt` set to '%a' by default"""

	def __init__(self, fmt: Formattable = "%a"):
		super().__init__(fmt, False, None)

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
		iterator: Optional[Union[Iterator, Iterable]] = None,
		text: str = 'Processing...',
		final_text: str = "Done\n",
		task_amount: Optional[int] = None,
	):

		if iterator:
			if isinstance(iterator, Iterator):
				self.iterator = iterator

			elif not hasattr(iterator, '__iter__'):
				raise TypeError(f"Provided object is not Iterable, Type: {type(iterator)}")

			else:
				self.iterator = iterator.__iter__()

		else:
			self.iterator = None

		if task_amount is None:
			if not hasattr(iterator, '__len__'):
				raise TypeError(f"You didn't provide task_amount for Iterator with no __len__ attribute")

			self.task_amount = iterator.__len__()

		else:
			self.task_amount = task_amount

		self._text = text
		self.completed_tasks = 0
		self.final_text = final_text

	@property
	def text(self) -> str:
		return self._text

	@text.setter
	def text(self, new_text: str):
		new_text_len = len(new_text)
		old_text_len = len(self._text)
		self._text = new_text + ' ' * (old_text_len - new_text_len if old_text_len > new_text_len else 0)

	def __iter__(self) -> 'ProgressBar':
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

	async def __aiter__(self) -> 'ProgressBar':
		if not hasattr(self, 'iterator'):
			raise ValueError("You didn't specify coroutine iterator. Do: `async for i in ProgressBar(iterator, ...)`")

		self.update(0)
		return self

	async def __anext__(self):
		try:
			result = await self.iterator.__anext__()
			self.update()
			return result

		except StopAsyncIteration:
			await self.finish()
			raise

	def __enter__(self) -> 'ProgressBar':
		self.update(0)
		return self

	async def __aenter__(self) -> 'ProgressBar':
		self.update(0)
		return self

	def update(self, by: int = 1):
		self.completed_tasks += by
		print(f'\r{self._text} {self.completed_tasks}/{self.task_amount}', end = '', flush = True)

	async def gather(self, tasks: Optional[Iterable[Coroutine]] = None) -> list[Any]:
		return [r async for r in self.as_completed(tasks)]

	async def as_completed(self, tasks: Optional[Iterable[Coroutine]] = None):
		tasks = tasks or self.iterator
		if not tasks:
			raise ValueError("You didn't provide any tasks")

		self.update(0)

		for task in self.asyncio.as_completed(tasks):
			result = await task
			self.update()
			yield result

		self.finish()

	def finish(self):
		finish_message = f'\r{self._text} {self.completed_tasks}/{self.task_amount} {self.final_text}'
		print(finish_message, flush = True)

	def __exit__(self, *exc):
		self.finish()

	async def __aexit__(self, *exc):
		self.finish()


class AnimChars:
	cubic_spinner = ('⠉', '⠙', '⠘', '⠰', '⠴', '⠤', '⠦', '⠆', '⠃', '⠋')
	slash = ('\\', '|', '/', '―')
	windows = ("⢀⠀", "⡀⠀", "⠄⠀", "⢂⠀", "⡂⠀", "⠅⠀", "⢃⠀", "⡃⠀", "⠍⠀", "⢋⠀", "⡋⠀", "⠍⠁", "⢋⠁", "⡋⠁", "⠍⠉", "⠋⠉", "⠋⠉", "⠉⠙", "⠉⠙", "⠉⠩", "⠈⢙", "⠈⡙", "⢈⠩", "⡀⢙", "⠄⡙", "⢂⠩", "⡂⢘", "⠅⡘", "⢃⠨", "⡃⢐", "⠍⡐", "⢋⠠", "⡋⢀", "⠍⡁", "⢋⠁", "⡋⠁", "⠍⠉", "⠋⠉", "⠋⠉", "⠉⠙", "⠉⠙", "⠉⠩", "⠈⢙", "⠈⡙", "⠈⠩", "⠀⢙", "⠀⡙", "⠀⠩", "⠀⢘", "⠀⡘", "⠀⠨", "⠀⢐", "⠀⡐", "⠀⠠", "⠀⢀")
	simpleDots = ('.', '..', '...')
	simpleDotsScrolling = (".  ", ".. ", "...", " ..", "  .", "   ")
	circle = ("◜", "◠", "◝", "◟", "◡", "◞")
	clock = ("🕛 ", "🕐 ", "🕑 ", "🕒 ", "🕓 ", "🕔 ", "🕕 ", "🕖 ", "🕗 ", "🕘 ", "🕙 ", "🕚 ")
	clockBackwards = ("🕛 ", "🕚 ", "🕙 ", "🕘 ", "🕗 ", "🕖 ", "🕕 ", "🕔 ", "🕓 ", "🕒 ", "🕑 ", "🕐 ")
	pingpong = ("▐⠂       ▌", "▐⠈       ▌", "▐ ⠂      ▌", "▐ ⠠      ▌", "▐  ⡀     ▌", "▐  ⠠     ▌", "▐   ⠂    ▌", "▐   ⠈    ▌", "▐    ⠂   ▌", "▐    ⠠   ▌", "▐     ⡀  ▌", "▐     ⠠  ▌", "▐      ⠂ ▌", "▐      ⠈ ▌", "▐       ⠂▌", "▐       ⠠▌", "▐       ⡀▌", "▐      ⠠ ▌", "▐      ⠂ ▌", "▐     ⠈  ▌", "▐     ⠂  ▌", "▐    ⠠   ▌", "▐    ⡀   ▌", "▐   ⠠    ▌", "▐   ⠂    ▌", "▐  ⠈     ▌", "▐  ⠂     ▌", "▐ ⠠      ▌", "▐ ⡀      ▌", "▐⠠       ▌")

class Anim:
	def __init__(
		self,
		# Formatting stuff
		prepend_text: str = '', append_text: str = '',
		text_format: str = '{prepend} {char}{append}',
		# This will be appended to the end
		do_timer: Union[Formattable, None] = None, # '(%a)',

		delay: float = 0.08,
		nap_time: float = 0.01,
		chars: Optional[AnimChars] = None,

		# True -> Leave as is (Why)
		# False -> Clear char
		# None -> Whole line
		clear_on_exit: Union[bool, None] = False,
	):
		from threading import Thread
		from shutil import get_terminal_size
		from time import sleep

		self.Thread = Thread
		self.sleep = sleep

		self.prepend_text = prepend_text
		self.append_text = append_text
		self.text_format = text_format
		self.do_timer = do_timer
		self.clear_on_exit = clear_on_exit

		self.chars = chars or  ('⠉', '⠙', '⠘', '⠰', '⠴', '⠤', '⠦', '⠆', '⠃', '⠋')
		self.delay = delay

		self.nap_period = range(int(delay / nap_time))
		self.normal_nap = nap_time
		self.last_nap = delay % nap_time

		self.terminal_width = get_terminal_size().columns
		self.chars = self.adapt_chars_spaces(self.chars)
		self.char = self.chars[0]
		self.done = False

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
	def adapt_chars_spaces(cls, chars: Iterable) -> Iterable:
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

	@property
	def _chars(self, chars: AnimChars):
		self.chars = self.adapt_chars_spaces(chars)

	def set_text(self, new_text: str, prepended: bool = True):
		new_len = len(new_text)
		# if new_len > self.terminal_width:
		# 	return

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

		else:
			self.safe_line_echo(self.get_line())

	def safe_line_echo(self, line: str):
		print(line, end = '', flush = True)

	def get_line(self) -> str:
		line = self.text_format.format(
			prepend=self.prepend_text,
			char=self.char,
			append=self.append_text
		)

		if len(line) >= self.terminal_width:
			line = line[:self.terminal_width - 4] + "..."

		return f"\r{line}"

	def update(self):
		line = self.get_line()
		print(line, end = '', flush = True)

	def _format_final_line(self, timer: Optional[Timer] = None) -> str:
		base = '\r'

		if timer:
			timer.fmt = self.do_timer
			# Format with timer
			return base + self.text_format.format(
				prepend = self.prepend_text,
				char = ' ' * len(self.char),
				append = self.append_text + timer.format_output(timer.diff)
			)

		elif self.clear_on_exit is True:
			# Clear entire line
			return base + ' ' * len(self.get_line()) + base

		elif self.clear_on_exit is False:
			# Clear only animation char
			return base + self.text_format.format(
				prepend = self.prepend_text,
				char = ' ' * len(self.char),
				append = self.append_text
			)

		else:
			# Leave as is
			return base + self.get_line()

	def anim(self):
		with QTimer() as t:
			while not self.done:
				for self.char in self.chars:
					if self.done: break
					self.update()

					for _ in self.nap_period:
						if self.done: break
						self.sleep(self.normal_nap)

					self.sleep(self.last_nap)

		# Format and display final line
		final_line = self._format_final_line(t if self.do_timer else None)
		self.safe_line_echo(final_line)

	def __enter__(self) -> 'Anim':
		self.thread = self.Thread(target=self.anim)
		self.thread.daemon = True
		self.thread.start()

		return self

	def __exit__(self, *exc):
		self.done = True
		self.thread.join()


class Callbacks:
	direct = 1
	toggle = 2
	callable = 3
	scrollable = 4
	instant = 5

class Option:
	def __init__(
		self,
		title: str = 'Option',
		id: Any = None,
		value: str = '',
		callback: Callbacks = Callbacks.direct, # Pending rename to `type`
		scrollable_values: Optional[list[str]] = None
	):
		"""
		Args:
			name: str - Option name
			value: str - Option default value
			callback: Callbacks - Option callback type
				direct: 1 - Direct in-terminal editing. `value` acts as editable value
				toggle: 2 - Toggle option. `value` acts as boolean value
				callable: 3 - Custom callback function. `value` acts as function, which receives `Option` as argument. Can be useful for inner-configs
				scrollable: 4 - Let's you scroll (left/right) through `selectable_values` list. `value` acts as current/selected value
				instant: 5 - On any toggle key, Option.id is returned. Can be useful for quick option selection

			values: list[str] - Option values

		"""

		self.title = title
		self.value = value
		self.id = id or title # Option identifier
		self.callback = callback
		self.scrollable_values = scrollable_values

		# Check if provided value exists in value list
		if callback == Callbacks.scrollable and value not in scrollable_values:
			self.value = scrollable_values[0]

class Config:
	def __init__(
		self,
		options: Union[list[Option], list[list[Option]]],
		per_page: int = 9
	):
		self.per_page = per_page

		is_rowed = isinstance(options[0], list)
		if is_rowed:
			self.options: list[list[Option]] = options
			self.page_amount = len(options)
			self.option_amount = sum(len(row) for row in options) or 1

		else:
			self.option_amount = len(options)
			self.page_amount = self.option_amount // per_page or 1
			self.options: list[list[Option]] = [options[i:i + per_page] for i in range(0, self.option_amount, per_page)]

		from sys import platform
		if 'win' in platform or 'nt' in platform:
			self.cli = self.win_cli
		elif platform == 'linux' or 'darwin' in platform:
			self.cli = self.unix_cli
		else:
			self.cli = self.any_cli

	def set_page(self, index: int):
		self.index = index % self.page_amount

	def add_page(self, amount: int = 1):
		new_index = self.index + amount
		self.index = new_index % self.page_amount

	def win_cli(self) -> dict[str, str]:
		import msvcrt, os
		os.system('')
		self.index = 0
		selected_option = 0
		cursor_pos = 0
		editing = False
		new_value = ''
		EXIT_KEYS = {b'\x03', b'\x04', b'q', b'\x1b'}
		TOGGLE_KEYS = {b'\r', b' '}

		while True:
			page = self.index + 1
			offset = 1 if page == 1 else page * self.per_page
			options = self.options[self.index]
			options_repr = []

			for i, option in enumerate(options):
				prefix = '>' if i == selected_option else ' '
				toggle = f" [{'*' if option.value else ' '}]" if option.callback == Callbacks.toggle else ""

				if editing and i == selected_option:
					value = new_value[:cursor_pos] + '█' + new_value[cursor_pos:]
				else:
					value = option.value

				if option.callback == Callbacks.direct:
					value = f' - {value}'
				elif option.callback == Callbacks.scrollable:
					current_idx = option.scrollable_values.index(option.value)
					value = f'{"< " if current_idx > 0 else ""}{value}{" >" if current_idx + 1 < len(option.scrollable_values) else ""}'
				else:
					value = ''

				options_repr.append(f'{prefix} [{offset + i}]{toggle} {option.title}{value}')

			options_repr = '\n'.join(options_repr)
			print(f'\033[2J\033[H{options_repr}\n\nPage {page}/{self.page_amount}', flush = True, end = '')
			key = msvcrt.getch()

			if editing:
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

			elif key == b'\xe0':  # Special keys prefix
				key = msvcrt.getch()

				if key == b'H':  # Up arrow
					selected_option = (selected_option - 1) % len(options)
				elif key == b'P':  # Down arrow
					selected_option = (selected_option + 1) % len(options)

				elif key == b'M':  # Right arrow
					option = options[selected_option]

					if option.callback == Callbacks.scrollable:
						current_idx = option.scrollable_values.index(option.value)
						option.value = option.scrollable_values[(current_idx + 1) % len(option.scrollable_values)]
					else:
						self.add_page(1)
						selected_option = 0

				elif key == b'K':  # Left arrow
					option = options[selected_option]

					if option.callback == Callbacks.scrollable:
						current_idx = option.scrollable_values.index(option.value)
						option.value = option.scrollable_values[(current_idx - 1) % len(option.scrollable_values)]
					else:
						self.add_page(-1)
						selected_option = 0

				elif key == b's':
					option = options[selected_option]
					if option.callback == Callbacks.scrollable:
						option.value = option.scrollable_values[0]

				elif key == b't':
					option = options[selected_option]
					if option.callback == Callbacks.scrollable:
						option.value = option.scrollable_values[-1]

			elif key in TOGGLE_KEYS: # Enter or Space
				option = options[selected_option]

				if option.callback == Callbacks.toggle:
					option.value = not option.value

				elif option.callback == Callbacks.instant:
					print('\033[2J\033[H', flush = True, end = '')
					return option.id

				elif option.callback == Callbacks.callable:
					option.callback(option)

				elif option.callback == Callbacks.scrollable:
					current_idx = option.scrollable_values.index(option.value)
					option.value = option.scrollable_values[(current_idx + 1) % len(option.scrollable_values)]

				else:
					editing = True
					new_value = option.value
					cursor_pos = len(new_value)

			elif key == b'p':
				inp = input('\nPage: ')

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

			elif key == b't': # Toggle all
				for option in options:
					if option.callback == Callbacks.toggle:
						option.value = not option.value

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

			elif key == b'\x06': # Ctrl+F - search options' values
				term = input('\nSearch: ').lower()
				for pg_idx, page in enumerate(self.options):
					for opt_idx, opt in enumerate(page):
						if term in opt.title.lower():
							self.index = pg_idx
							selected_option = opt_idx
							break
					else:
						continue
					break

			elif key in EXIT_KEYS:  # Quit
				break

		# Return all options
		print('\033[2J\033[H', flush = True, end = '')
		return {option.id: option.value for page in self.options for option in page}

	def unix_cli(self) -> dict[str, str]:

		import sys, tty, termios, select

		def getch():
			fd = sys.stdin.fileno()
			old_settings = termios.tcgetattr(fd)

			try:
				tty.setraw(sys.stdin.fileno())
				rlist, _, _ = select.select([fd], [], [])

				if rlist:
						ch = sys.stdin.read(1)
						if ch == '\x1b':  # escape sequences
							ch2 = sys.stdin.read(1)
							if ch2 == '[':
								ch3 = sys.stdin.read(1)
								return f'\x1b[{ch3}'
						return ch

				else:
						return None
			finally:
				termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

		self.index = 0
		selected_option = 0
		editing = False
		new_value = ''
		cursor_pos = 0
		EXIT_KEYS = {'\x03', '\x04', 'q', '\x1b'}
		TOGGLE_KEYS = {'\r', ' '}

		while True:
			page = self.index + 1
			offset = 1 if page == 1 else page * self.per_page
			options = self.options[self.index]
			options_repr = []

			for i, option in enumerate(options):
				prefix = '>' if i == selected_option else ' '
				toggle = f" [{'*' if option.value else ' '}]" if option.callback == Callbacks.toggle else ""

				if editing and i == selected_option:
					value = new_value[:cursor_pos] + '█' + new_value[cursor_pos:]
				else:
					value = option.value

				if option.callback == Callbacks.direct:
					value = f' - {value}'
				elif option.callback == Callbacks.scrollable:
					current_idx = option.scrollable_values.index(option.value)
					value = f'{"< " if current_idx > 0 else ""}{value}{" >" if current_idx + 1 < len(option.scrollable_values) else ""}'
				else:
					value = ''

				options_repr.append(f'{prefix} [{offset + i}]{toggle} {option.title}{value}')

			options_repr = '\n'.join(options_repr)
			print(f'\033[2J\033[H{options_repr}\n\nPage {page}/{self.page_amount}', flush = True, end = '')
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
				option = options[selected_option]
				if option.scrollable_values:
					current_idx = option.scrollable_values.index(option.value)
					option.value = option.scrollable_values[(current_idx + 1) % len(option.scrollable_values)]
				else:
					self.add_page(1)
					selected_option = 0
			elif key == '\x1b[D':  # Left arrow
				option = options[selected_option]
				if option.scrollable_values:
					current_idx = option.scrollable_values.index(option.value)
					option.value = option.scrollable_values[(current_idx - 1) % len(option.scrollable_values)]
				else:
					self.add_page(-1)
					selected_option = 0

			elif key in TOGGLE_KEYS:  # Enter or Space
				option = options[selected_option]

				if option.callback == Callbacks.toggle:
					option.value = not option.value

				elif option.callback == Callbacks.instant:
					print('\033[2J\033[H', flush = True, end = '')
					return option.id

				elif option.callback == Callbacks.callable:
					option.callback(option)

				elif option.callback == Callbacks.scrollable:
					current_idx = option.scrollable_values.index(option.value)
					option.value = option.scrollable_values[(current_idx + 1) % len(option.scrollable_values)]

				else:
					editing = True
					new_value = option.value
					cursor_pos = len(new_value)

			elif key == 'p':  # Page select
				try:
					page = int(input("\nPage: ")) - 1
					self.set_page(page)
					selected_option = 0
				except ValueError:
					pass

			elif key.isdigit():  # Number selection
				num = int(key) - 1
				if 0 <= num < len(options):
					selected_option = num

			elif key == 't': # Toggle all
				for option in options:
					if option.callback == Callbacks.toggle:
						option.value = not option.value

			elif key == 'w':  # Alternative up
				selected_option = (selected_option - 1) % len(options)
			elif key == 's':  # Alternative down
				selected_option = (selected_option + 1) % len(options)
			elif key == 'a':  # Alternative left
				self.add_page(-1)
			elif key == 'd':  # Alternative right
				self.add_page(1)

			elif key == '\x06':  # Ctrl+F - search options' values
				term = input('\nSearch: ').lower()
				for pg_idx, page in enumerate(self.options):
					for opt_idx, opt in enumerate(page):
						if term in opt.title.lower():
							self.index = pg_idx
							selected_option = opt_idx
							break
					else:
						continue
					break

			elif key == '\x1b[1;5D':  # Ctrl+←
				option = options[selected_option]
				if option.callback == Callbacks.scrollable:
					option.value = option.scrollable_values[0]
			elif key == '\x1b[1;5C':  # Ctrl+→
				option = options[selected_option]
				if option.callback == Callbacks.scrollable:
					option.value = option.scrollable_values[-1]

			elif key in EXIT_KEYS:  # q or Escape
				break

		# Return all options
		print('\033[2J\033[H', flush = True, end = '')
		return {option.id: option.value for page in self.options for option in page}

	def any_cli(self) -> dict[str, str]:
		self.index = 0

		while True:
			page = self.index + 1
			options = self.options[self.index]

			options_repr = ''
			for i, option in enumerate(options):
				toggle = f" [{'*' if option.value else ' '}]" if option.callback == Callbacks.toggle else ""
				value = f' - {option.value}' if option.callback == Callbacks.direct else ''
				options_repr += (f'[{i + 1}]{toggle} {option.title}{value}\n')

			options_repr += f'\nPage {page}/{self.page_amount}'
			options_repr += '\nOption: '

			with NewLiner():
				inp = input(options_repr)

			if inp.isdigit():
				num = int(inp) - 1
				if 0 <= num < len(options):
					option = options[num]

					if option.callback == Callbacks.toggle:
						option.value = not option.value

					elif option.callback == Callbacks.callable:
						option.callback(option)

					elif option.callback == Callbacks.instant:
						return option.id

					elif option.callback == Callbacks.scrollable:
						current_idx = option.scrollable_values.index(option.value)
						option.value = option.scrollable_values[(current_idx + 1) % len(option.scrollable_values)]

					else:
						new_value = input(f"New value for {option.title}: ")
						option.value = new_value

			elif inp == 'p':
				page = input("Page: ")
				try:
					page = int(page) - 1
					self.set_page(page)
				except ValueError:
					pass

			elif inp == 't': # Toggle all
				for option in options:
					if option.callback == Callbacks.toggle:
						option.value = not option.value

			elif inp == 'a':
				self.add_page(-1)

			elif inp == 'd':
				self.add_page(1)

			elif inp == 'q':
				break

			elif inp == 'f':
				term = input('Search: ').lower()
				for pg_idx, page in enumerate(self.options):
					for opt in page:
						if term in opt.title.lower():
							self.index = pg_idx
							break
					else:
						continue
					break

		# Return all options
		return {option.id: option.value for page in self.options for option in page}

class RequestError(Exception):
	def __init__(self, exc: Exception, return_items_len: int = 1):
		"""Specify `return_items_len` if object may be unpacked (returns None)"""
		self.return_items_len = return_items_len
		self.orig_exc = exc
		super().__init__(exc)

	def __bool__(self):
		return False

	# Simulate unpackable with return items length - a, b = response => [None, None]
	def __iter__(self):
		for i in range(self.return_items_len):
			yield None

	def __str__(self):
		return f'Error making aio.request: {self.orig_exc}'
	def __repr__(self):
		return f'RequestError({self.orig_exc})'

	def __getattr__(self, name):
		return getattr(self.orig_exc, name)

class aio:

	"""
	Methods:
		- aio.get() - 'GET' wrapper for aio.request
		- aio.post() - 'POST' wrapper for aio.request
		- aio.request() - ikyk
		- aio.open() - aiofiles.open() wrapper
		- aio.sem_task() - (asyncio.Semaphore, Coroutine) wrapper
	"""

	@staticmethod
	async def request(
		method: RequestMethods,
		url: str,
		session = None,
		toreturn: Union[ReturnTypes, Iterable[ReturnTypes]] = 'text',
		raise_exceptions: bool = False,
		httpx: bool = False,
		niquests: bool = False,
		*,
		filter: Callable[[Any], bool] = None,
		**kwargs,
	) -> Union[Any, list[Any], RequestError]:

		"""
		Accepts:

			- method: `GET` or `POST` request type
			- url: str

			- session: httpx/aiohttp Client Session
			- toreturn: ReturnTypes - List or Str separated by `+` of response object methods/properties
			- raise_exceptions: bool - Wether to raise occurred exceptions while making request or return list of None (or append to existing items) with same `toreturn` length
			- filter: Callable - Filters received response right after getting one
			- any other session.request() argument

		Returns:
			- Valid response: list of toreturn items
			- Exception at session.request(): RequestError

		Raises:
			Any Exception that can occur during session.request() and item processing

		"""

		if session:
			ses = session

		else:
			if httpx:
				import httpx
				ses = httpx.AsyncClient(http2 = True, follow_redirects = True)

			elif niquests:
				import niquests
				ses = niquests.AsyncSession()

			else:
				import aiohttp
				ses = aiohttp.ClientSession()

		_toreturn = toreturn
		if isinstance(toreturn, str):
			toreturn = toreturn.split('+')

		items_len = len(toreturn)

		try:
			response = await ses.request(method, url, **kwargs)
			if _toreturn == 'response':
				return response

		except Exception as e:
			if not session:
				if httpx: await ses.aclose()
				else: await ses.close()

			if raise_exceptions:
				raise e

			return RequestError(e, return_items_len = items_len)

		import inspect

		if filter:
			ok = filter(response)
			if inspect.iscoroutine(ok):
				ok = await ok

			if ok is not True:
				return ok

		return_items = []

		for item in toreturn:

			try:
				result = getattr(response, item)

				if inspect.iscoroutinefunction(result):
					result = await result()
				elif inspect.iscoroutine(result):
					result = await result
				elif callable(result):
					result = result()

			except:
				if raise_exceptions:
					raise

				result = None

			return_items.append(result)

		if not session:
			if httpx: await ses.aclose()
			else: await ses.close()

		return return_items if items_len != 1 else return_items[0]

	@staticmethod
	async def get(
		url: str,
		session = None,
		toreturn: Union[ReturnTypes, Iterable[ReturnTypes]] = 'text',
		raise_exceptions: bool = False,
		httpx: bool = False,
		niquests: bool = False,
		**kwargs,
	) -> Union[Any, list[Any], RequestError]:
		return await aio.request('GET', url, session, toreturn, raise_exceptions, httpx, niquests, **kwargs)

	@staticmethod
	async def post(
		url: str,
		session = None,
		toreturn: Union[ReturnTypes, Iterable[ReturnTypes]] = 'text',
		raise_exceptions: bool = False,
		httpx: bool = False,
		niquests: bool = False,
		**kwargs,
	) -> Union[Any, list[Any], RequestError]:
		return await aio.request('POST', url, session, toreturn, raise_exceptions, httpx, niquests, **kwargs)

	@staticmethod
	async def fuckoff(
		method: RequestMethods,
		url: str,
		session = None,
		toreturn: Union[ReturnTypes, Iterable[ReturnTypes]] = 'text',
		raise_exceptions: bool = False,
		httpx: bool = False,
		niquests: bool = False,
		filter: Callable[[Any], Union[bool, None]] = lambda r: getattr(r, 'status', getattr(r, 'status_code')) == 200,
		interval: Union[float, None] = 5.0,
		retries: int = -1,
		**kwargs
	) -> Union[Any, list[Any], None]:

		if interval:
			import asyncio

		while retries != 0:
			retries -= 1
			items = await aio.request(
				method, url, session, toreturn,
				raise_exceptions,
				httpx, niquests,
				filter = filter,
				**kwargs
			)

			if not isinstance(items, RequestError):
				return items

			elif interval and retries != 0:
				await asyncio.sleep(interval)

	@staticmethod
	async def open(
		file: str,
		action: ActionModes = 'read',
		mode: 'OpenTextMode' = 'r',
		content = None,
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
		coro: Coroutine,
	) -> Any:

		async with semaphore:
			return await coro

class pyromisc:

	@staticmethod
	def get_md(message) -> Optional[str]:
		return (message.caption or message.text, 'markdown', None)

	@staticmethod
	def get_user_name(user) -> Union[str, int]:
		if user.username:
			slug = f'@{user.username}'

		elif user.first_name:
			slug = user.first_name
			if user.last_name:
				slug += f' {user.last_name}'

		else:
			slug = user.id

		return slug

	@staticmethod
	def get_chat_name(chat) -> Union[str, int]:
		if chat.username:
			slug = f'@{chat.username}'

		elif chat.title:
			slug = chat.title

		elif chat.first_name:
			slug = chat.first_name
			if chat.last_name:
				slug += f' {chat.last_name}'

		else:
			slug = chat.id

		return slug


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
		round_decimals: bool = False,
		precission: int = 14,
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
			if absvalue < unit * magnitude:
				break

		value /= unit
		formatted: str = num.decim_round(value, decimals, round_decimals, precission, decims = [100, 10, 1])
		return formatted + suffix

	@staticmethod
	def unshorten(
		value: str,
		_round: bool = False
	) -> Union[float, str]:

		"""
		Accepts:

			- value: str - int-like value with shortener at the end
			- _round: bool - wether returned value should be rounded to integer

		Returns:
			Unshortened float

		Raises:
			ValueError: if provided value is not a number

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
		round_decimals: bool = True,
		precission: int = 14,
		decims: Optional[list[int]] = None,
	) -> str:

		"""
		Accepts:

			- value: float - usually with medium-big decimal length

			- decimals: int - amount of float decimals (+2 for rounding, after decimal point) that will be used in 'calculations'

			- precission: int - precission level (format(value, f'.->{precission}<-f'

			- decims: list[int] - if decimals argument is -1, this can be passed to change how many decimals to leave: default list is [1000, 100, 10, 5], List is iterated using enumerate(), so by each iter. decimal amount increases by 1 (starting from 0)

		Returns:
			- float-like str
			- str(value): if isinstance(value, int)

		"""

		if value.is_integer():
			# Wether to remove trailing `.0` from received float
			if round_decimals or decimals <= 0:
				return str(int(value))

			return str(value)

		# Convert float into string with given <percission>
		str_val = format(value, f'.{precission}f')
		number, decim = str_val.split('.')

		num_gt_1 = abs(value) > 1

		if decimals == -1: # Find best-suited decimal based on <decims>
			absvalue = abs(value)
			decims = decims or num.decims
			decimals = len(decims) # If value is lower than decims[-1], use its len

			for decim_amount, min_num in enumerate(decims):
				if absvalue < min_num:
					continue

				decimals = decim_amount
				break

		if decimals == 0:
			return str(int(value))

		elif num_gt_1:
			if round_decimals:
				return str(round(value, decimals))
			else:
				return f'{number}.{decim[:decimals]}'

		for i, char in enumerate(decim):
			if char != '0': break

		zeroes = '0' * i
		decim = decim.rstrip('0')

		if round_decimals and len(decim) >= i + decimals + 1:
			round_part = decim[i:i + decimals] + '.' + decim[i + decimals : len(decim)]
			rounded = str(round(float(round_part)))
			# print(round_part, rounded)
			decim = zeroes + rounded

		else:
			decim = zeroes + decim[i:i + decimals]

		return f'{number}.{decim}'

	decim = decim_round
	# print(decim_round(0.00000000485992, 3))

	def nicify(value: int) -> int:
		"""Converts numbers: 1234 -> 1200, 278 -> 250, 399 -> 300, 478 -> 400 etc."""

		if value == 0:
			return value

		import math
		abs_value = abs(value)
		exponent = math.floor(math.log10(abs_value))
		factor = 10 ** exponent
		scaled = abs_value / factor

		if scaled < 3:
			step = factor * 0.5 # 50
		else:
			step = factor# * 1 # 100

		max_tick = math.floor(abs_value / step) * step
		if value < 0:
			max_tick = -max_tick

		return int(max_tick)

	def bss(
		value: Union[int, float],
		decimals: int = -1,
		round_decimals: bool = False,
		precission: int = 14,
		suffixes: Optional[list[Union[str, int]]] = None
	) -> str:

		"""num.shorten() wrapper with byte size suffixes"""
		return num.shorten(value, decimals, round_decimals, precission, suffixes or num.fileSize_suffixes)

	bytesize_shorten = bss

	@staticmethod
	def beautify(value: Union[int, float], decimals: int = -1, round_decimals: bool = False, precission: int = 14) -> str:
		return num.shorten(float(
			num.decim_round(value, decimals, round_decimals, precission = precission)
		), decimals, round_decimals, precission)

# -------------MINECRAFT-VERSIONING-LOL-------------

class MC_VersionList:
	def __init__(self, versions: list[str], indices: list[int]):
		self.length = len(versions)

		if self.length != len(indices):
			raise ValueError(f'Versions and indices length mismatch: {self.length} != {len(indices)}')

		self.versions = versions
		self.indices = indices
		# self.map = {version: index for version, index in zip(versions, indices)}

class MC_Versions:
	"""
	Initialize via `await MC_Versions.init()`
	"""

	def __init__(self):
		from re import compile
		self.manifest_url = 'https://launchermeta.mojang.com/mc/game/version_manifest.json'

		# Pattern for a single version
		version_pattern = r'1\.\d+(?:\.\d+){0,1}'
		# Pattern for a single version or a version range
		item_pattern = rf'{version_pattern}(?:\s*-\s*{version_pattern})*'
		# Full pattern allowing multiple items separated by commas
		self.full_pattern = compile(rf'{item_pattern}(?:,\s*{item_pattern})*')

	@classmethod
	async def init(cls):
		"""
		Raises: RequestError if version manifest can't be fetched
		"""

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
			raise RequestError(f"Couldn't fetch minecraft version manifest ({status}). Data: {manifest_data}")

		self.release_versions: list[str] = [version['id'] for version in manifest_data['versions'] if version['type'] == 'release']
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

def setup_logger(name: str, clear_file: bool = False, dir: str = 'logs/'):
	"""
	Sets up minimalistic logger with file (all levels) and console (>debug) handlers
	Using queue.Queue to exclude logging from main thread
	"""

	import logging
	import logging.handlers
	import os
	from queue import Queue

	if not os.path.exists(dir):
		os.makedirs(dir)

	if clear_file:
		open(f'{dir}/{name}.log', 'w').write('')

	logger = logging.getLogger(name)
	logger.setLevel(logging.DEBUG)

	log_queue = Queue()
	queue_handler = logging.handlers.QueueHandler(log_queue)
	file_handler = logging.FileHandler(f'logs/{name}.log', encoding = 'utf-8')

	console_handler = logging.StreamHandler()
	console_handler.setLevel(logging.INFO)

	formatter = logging.Formatter(
		'%(levelname)s - %(asctime)s.%(msecs)03d - %(message)s',
		datefmt = '%H:%M:%S'
	)
	file_handler.setFormatter(formatter)
	console_handler.setFormatter(formatter)

	# Setup queue listener
	listeners = [file_handler, console_handler]
	queue_listener = logging.handlers.QueueListener(
		log_queue,
		*listeners,
		respect_handler_level = True
	)
	queue_listener.start()

	# Store listener reference to prevent garbage collection
	logger.addHandler(queue_handler)
	logger.queue_listener = queue_listener

	return logger

def get_content(source: Union[str, bytes, IO[bytes]]) -> tuple[Optional[int], Optional[bytes]]:
	"""
	Returns source byte content in tuple - (type, content)
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

def write_content(content: Union[str, bytes], output: Union[Literal[False], str, IO[bytes]]) -> Optional[Union[int, bytes]]:
	"""
	If output has `write` attribute, writes content to it and returns written bytes
	If output is False, returns content
	Otherwise writes content to file and returns written bytes,
	Or None if output is not a file path
	"""

	_, content = get_content(content)

	if hasattr(output, 'write'):
		return output.write(content)

	elif output is False:
		return content

	else:
		try:
			return open(output, 'wb').write(content)

		except:
			return

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
		'gzip': (lambda: __import__('gzip').compress, {}, {'level': 'compresslevel'}),
		'bzip2': (lambda: __import__('bz2').compress, {}, {'level': 'compresslevel'}),
		'lzma': (lambda: __import__('lzma').compress, {}, {'level': 'preset'}),
		'lzma2': (lambda: __import__('lzma').compress, lambda: {'format': __import__('lzma').FORMAT_XZ}, {'level': 'preset'}),
		'deflate': (lambda: __import__('zlib').compress, {}, {'level': 'level'}),
		'lz4': (lambda: __import__('lz4.frame').frame.compress, {}, {'level': 'compression_level'}),
		'zstd': (lambda: __import__('zstandard').compress, {}, {'level': 'level'}),
		'brotli': (lambda: __import__('brotli').compress, lambda: {'mode': __import__('brotli').MODE_GENERIC}, {'level': 'quality'}),
	}

	get_compress_func, additional_args, slug_map = algorithm_map[algorithm]

	if check_algorithm_support:

		try:
			get_compress_func()
			return True

		except:# ImportError
			return False

	compress = get_compress_func()

	if callable(additional_args):
		additional_args = additional_args()

	if compression_level:
		compression_slug = slug_map.get('level')

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
		compressed = compress(
			source, **additional_args
		)

	else:
		if not tar_if_file and os.path.isfile(source):
			with open(source, 'rb') as f:
				compressed = compress(f.read(), **additional_args)

		else:
			tar_path = '' if tar_in_memory else output + '.tar'
			if isinstance(output, str) and os.path.exists(output):
				os.remove(output)

			stream = make_tar(source, tar_path, ignored_exceptions, tar_in_memory)
			compressed = compress(stream if tar_in_memory else tar_path, **additional_args)

			if not tar_in_memory:
				os.remove(tar_path)

	return write_content(compressed, output)

def is_brotli(data: bytes) -> bool:
	"""
	Don't use this
	"""

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
		for algo, (decompress, start_bytes) in algorithm_map.items():
			if callable(start_bytes):
				algorithm = algo if start_bytes(content) else None

			elif content.startswith(start_bytes):
				algorithm = algo
				break

		if not algorithm:
			raise ValueError(f"Couldn't detect algorithm for decompression. First 10 bytes: {content[:10]}")

	decompress = algorithm_map[algorithm][0]()
	result = decompress(content, **kwargs)

	if output is None:
		output = source.rsplit('.', 1)[0] if isinstance(source, str) else False

	if output is False:
		return result

	elif hasattr(output, 'write'):
		return output.write(result)

	# Assuming output is a path
	import tarfile, io

	stream = io.BytesIO(result)
	is_tar = tarfile.is_tarfile(stream)

	if is_tar:
		import sys
		stream.seek(0)

		if sys.version_info >= (3, 12):
			tarfile.open(fileobj = stream).extractall(output, filter = 'data')
		else:
			tarfile.open(fileobj = stream).extractall(output)

	else:
		with open(output, 'wb') as f:
			f.write(result)

	return output

def compress_images(images: dict[str, Iterable[int]], page_amount: int = None, repetitive: bool = False) -> bytes:
	"""
	ONLY Use if:

	- Input page lists are sorted in ascending order.
	- You know if page numbers repeat across extensions (repetitive=True),
	  otherwise missing pages will be assigned to the default extension.
	  If not sure, always set repetitive=True

	- Page numbers do NOT exceed `page_amount` (if given).

	Failure to meet these conditions will result in CORRUPTED output

	"""

	import struct

	# ----------------------METHODS----------------------
	def encode_numbers(numbers: list[int]) -> bytes:
		data = bytearray()
		numbers_len = len(numbers)

		if numbers_len == 1:
			return struct.pack(STRUCT, numbers[0])

		max_step = max(numbers[i + 1] - numbers[i] for i in range(numbers_len - 1))

		# Set encoding based on max step
		set_encoding(max_step < 0xFF)

		# Add starting page
		prev_page = numbers[0]
		data.extend(struct.pack(STRUCT, prev_page))

		# Add encoding byte
		data.extend(encoding)

		i = 1

		while i < numbers_len:
			page = numbers[i]
			from_prev_step = page - prev_page
			# print(prev_page, page, from_prev_step, max_step)

			if i + 1 < numbers_len:
				range_step = numbers[i + 1] - page
				length = 1

				# Check for a sequence with constant step
				while i + length < numbers_len and numbers[i + length] == page + range_step * length:
					length += 1

				# Use range function
				if length >= 4:
					data.extend(FUNCTION)

					# Default range
					if range_step == 1:
						data.extend(RANGE_FUNCTION)

					# Custom step range
					else:
						data.extend(STEP_RANGE_FUNCTION)
						data.extend(struct.pack(STRUCT, range_step))

					# Step from previous page
					data.extend(struct.pack(struct_format, from_prev_step))
					# Range length
					data.extend(struct.pack(STRUCT, length))

					i += length
					prev_page = numbers[i - 1]
					continue

			# Regular number if no pattern found
			data.extend(struct.pack(struct_format, from_prev_step))
			prev_page = page
			i += 1

		return bytes(data)

	def set_encoding(Uint8 = False):
		nonlocal FUNCTION, struct_format, encoding, separator

		if Uint8:
			separator = b'\x00'
			encoding = b'\x01'
			FUNCTION = b'\xFF'
			struct_format = '>B'

		else:
			separator = b'\x00\x00'
			FUNCTION = b'\xFF\xFF'
			struct_format = '>H'
			encoding = b'\x02'

	# --------------------CONSTANTS--------------------
	# Custom Bytes
	SEPARATOR = EXT_SEPARATOR = separator = b'\x00'
	FUNCTION = b'\xFF'
	RANGE_FUNCTION = ENCODING = encoding = b'\x01'  # Consecutive range (step=1)
	STEP_RANGE_FUNCTION = b'\x02'  # Stepped range
	# CONSEC_BYTES_FUNCTION = b'\x03'
	STRUCT = struct_format = '>B'

	# Default extension, page amount from received data
	default_ext = max(images, key = lambda ext: len(images[ext]))
	page_amount = page_amount or max(max(sublist) for sublist in images.values())
	assert page_amount < 65535, "Invalid page amount, Allowed from 1 to 65534"

	# Choose encoding type
	if page_amount >= 0xFF:
		set_encoding()
		ENCODING = encoding
		STRUCT = struct_format
		EXT_SEPARATOR = separator

	# ------------------COMPRESSION------------------
	# Stream base data
	data = bytearray()
	data.extend(default_ext.encode('utf-8'))  # Default extension
	data.extend(SEPARATOR + ENCODING)  # Encoding flag
	data.extend(struct.pack(STRUCT, page_amount))  # Page amount

	# Return if only one extension
	if len(images) == 1:
		return bytes(data)

	if repetitive:
		# Iterate through all extensions and add pages that are present in default_ext
		default_pages = set(images[default_ext])
		other_pages = set(page for ext, pages in images.items() if ext != default_ext for page in pages)
		repetitive_pages = list(default_pages.intersection(other_pages))

		if repetitive_pages:
			data.extend(b'\xFF') # Byte after page amount tells wether indices are repetitive
			data.extend(encode_numbers(repetitive_pages))

	# STRUCTURE:
	# & - SEPARATOR, && - EXT_SEPARATOR, | - possible EOData, [...] - repeated stuff
	# (default extension) & (encoding type) & (page amount) |
	# [ && (ext1 name) (start page) | (encoding type) (ext1 data) ]

	# Compress all extensions
	for ext, num_list in images.items():
		if ext == default_ext:
			continue

		data.extend(EXT_SEPARATOR)
		data.extend(ext.encode('utf-8'))  # Extension name
		data.extend(SEPARATOR)
		data.extend(encode_numbers(num_list))  # Encoded numbers

	return bytes(data)

def decompress_images(data: bytes) -> dict[str, list[int]]:
	import struct

	# ----------------------METHODS----------------------
	# Helper function to read a null-terminated string
	def read_string() -> str:
		nonlocal index
		end = data.find(SEPARATOR, index)

		if end == -1:
			raise ValueError("Missing separator after string")

		string = data[index:end].decode('utf-8')
		index = end + 1  # Move past the separator
		return string

	def set_encoding(Uint8 = False):
		nonlocal FUNCTION, struct_format, int_size, separator

		if Uint8:
			separator = b'\x00'
			FUNCTION = b'\xFF'
			struct_format = '>B'
			int_size = 1

		else:
			separator = b'\x00\x00'
			FUNCTION = b'\xFF\xFF'
			struct_format = '>H'
			int_size = 2

	def decode_numbers() -> list[int]:
		nonlocal index

		# Get starting page
		prev_page = struct.unpack(STRUCT, data[index:index + INT_SIZE])[0]
		index += INT_SIZE # Move past start page

		# Set start page
		numbers = [prev_page]

		if index == LENGTH or data[index:index + INT_SIZE] == EXT_SEPARATOR:
			return numbers

		# Get extension encoding
		set_encoding(data[index] == 0x01)
		index += 1 # Move past encoding byte

		while index < LENGTH and data[index:index + INT_SIZE] != EXT_SEPARATOR:  # Until next separator

			if data[index:index + int_size] == FUNCTION:
				index += int_size
				function_id = data[index]
				index += 1  # Move past function ID

				if function_id == RANGE_FUNCTION[0]:  # Integer range function
					# Start - steps from previous page
					start = prev_page + struct.unpack(struct_format, data[index:index + int_size])[0]
					index += int_size

					# Range length
					range_len = struct.unpack(STRUCT, data[index:index + INT_SIZE])[0]
					index += INT_SIZE

					numbers.extend(range(start, start + range_len))

				elif function_id == STEP_RANGE_FUNCTION[0]:  # Stepped range
					# Range step
					step = struct.unpack(STRUCT, data[index:index + INT_SIZE])[0]
					index += INT_SIZE

					# Start - steps from previous page
					start = prev_page + struct.unpack(struct_format, data[index:index + int_size])[0]
					index += int_size

					# Range length
					range_len = struct.unpack(STRUCT, data[index:index + INT_SIZE])[0]
					index += INT_SIZE

					numbers.extend(range(start, start + step * range_len, step))

				else:
					raise ValueError(f"Unknown function ID: {function_id}")

				prev_page = numbers[-1]

			else:  # Regular number
				prev_page = prev_page + struct.unpack(struct_format, data[index:index + int_size])[0]
				index += int_size
				numbers.append(prev_page)

		return numbers

	# --------------------CONSTANTS--------------------
	# Custom Bytes
	SEPARATOR = EXT_SEPARATOR = separator = b'\x00'
	INT_SIZE = int_size = 1
	FUNCTION = b'\xFF'
	RANGE_FUNCTION = b'\x01'
	STEP_RANGE_FUNCTION = b'\x02'
	# CONSEC_BYTES_FUNCTION = b'\x03'
	STRUCT = struct_format = '>B'

	# Stream constants
	index = 0
	LENGTH = len(data)

	# STRUCTURE:
	# & - SEPARATOR, && - EXT_SEPARATOR, | - possible EOData, [...] - repeated stuff
	# (default extension) & (encoding type) & (page amount) |
	# [ && (ext1 name) (start page) | (encoding type) (ext1 data) ]

	# Get default extension
	default_ext = read_string()

	# Get encoding flag
	ENCODING = data[index]
	index += 1  # Move past encoding flag

	if ENCODING == 0x02:
		set_encoding()
		STRUCT = struct_format
		INT_SIZE = int_size
		EXT_SEPARATOR = separator

	# Get page amount
	page_amount = struct.unpack(STRUCT, data[index:index + INT_SIZE])[0]
	index += INT_SIZE

	added_pages = set()
	images = dict()
	repetitive = False

	# Single extension case
	if index == LENGTH:
		return {default_ext: list(range(1, page_amount + 1))}

	# Check if pages are repetitive (next byte is 0xFF)
	elif data[index] == 0xFF:
		index += 1
		numbers = decode_numbers()
		added_pages = set(numbers)
		images[default_ext] = numbers
		repetitive = True

	index += INT_SIZE  # Move past extension separator

	# ----------------DECOMPRESSION----------------

	while index < LENGTH:
		# Get extension name
		ext = read_string()

		numbers = decode_numbers()
		images[ext] = numbers
		added_pages.update(numbers)
		index += INT_SIZE  # Move past separator

	# Fill default extension pages
	if not repetitive:
		images[default_ext] = []

	images[default_ext].extend(set(range(1, page_amount + 1)) - added_pages)

	if repetitive:
		images[default_ext].sort()

	return images