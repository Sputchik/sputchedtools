"""commons"""

import time
import shutil
from .num import decim_round

from typing import Any, Optional, Iterable, Union, Literal
from dataclasses import dataclass
from threading import Thread

__all__ = ['Timer', 'Anim', 'NewLiner']

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

		self.echo_fmt = echo_fmt
		self.append_fmt = append_fmt
		self.time_fmts = ['s', 'ms', 'us']
		self.mps = [1] + [1000**i for i in range(1, len(self.time_fmts))]
		self.laps: list[TimerLap] = []

	def __enter__(self) -> 'Timer':
		self._start_time = self._last_lap = time.perf_counter()
		return self

	def lap(self, name: str = "") -> float:
		now = time.perf_counter()
		lap_time = TimerLap(self._last_lap, now, name)
		self.laps.append(lap_time)
		self._last_lap = now

		return now - self._last_lap

	def format_output(self, seconds: float) -> str:
		fmt = self.echo_fmt

		for mp, unit in zip(self.mps, self.time_fmts):
			fmt = fmt.replace(f"%{unit}", f"{decim_round(seconds * mp)}{unit}" if self.append_fmt else '', 1)

		return fmt

	def __exit__(self, *exc):
		end_time = time.perf_counter()
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

		self.chars = chars or  ('⠉', '⠙', '⠘', '⠰', '⠴', '⠤', '⠦', '⠆', '⠃', '⠋')
		self.prepend_text = prepend_text

		if len(self.prepend_text) != 0 and not self.prepend_text.endswith(' '):
			self.prepend_text += ' '

		self.append_text = append_text
		self.just_clear_char = just_clear_char
		self.clear_on_exit = clear_on_exit
		self.delay = delay
		self.manual_update = manual_update

		self.terminal_size = shutil.get_terminal_size().columns
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
				time.sleep(self.delay)

		if self.clear_on_exit:
			self.safe_line_echo('\r' + ' ' * len(self.get_line()) + '\r')

		elif self.just_clear_char:
			self.safe_line_echo('\r' + self.prepend_text + ' ' * len(self.char) + self.append_text)

	def __enter__(self) -> 'Anim':
		if self.manual_update:
			self.update()

		else:
			self.thread = Thread(target=self.anim)
			self.thread.daemon = True
			self.thread.start()

		return self

	def __exit__(self, *exc):
		if not self.manual_update:
			self.done = True
			self.thread.join()