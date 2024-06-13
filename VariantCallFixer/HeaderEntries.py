
from VariantCallFixer.Globals import *

_NOT_SET = object()
_UNIQUES = ["fileformat", "fileDate", "source"]

class URL(str):
	"""Base class for all URL types. It is advised to use the specific URL-type intended directly, and
	not the base class."""
	
	PROTOCOL = ""

	def __new__(cls, data):
		if isinstance(data, URL):
			return data
		data = str(data)
		if cls is URL:
			for subClass in URL.__subclasses__():
				if data.startswith(subClass.PROTOCOL):
					return super().__new__(subClass, data)
			else:
				if os.path.exists(data):
					return super().__new__(FILE, FILE.PROTOCOL + data)
				else:
					raise NotImplementedError(f"Can't arbitrate URL type of {data!r}. If you know the intended URL type beforehand, use the correct subclass of URL instead of URL directly.")
		elif data.startswith(cls.PROTOCOL):
			return super().__new__(cls, data)
		else:
			return super().__new__(cls, cls.PROTOCOL + data)
	
	def __init_subclass__(cls) -> None:
		cls.PROTOCOL = f"{cls.__name__.lower()}://"

class FILE(URL): pass
class FTP(URL): pass
class HTTP(URL): pass
class HTTPS(URL): pass

class TagDict(dict):
	
	NAME_VALUE_PATTERN = re.compile(r"""(\w+?)[=](["].*?["]|['].*?[']|[^,]*)""", flags=re.DOTALL)
	FULL_PATTERN = re.compile(f"^[<]({NAME_VALUE_PATTERN.pattern}([,]{NAME_VALUE_PATTERN.pattern})*)[>]$")

	def __format__(self, fs):
		return f"<{','.join(f'{key}={value}' for key, value in self.items() if value is not _NOT_SET)}>"
	
	@classmethod
	def parse(cls, string : str) -> "TagDict":
		if (m := cls.FULL_PATTERN.fullmatch(string)):
			return cls(m.groups() for m in cls.NAME_VALUE_PATTERN.finditer(m.group(1)))
		else:
			return None

class HeaderEntry:

	name : str
	value : str|int|float|TagDict
	tagNames : None|tuple[str]
	unique : bool

	scalar : bool
	"""Reflects value of singlet/multiplet/tag"""
	singlet : bool
	"""Reflects value of scalar/multiplet/tag"""
	multiplet : bool
	"""Reflects value of scalar/singlet/tag"""
	tag : bool
	"""Reflects value of scalar/singlet/multiplet"""

	def __init__(self, arg=_NOT_SET, /, **kwargs):
		if arg is not _NOT_SET and self.singlet:
			self.value = arg
		elif arg is _NOT_SET and self.multiplet:
			self.value = TagDict()
			if self.tagNames:
				for name in self.tagNames:
					self.value[name] = kwargs.get(name, _NOT_SET)
			else:
				for name, value in kwargs.items():
					self.value[name] = value
		elif self.singlet:
			raise ValueError(f"{type(self).__name__!r} object only takes a single position argument to instantiate.")
		elif self.multiplet:
			raise ValueError(f"{type(self).__name__!r} object only takes keyword arguments to instantiate.")

	def __init_subclass__(cls) -> None:
		if not hasattr(cls, "name"):
			if cls.__name__.isupper():
				cls.name = cls.__name__
			else:
				cls.name = cls.__name__[0].lower() + cls.__name__[1:]
		if getattr(cls, "tagNames", False):
			cls.scalar = cls.singlet = False
			cls.multiplet = cls.tag = True
		else:
			cls.scalar = cls.singlet = True
			cls.multiplet = cls.tag = False
		cls.unique = cls.name in _UNIQUES

	def __str__(self):
		return f"{self.name}={self.value}"
	
	def __eq__(self, other):
		return hasattr(other, "__hash__") and hash(self) == hash(other)

	def __hash__(self):
		return hash(self.name) if self.unique else hash(str(self))
	
	@classmethod
	def parse(cls : type["HeaderEntry"], string : str|bytes) -> "HeaderEntry":
		if isinstance(string, bytes):
			string = string.decode("utf-8")
		nameString, valueString = string.lstrip("#").split("=", 1)

		if any(valueString.startswith(sc2.PROTOCOL) for sc2 in URL.__subclasses__()):
			value = URL(valueString)
		else:
			value = TagDict.parse(valueString) or valueString
		
		for subClass in cls.__subclasses__():
			if subClass.name == nameString:
				entryType = subClass
				break
		else:
			isDict = isinstance(value, TagDict)
			entryType = type(nameString.capitalize(), (cls,), {
				"multiplet" : isDict, "tag" : isDict,
				"singlet" : not isDict, "scalar" : not isDict})
		
		if entryType.multiplet:
			return entryType(**value)
		else:
			return entryType(value)

