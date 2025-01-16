"""asynchronous util placeholder"""

import asyncio
import sys

from typing import Coroutine, Any, Union, Optional, Iterable, Iterator

__all__ = ['ProgressBar']

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

		self.flush = lambda k: sys.stdout.write(k); sys.stdout.flush()
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
		text_len = len(self._text)
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

		for task in asyncio.as_completed(tasks):
			result = await task
			await self.aupdate()
			results.append(result)

		self.finish()
		return results

	async def as_completed(self, tasks: Iterable[Coroutine]):
		self.update(0)

		for task in asyncio.as_completed(tasks):
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