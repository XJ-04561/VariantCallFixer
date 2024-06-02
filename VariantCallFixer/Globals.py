
from typing import TextIO, BinaryIO, overload, Iterable, Any, Literal, TypeVar, Generator
import time, logging, os
from functools import lru_cache, partial

class VCFException(Exception): pass

COLUMNS = ["CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO"]
OPTIONAL_COLUMNS = ["FORMAT", "SAMPLES"]
FULL_COLUMNS = COLUMNS + OPTIONAL_COLUMNS
COLUMN_TYPES = [str, int, str, str, lambda x:tuple(map(str.strip, x.strip("[()]").split(","))), int, str, lambda x:dict(map(partial(str.split, sep="="), x.split(";")))]
VCF_ROW =       "{CHROM}	{POS}	{ID}	{REF}	{ALT}	{QUAL}	{FILTER}	{INFO}"
SEPARATORS = [(0, ";"), (1, ":"), (2, "|"), (3, ",")]
CONDITIONS = {">":"__gt__", "<":"__lt__", ">=":"__ge__", "<=":"__le__", "==":"__eq__", "!=":"__ne__"}
LOGGER = logging.Logger("VariantCallFixer", level=logging.FATAL)
COLUMN_HEADER = "#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO"

class _Ditto(type):
	def __eq__(self, other):
		return True
class Ditto(metaclass=_Ditto):
	def __eq__(self, other):
		return True
	
class VCFIOWrapper:
	
	LOG : logging.Logger = LOGGER.getChild("VCFIOWrapper")

	file : BinaryIO|TextIO

	def __init__(self, filename : str, mode : str, *, logger : logging.Logger=None):
		if logger is not None:
			self.LOG = logger
		self.LOG.debug(f"Opening vcf file: open({filename!r}, {mode!r})")
		self.file = open(filename, mode)
	
	def __init_subclass__(cls, *args, **kwargs) -> None:
		super().__init_subclass__(*args, **kwargs)
		cls.LOG = cls.LOG.getChild(cls.__name__)
	
	def __del__(self):
		try:
			self.file.close()
		except:
			pass

	def __enter__(self):
		return self
	
	def __exit__(self, *args, **kwargs):
		try:
			self.file.close()
		except:
			pass
	
	def close(self):
		self.file.close()