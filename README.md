# spuchedtools

Simple, lazy-import, powerful multi-purpose module, initially created to reduce repetitive definitions across projects

## Installation

```bash
pip install sputchedtools
```

## Features

# CLI

### Timer/QTimer (1), NewLiner (2)
Use as context manager to (1) measure code execution time, with formatting and lap support, (2) print new line before and after code block

```python
with NewLiner(), Timer('Taken time: %s %ms %us. Best variant: %a'):
	...

with QTimer() as t: # won't print anything
	t.lap()

print(*t.laps, t.diff == t.elapsed, sep = '\n')
```

### ProgressBar
Async-supported, very simple, executed task counter

```python
for i in ProgressBar(
	iterator = range(10), # Or Coroutine Iterator if using `async for`
	text = 'Processing...',
	# task_amount = ..., <- If iterator doesn't have __len__ attribute
	final_text = 'Done!\n',
):
	...
```

### Anim
Iterates through given/default chars at configurable delay while executing code block. Supports dynamic text editing without shitting terminal. Supports manual updating

```python
with Anim(
	prepend_text = 'Downloading ...', append_text = '',
	just_clear_char = False, # On exit
	clear_on_exit = True,
	delay = 0.1,
	manual_update = False, # Manual Anim.update()
	# chars = (..., ...)
) as a:

	# a.set_text()
	# a.set_chars()
	__import__('time').sleep(1)
	a.update()
```

### Config, Option
Define option list and let user modify them via terminal

```python
options = [
	Option(
		title = f'Your favorite hot meal: ',
		value = '',
		callback = Callbacks.direct # In-terminal edit
		# Read Option docstring for more advanced usage
	)
]

# Results received as OptionName: Value
results: dict[str, str] = Config(
	options = options,
	per_page = 9, # Let's you navigate through options with 1-9 keys (if < 10)
).cli()
```

# Utilities

## aio

### Methods:
 - aio.request()
	- aiohttp/httpx/niquests wrapper
 - aio.get()
	- aio.request('GET') wrapper
 - aio.open()
	- aiofiles wrapper
 - aio.sem_task()
	- asyncio.Semaphore wrapper

```python
async def main():
	response = await aio.get(
		url = 'https://example.com',
		toreturn = ['text', 'status'], # Response attribute list
		# session = ...,
		raise_exceptions = False, # If True, replaces failed attributes with `None`, keeping `toreturn` length
		# Session provider
		httpx = False,
		niquests = False,
		# **request_args: headers, params, etc.
	)
	if not response: # The only way this can be evaluated is by an error during request. Here, response is `RequestError` object with __bool__ returning False
		raise response

	text = response[0]
	await aio.open(
		file = 'response.txt',
		action = 'write',
		mode = 'w',
		content = text
	)
```

## num
### Methods:
 - num.shorten
	- 10_000_000 -> 10M

- num.unshorten
	- 10M -> 10_000_000.0

- num.decim_round
	- Safely rounds float's decimals

```python
file_size = num.shorten(
	value = 25_000_000,
	decimals = -1,
	suffixes = num.fileSize_suffixes # or num.sfx
) # 23.8 MB

num.decim_round(
	value = 0.000000004801,
	decimals = 4, # How many to leave
	round_decimals = True,
	precission = 14,
	# decims = [...] if decimals argument is -1, this can be passed to change how many decimals to leave: default list is [1000, 100, 10, 5], List is iterated using enumerate(), so by each iter. decimal amount increases by 1 (starting from 0)
)
```

## Methods

#### enhance_loop() => installs uvloop or winloop
#### get_content() => Returns source byte content (raw, buffer, file)
#### write_content() => see docstring

## compress
Better explain here:

```python
compress(
	source = ..., # bytes, file/folder path, stream
	algorithm = 'lz4', # Supported are specified in `Algorithms` Literal
	output = ..., # False - bytes, file path, stream
	ignored_exceptions = (...) # Exceptions tuple to ignore when tar-ing directory. Default is (PermissionError, OSError),
	tar_in_memory = True,
	tar_if_file = False, # Directly compresses file content
	compression_level = None, # Use only if you know compression algorithm you use
	check_algorithm_support = False
)
```

## decompress
Gladly much simpler than `compress`, i'm tired writing this readme

```python
decompress(
	source = ..., # bytes, file path, stream
	algorithm = ..., # optional, function autodetects it, stops at `brotli` (undetectable) and raises if not it
	output = ... # False -> bytes, directory/file path, stream
)
