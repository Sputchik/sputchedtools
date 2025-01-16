# cython: language_level=3

__version__ = "0.30.0"

import sys
import ast
import importlib

class LazyModule:
	def __init__(self, name: str):
		self._name = name
		self._module = None

		# Extract __all__ using AST to avoid executing the module
		spec = importlib.util.find_spec(self._name, package=__package__)
		if spec is None:
			raise ImportError(f"No module named '{self._name}'")

		try:
			with open(spec.origin, 'r', encoding='utf-8') as f:
				module_ast = ast.parse(f.read(), spec.origin)

			for node in module_ast.body:
				if isinstance(node, ast.Assign):
					for target in node.targets:
						if isinstance(target, ast.Name) and target.id == '__all__':
							if isinstance(node.value, ast.List):
								all_list = [
									element.s
									for element in node.value.elts
									if isinstance(element, ast.Str)
								]
								# Create lazy attributes for each name in __all__
								for attr in all_list:
									setattr(sys.modules[__package__], attr, self._make_lazy_attribute(attr))
							break
		except:
			# If we can't parse the file, we'll load attributes on first access
			pass

	def _make_lazy_attribute(self, name):
		def _lazy_attribute(*args, **kwargs):
				if self._module is None:
					self._module = importlib.import_module(self._name, package=__package__)
				real_attr = getattr(self._module, name)
				# Replace the lazy attribute with the real one
				setattr(sys.modules[__package__], name, real_attr)
				return real_attr(*args, **kwargs) if callable(real_attr) else real_attr
		return _lazy_attribute

	def __getattr__(self, name):
		if self._module is None:
				self._module = importlib.import_module(self._name, package=__package__)
		return getattr(self._module, name)

	def __dir__(self):
		if self._module is None:
				self._module = importlib.import_module(self._name, package=__package__)
		return dir(self._module)

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