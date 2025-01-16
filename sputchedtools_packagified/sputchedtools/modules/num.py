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

from typing import Union, Optional

_suffixes: list[Union[str, int]] = ['', 'K', 'M', 'B', 'T', 1000]
_decims: list[int] = [1000, 100, 10, 5] # List is iterated using enumerate(), so by each iter. decimal amount increases by 1 (starting from 0)
_deshorteners: dict[str, int] = {'k': 10**3, 'm': 10**6, 'b': 10**9, 't': 10**12}

fileSize_suffixes: list[Union[str, int]] = [' B', ' KB', ' MB', ' GB', ' TB', 1024]
sfx = fileSize_suffixes

__all__ = ['fileSize_suffixes', 'sfx', 'shorten', 'unshorten', 'decim_round', 'beautify']

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
	suffixes: list[str] = suffixes or _suffixes
	magnitude = suffixes[-1]

	for i, suffix in enumerate(suffixes[:-1]):
		unit = magnitude ** i
		if absvalue < unit * magnitude or i == len(suffixes) - 1:
			value /= unit
			formatted: str = decim_round(value, decimals, decims = [100, 10, 1])
			return formatted + suffix

def unshorten(
	value: str,
	_round: bool = True
) -> Union[float, int, str]:

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
		mp = _deshorteners[mp]

		if _round:
			unshortened = round(number * mp)

		else:
			unshortened = number * mp

		return unshortened

	except (ValueError, KeyError):
		return value

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
		decims = decims or _decims
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

def beautify(value: Union[int, float], decimals: int = -1, precission: int = 20) -> str:
	return shorten(float(decim_round(value, decimals, precission = precission)), decimals)