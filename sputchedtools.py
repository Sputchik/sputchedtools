class Timer:

	"""

	Code execution Timer, use 'with' keyword

	Accepts:
		txt = '': text after main print message
		decimals = 2: time difference precission

	"""

	import time

	def __init__(self, txt = '', decimals = 2):
		self.txt = txt
		self.decimals = decimals

	def __enter__(self):
		self.was = Timer.time.time()

	def __exit__(self, f, u, c):
		self.diff = format((Timer.time.time() - self.was), f'.{self.decimals}f')
		print(f'\nTaken time: {self.diff}s {self.txt}')


class aio:
	import asyncio, aiohttp, aiofiles

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


		created_session = False
		if session is None:
			session = aio.aiohttp.ClientSession()
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

		except aio.asyncio.TimeoutError:
			return 0, None

		except aio.asyncio.CancelledError:
			return None, None

		except Exception as e:
			# print(f'\nFailed to get response from {url}')
			return -3, e

		finally:
			if created_session is True:
				await session.close()

	@staticmethod
	async def post(url, session = None, toreturn = 'json', **kwargs):

		created_session = False
		if session is None:
			session = aio.aiohttp.ClientSession()
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

		except aio.asyncio.TimeoutError:
			return 0, None

		except aio.asyncio.CancelledError:
			return None, None

		except Exception as e:
			# print(f'\nFailed to get response from {url}')
			return -3, e

		finally:
			if created_session is True:
				await session.close()

	@staticmethod
	async def open(file: str, action: str = 'read', mode: str = 'r', content = None, **kwargs):
		async with aio.aiofiles.open(file, mode, **kwargs) as f:

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
	import asyncio
	from sys import platform

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
	suffixes = ['k', 'm', 'b', 't']
	multipliers = {'k': 10**3, 'm': 10**6, 'b': 10**9, 't': 10**12}

	@staticmethod
	def shorten(value: int | float, decimals = 2):

		if not isinstance(value, (int, float)):
			return None

		magnitude = 1000.0

		sign = '-' if value < 0 else ''
		value = abs(value)

		if value < magnitude:
			return f"{sign}{value}"

		for i, suffix in enumerate(num.suffixes, start=1):
			unit = magnitude ** i

			if value < unit * magnitude:
				value = format(value / unit, f'.{decimals}f')
				return f"{sign}{value}{suffix}"

		value = format(value / (magnitude ** len(num.suffixes)), f'.{decimals}f')
		return f'{sign}{value}t'

	@staticmethod
	def unshorten(value: str) -> float | str:

		mp = value[-1].lower()
		digit = value[:-1]

		try:
			digit = float(digit)
			mp = num.multipliers[mp]
			return digit * mp

		except (ValueError, IndexError):
			return num

	@staticmethod
	def decim_round(value: float, decimals: int = 2, precission: int = 20) -> str:
		"""

		Accepts:
			value: float - usually with mid-big decimals length
			decimals: int - determines amount of digits (+2 for rounding, after decimal point) that will be used in 'calculations'
			precission: int - determines precission level (format(value, f'.->{precission}<-f'

		Returns:
			accepted value:
				if value == 0,
				not isinstance(value & (decimals, precission), float & int)
				decimals & value < 1

			str-like float

		"""

		if value == 0: return value
		elif not isinstance(value, float): return value
		elif not (decimals > 0 and isinstance(decimals, int)) or not (precission > 0 and isinstance(precission, int)): return value

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
			rounded = str(round(float(decim[:-2] + '.' + decim[-2:]))).rstrip('0')
			decim = '0' * i + rounded

		else: decim = '0' * i + str(decim)

		return integer + '.' + decim
