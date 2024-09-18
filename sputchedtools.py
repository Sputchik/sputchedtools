class Timer:
	"""
	
	Code execution Timer, use 'with' keyword

	Accepts:
		txt = '': text after main print message
		decimals = 2: time difference precission
	
	"""

	def __init__(self, txt = '', decimals = 2):
		import time
		self.time = time
		self.txt = txt
		self.decimals = decimals
	
	def __enter__(self):
		self.was = self.time.time()
		
	def __exit__(self, f, u, c):
		self.diff = format((self.time.time() - self.was), f'.{self.decimals}f')
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

				if 200 <= response.status < 300 and str(response.url)[-5:] !=  '/404/':
					status = response.status
					
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

		if platform == 'win32':
			import winloop # type: ignore
			winloop.install()
	
		else:
			import uvloop # type: ignore
			asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
		
		return True
	
	except ImportError:
		return False

def safe_round(value: float, decimals: int = 2) -> str:
	
	if value == 0: return value
	elif not isinstance(value, float) or not isinstance(decimals, int) or decimals > 20: return value
	
	value = format(value, '.20f')
	decim = value.split('.')[1]
	
	if value != '0':
		decim = decim[0:decimals]
		i = 0
	
	else:
		for i in range(20):
			if decim[i] != '0': break
		decim = decim[i:i + decimals + 1]
	
	while decim.endswith('0'):
		decim = decim[:-1]
	
	if len(decim) > decimals:
		rounded = str(round(float(decim[:decimals] + '.' + decim[-1])))
		
		while rounded.endswith('0'):
			rounded = rounded[:-1]
		
		decim = '0' * i + rounded
	
	else: decim = '0' * i + str(decim)
	
	return value.split('.')[0] + '.' + decim

def convert_to_float(num):
	multipliers = {'k': 10**3, 'm': 10**6, 'b': 10**9, 't': 10**12}
	
	mp = num[-1].lower()
	digit = num[:-1]
	
	try:
		digit = float(digit)
		mp = multipliers[mp]
		return digit * mp
	
	except (ValueError, IndexError):
		return num
