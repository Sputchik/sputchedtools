# sputchedtools

#### Simple, powerfull different-purpose module, initially created to reduce repetetive functions defenitions across projects

## Installation

```bash
pip install sputchedtools
```

## Features

### Miscellaneous Classes
- `Anim` - Animated loading 'spinner' with customizable characters and text (using `set_text`)
- `ProgressBar` - Progress bar for iterables with customizable text. Simply displays completed iterations out of overall length
- `AsyncProgressBar` - Asynchronous version of progress bar. Has `gather` and `as_completed` methods
- `NewLiner` - Context manager for adding newlines before/after code blocks
- `Timer` - Context manager for code execution timing

### Asynchronous Operations
- `aio` class with methods:
	- _request() - `aiohttp`/`httpx`/`niquests` Manually-specified request
	- `request()` - `aiohttp`/`httpx`/`niquests` GET requests
	- `post()` - `aiohttp`/`httpx`/`niquests` POST requests
	- `open()` - `aiofiles` file operations
	- `sem_task()` - Semaphore-controlled task execution

### Number Formatting
- `num` class with methods:
	- `shorten()` - Convert numbers to shortened form (e.g., 1000000 → 1M)
	- `unshorten()` - Convert shortened numbers back (e.g., 1M → 1000000)
	- `decim_round()` - Smart decimal rounding, returns **`str`* object, mainly for **readability** purpose
	- `beautify()` - Combine shortening and decimal rounding

### Web3 Utilities
- `Web3Misc` - Ethereum-related utilities:
	- Gas price monitoring
	- Transaction nonce tracking
	- Gas estimation (-monitoring)

### Minecraft Version Management
- `MC_Versions` - Minecraft version manifest handling - Version sorting, list to stringified range converter

### Compression Tools
- `compress()` - File/Directory/Stream/Bytes compression with multiple algorithms:
	- gzip, bzip2, lzma, zlib, lz4, zstd, brotli
- `decompress()` - Auto-algo-detective File/Directory/Stream/Bytes decompression

## Usage Example

> ### Checkout [test.py](test.py)

## Running [test.py](test.py)

```
git clone https://github.com/Sputchik/sputchedtools.git && cd sputchedtools
```
```
pip install -r reqs
```
```
python3 test.py
````