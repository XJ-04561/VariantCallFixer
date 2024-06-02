
from VariantCallFixer.Globals import *
from collections import UserList
from VariantCallFixer.HeaderEntries import HeaderEntry

class VCFHeader(UserList):
	
	_nameDict : dict[str,HeaderEntry]

	def __init__(self, initList : Iterable[HeaderEntry] = None):
		if initList:
			self._nameDict = {item.name:item for item in initList}
		else:
			self._nameDict = {}
		super().__init__(initList)

	def __getitem__(self, key):
		if isinstance(key, type) and issubclass(key, HeaderEntry):
			return self._nameDict[key.name]
		elif isinstance(key, str):
			return self._nameDict[key]
		else:
			return super().__getitem__(key)
	
	def __setitem__(self, key, value : HeaderEntry):
		_APPEND = object()
		if isinstance(key, type) and issubclass(key, HeaderEntry):
			name = key.name
			if key in self:
				key = self.index(key)
			else:
				key = _APPEND
		elif isinstance(key, str):
			name = key
			if key in self:
				key = self.index(key)
			else:
				key = _APPEND
		else:
			name = value.name
			key = key
		
		if key is _APPEND:
			super().append(value)
		else:
			super().__setitem__(key, value)
		
		if value.unique:
			self._nameDict[name] = value
		else:
			if name in self._nameDict[name]:
				self._nameDict[name][self._nameDict[name].index(name)] = value
			else:
				
				self._nameDict[name].append(value)

		return super().__getitem__(key)
	
	def __format__(self, fs : str="\n"):
		if not fs:
			fs = "\n"
		return "".join(map(f"##{{}}{fs}".format, self))
	
	def append(self, item):
		super().append(item)
		if item.multiplet:
			if item.name not in self._nameDict:
				self._nameDict[item.name] = []
			self._nameDict[item.name].append(item.value)
		else:
			self._nameDict[item.name] = item.value

class VCFBody(UserList):
	def __format__(self, fs : str="\n"):
		if not fs:
			fs = "\n"
		return "".join(map(f"{{}}{fs}".format, self))