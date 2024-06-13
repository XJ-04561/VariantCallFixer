
from VariantCallFixer.Globals import *
from VariantCallFixer.SampleData import SampleData
from collections import UserDict

_T = TypeVar("_T")

class RowDict(dict):
	CHROM : str|None
	POS : int|None
	ID : str|None
	REF : str|None
	ALT : tuple|None
	QUAL : int|None
	FILTER : str|None
	INFO : dict|None
	FORMAT : list|None
	SAMPLES : list[SampleData]|None

	def __getattr__(self, name):
		try:
			return self[name]
		except:
			# To get the same error message as usual.
			return self.__getattribute__(name)
	
	def __getitem__(self, key):
		if key in self.keys():
			return super().__getitem__(key)
		elif "FORMAT" in self and key in self["FORMAT"]:
			return tuple(map(lambda x:x.get(key), self.SAMPLES))
		elif "INFO" in self and key in self["INFO"]:
			return self["INFO"].get(key)
		
		return super().__getitem__(key)
	
	@overload
	def get(self, key : str, /): ...
	@overload
	def get(self, key : str, default : Any, /) -> Any: ...
	@overload
	def get(self, key : str, default : _T, /) -> _T|Any: ...
	def get(self, key, default=None, /):
		try:
			return self[key]
		except KeyError:
			return default