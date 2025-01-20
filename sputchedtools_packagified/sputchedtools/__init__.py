# cython: language_level=3

__version__ = "0.30.0"

import sys
import ast
import importlib

class LazyModule:
	...

# Core utilities
from .core import *

# Lazy load modules
utils = LazyModule('.modules.utils')
autils = LazyModule('.modules.autils')
aio = LazyModule('.modules.aio')
num = LazyModule('.modules.num')
web3 = LazyModule('.modules.web3')
mc = LazyModule('.modules.mc')
compress = LazyModule('.modules.compress')