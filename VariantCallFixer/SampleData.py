
from VariantCallFixer.Globals import *
from collections import UserDict

_T = TypeVar("_T")
_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")

class MathTuple(tuple):
	
	@overload
	def __add__(self : _T1, other : _T2) -> _T1: ...
	@overload
	def __add__(self : _T, other : _T) -> _T: ...
	def __add__(self, other):
		if isinstance(other, type(self)) or (isinstance(other, MathTuple) and len(self) == len(other)):
			return type(self)(x+y for x,y in zip(self, other))
		else:
			return type(self)(x+other for x in self)
		
	@overload
	def __radd__(self : _T1, other : _T2) -> _T1: ...
	@overload
	def __radd__(self : _T, other : _T) -> _T: ...
	def __radd__(self, other):
		if isinstance(other, type(self)) or (isinstance(other, MathTuple) and len(self) == len(other)):
			return type(self)(y+x for x,y in zip(self, other))
		else:
			return type(self)(other+x for x in self)
		
	@overload
	def __truediv__(self : _T1, other : _T2) -> _T1: ...
	@overload
	def __truediv__(self : _T, other : _T) -> _T: ...
	def __truediv__(self, other):
		if isinstance(other, type(self)) or (isinstance(other, MathTuple) and len(self) == len(other)):
			return type(self)(x/y for x,y in zip(self, other))
		else:
			return type(self)(x/other for x in self)
		
	@overload
	def __rtruediv__(self : _T1, other : _T2) -> _T1: ...
	@overload
	def __rtruediv__(self : _T, other : _T) -> _T: ...
	def __rtruediv__(self, other):
		if isinstance(other, type(self)) or (isinstance(other, MathTuple) and len(self) == len(other)):
			return type(self)(y/x for x,y in zip(self, other))
		else:
			return type(self)(other/x for x in self)
		
	@overload
	def __floordiv__(self : _T1, other : _T2) -> _T1: ...
	@overload
	def __floordiv__(self : _T, other : _T) -> _T: ...
	def __floordiv__(self, other):
		if isinstance(other, type(self)) or (isinstance(other, MathTuple) and len(self) == len(other)):
			return type(self)(x//y for x,y in zip(self, other))
		else:
			return type(self)(x//other for x in self)
		
	@overload
	def __rfloordiv__(self : _T1, other : _T2) -> _T1: ...
	@overload
	def __rfloordiv__(self : _T, other : _T) -> _T: ...
	def __rfloordiv__(self, other):
		if isinstance(other, type(self)) or (isinstance(other, MathTuple) and len(self) == len(other)):
			return type(self)(y//x for x,y in zip(self, other))
		else:
			return type(self)(other//x for x in self)
		
	@overload
	def __floordiv__(self : _T1, other : _T2) -> _T1: ...
	@overload
	def __floordiv__(self : _T, other : _T) -> _T: ...
	def __floordiv__(self, other):
		if isinstance(other, type(self)) or (isinstance(other, MathTuple) and len(self) == len(other)):
			return type(self)(x%y for x,y in zip(self, other))
		else:
			return type(self)(x%other for x in self)
		
	@overload
	def __rfloordiv__(self : _T1, other : _T2) -> _T1: ...
	@overload
	def __rfloordiv__(self : _T, other : _T) -> _T: ...
	def __rfloordiv__(self, other):
		if isinstance(other, type(self)) or (isinstance(other, MathTuple) and len(self) == len(other)):
			return type(self)(y%x for x,y in zip(self, other))
		else:
			return type(self)(other%x for x in self)
"""
AJ749949.2
29478
.
C
A,T,G
.
.
AS_SB_TABLE=126,124|0,0|0,0|0,0;DP=250;ECNT=1;MBQ=20,0,0,0;MFRL=179,0,0,0;MMQ=60,60,60,60;MPOS=50,50,50;POPAF=7.30,7.30,7.30;TLOD=-1.669e+00,-1.669e+00,-1.669e+00
GT		:	AD		:AF								:DP		:F1R2		:F2R1		:FAD		:SB
0/1/2/3	:250,0,0,0	:7.093e-03,7.093e-03,7.093e-03	:250	:69,0,0,0	:67,0,0,0	:137,0,0,0	:126,124,0,0
"""
class DataField(MathTuple):
	name : str
	sep : str = ","
	innerSep : str = None
	datatype : type = str
	def __init_subclass__(cls) -> None:

		cls.name = cls.__name__
		if cls.sep and len(cls.sep) > 1:
			cls.split = re.compile(f"([{cls.sep}])").split
		elif cls.sep:
			cls.split = re.compile(f"[{cls.sep}]").split
		
		if cls.innerSep and len(cls.innerSep) > 1:
			cls.innerSplit = re.compile(f"([{cls.innerSep}])").split
		elif cls.innerSep:
			cls.innerSplit = re.compile(f"[{cls.innerSep}]").split

		return super().__init_subclass__()
	
	def __new__(cls, string : str):
		if isinstance(string, str):
			if cls.sep and len(cls.sep) > 1:
				if cls.innerSep:
					return super().__new__(cls, map(lambda x:x[1] if x[0]%2 else MathTuple(map(cls.datatype, cls.innerSplit(x[1]))), enumerate(cls.split(string))))
				else:
					return super().__new__(cls, map(lambda x:x[1] if x[0]%2 else cls.datatype(x[1]), enumerate(cls.split(string))))
			elif cls.sep and cls.innerSep:
				return super().__new__(cls, map(lambda x:MathTuple(map(cls.datatype, cls.innerSplit(x))), cls.split(string)))
			elif cls.sep:
				return super().__new__(cls, map(cls.datatype, cls.split(string)))
			else:
				return super().__new__(cls, [cls.datatype(string)])
		else:
			return super().__new__(cls, string)
	
	def __str__(self):
		if self.sep and len(self.sep) > 1:
			if self.innerSep:
				return ''.join(map(lambda x:x[1] if x[0]%2 else self.innerSep.join(map(format, x[1])), enumerate(self)))
			else:
				return ''.join(map(format, self))
		elif self.sep and self.innerSep:
			return self.sep.join(map(lambda x:self.innerSep.join(map(format, x)), self))
		elif self.sep:
			return self.sep.join(map(format, self))
		else:
			return self.sep.join(map(format, self))
		

class NovelField(DataField): ...

class GT(DataField):
	sep = "|/"
	datatype = int

class AD(DataField):
	datatype = int

class AF(DataField):
	datatype = float

class DP(DataField):
	datatype = int

class F1R2(DataField):
	datatype = int

class F2R1(DataField):
	datatype = int

class FAD(DataField):
	datatype = int

class SB(DataField):
	datatype = int


class SampleData(dict):
	def __init__(self, _iterable : Iterable=None, /, **kwargs):
		if isinstance(_iterable, dict):
			_iterable = _iterable.items()
		elif _iterable is None:
			_iterable = kwargs.items()
		for name, valueString in _iterable:
			for subClass in DataField.__subclasses__():
				if name == subClass.__name__:
					self[name] = subClass(valueString)
					break
			else:
				self[name] = NovelField(valueString)
	
	@property
	def names(self):
		return ":".join(map(format, self.keys()))

	def __str__(self):
		return ":".join(map(format, self.values()))