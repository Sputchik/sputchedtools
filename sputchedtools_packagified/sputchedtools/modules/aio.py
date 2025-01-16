"""
Methods:
	- aio.get() - 'GET' wrapper for aio.request
	- aio.post() - 'POST' wrapper for aio.request
	- aio.request() - ikyk
	- aio.open() - aiofiles.open() method
	- aio.sem_task() - uses received semaphore to return function execution result
"""

import asyncio
import inspect
import aiofiles

from typing import Optional, Union, Any, Literal, Iterable, Callable

__all__ = ['get', 'post', 'request']

RequestMethods = Literal['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE']
ReturnTypes = Literal['ATTRS', 'charset', 'close', 'closed', 'connection', 'content', 'content_disposition', 'content_length', 'content_type', 'cookies', 'get_encoding', 'headers', 'history', 'host', 'json', 'links', 'ok', 'raise_for_status', 'raw_headers', 'read', 'real_url', 'reason', 'release', 'request_info', 'start', 'status', 'text', 'url', 'url_obj', 'version', 'wait_for_close']

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

async def get(
	url: str,
	toreturn: Union[ReturnTypes, Iterable[ReturnTypes]] = 'text',
	session: Optional[Any] = None,
	raise_exceptions: bool = False,
	httpx: bool = False,
	niquests: bool = False,
	**kwargs,
) -> list[Any]:
	return await request('GET', url, toreturn, session, raise_exceptions, httpx, niquests, **kwargs)

async def post(
	url: str,
	toreturn: Union[ReturnTypes, Iterable[ReturnTypes]] = 'text',
	session: Optional[Any] = None,
	raise_exceptions: bool = False,
	httpx: bool = False,
	niquests: bool = False,
	**kwargs,
) -> list[Any]:
	return await request('POST', url, toreturn, session, raise_exceptions, httpx, niquests, **kwargs)

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

	async with aiofiles.open(file, mode, **kwargs) as f:
		if action == 'write':
			return await f.write(content)
		else:
			return await f.read()

async def sem_task(
	semaphore: asyncio.Semaphore,
	func: Callable[..., Any],
	*args, **kwargs
) -> Any:
	async with semaphore:
		return await func(*args, **kwargs)