class Fileformat(HeaderEntry):
	def __init__(self, value : str="VCFv4.3", /): super().__init__(value)
class FileDate(HeaderEntry):
	
	@overload
	def __init__(self, /):
		"""Use the current local date."""
	@overload
	def __init__(self, datetime : float|int|str, /):
		"""Use a specific time string or create string from seconds converted to local time."""
	def __init__(self, datetime : float|int|str=_NOT_SET, /):
		if datetime is _NOT_SET:
			self.value = "{:0>4}{:0>2}{:0>2}".format(*(time.localtime()[:3]))
		elif isinstance(datetime, str):
			self.value = datetime
		else:
			self.value = "{:0>4}{:0>2}{:0>2}".format(*(time.localtime(datetime)[:3]))
class Source(HeaderEntry):
	def __init__(self, value : str, /): super().__init__(value)
class Reference(HeaderEntry):
	def __init__(self, path : URL|str, /):
		super().__init__(URL(path))
class Contig(HeaderEntry):
	
	tagNames = ("ID", "URL", "length", "assembly", "md5", "species", "taxonomy")

	@overload
	def __init__(self, *, ID : str=None, URL : URL=None, length : int=None, assembly : str=None, md5 : str=None, species : str=None, taxonomy : str=None): ...
	def __init__(self, /, **kwargs):
		super().__init__(**kwargs)
class Phasing(HeaderEntry):
	def __init__(self, phasing : str):
		super().__init__(phasing)
class INFO(HeaderEntry):
	tagNames = ("ID", "Number", "Type", "Description", "Source", "Version")
	@overload
	def __init__(self, *, ID : str, Number : int, Type : str, Description : str): ...
	@overload
	def __init__(self, *, ID : str, Number : int, Type : str, Description : str, Source : str=None, Version : str=None): ...
	def __init__(self, /, **kwargs):
		super().__init__(**kwargs)
class FILTER(HeaderEntry):
	tagNames = ("ID", "Description")
	@overload
	def __init__(self, *, ID : str, Description : str): ...
	def __init__(self, /, **kwargs):
		super().__init__(**kwargs)
class FORMAT(HeaderEntry):
	tagNames = ("ID", "Number", "Type", "Description")
	@overload
	def __init__(self, *, ID : str, Number : int, Type : str, Description : str): ...
	def __init__(self, /, **kwargs):
		super().__init__(**kwargs)
class ALT(HeaderEntry):
	tagNames = ("ID", "Description")
	@overload
	def __init__(self, *, ID : str, Description : str): ...
	def __init__(self, /, **kwargs):
		super().__init__(**kwargs)
class PEDIGREE(HeaderEntry):
	
	@overload
	def __init__(self, Name_0 : str, /): ...
	@overload
	def __init__(self, Name_0 : str, Name_1 : str, /): ...
	@overload
	def __init__(self, Name_0 : str, Name_1 : str, Name_2 : str, /): ...
	@overload
	def __init__(self, *names : str): ...
	def __init__(self, *names : str):
		super().__init__(**{f"Name_{i}":name for i, name in enumerate(names)})
class PedigreeDB(HeaderEntry):
	def __init__(self, path : URL|str, /):
		super().__init__(URL(path))

_EXAMPLE_VCF_HEADER = """
##fileformat=VCFv4.3
##fileDate={dateYYYYMMDD}
##source=MetaCanSNPer
##reference={referenceFile}
##contig=<ID={ID},length={length},assembly={assembly},md5={md5},species="{species}",taxonomy="{taxonomy}">
##phasing={phasing}
##INFO=<ID=NS,Number=1,Type=Integer,Description="Number of Samples With Data">
##INFO=<ID=DP,Number=1,Type=Integer,Description="Total Depth">
##INFO=<ID=AF,Number=A,Type=Float,Description="Allele Frequency">
##INFO=<ID=AA,Number=1,Type=String,Description="Ancestral Allele">
##FILTER=<ID=q10,Description="Quality below 10">
##FILTER=<ID=s50,Description="Less than 50% of samples have data">
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##FORMAT=<ID=GQ,Number=1,Type=Integer,Description="Genotype Quality">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Read Depth">
##FORMAT=<ID=BQ,Number=1,Type=Integer,Description="RMS base quality at this position">
##FORMAT=<ID=MQ,Number=2,Type=Integer,Description="RMS mapping quality, e.g. MQ=52">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT
"""