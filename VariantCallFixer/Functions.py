

from typing import Generator
from VariantCallFixer.Globals import *
from VariantCallFixer.SampleData import SampleData

@lru_cache(300)
def rowFromBytes(row : bytes):
	from VariantCallFixer.RowDict import RowDict
	import itertools
	kwargs = {}
	try:
		rowIter = iter(row.decode("utf-8").rstrip().split("\t"))
		for name, convFunc, col in zip(COLUMNS, COLUMN_TYPES, rowIter):
			if col == ".":
				kwargs[name] = None
			else:
				kwargs[name] = convFunc(col)
		try:
			FORMAT, *SAMPLES = rowIter
		except:
			pass
		else:
			kwargs["FORMAT"] = FORMAT.split(":")
			kwargs["SAMPLES"] = []
			for sampleString in SAMPLES:
				kwargs["SAMPLES"].append({})
				for name, valueString in zip(FORMAT.split(":"), sampleString.split(":")):
					kwargs["SAMPLES"][-1][name] = valueString
				kwargs["SAMPLES"][-1] = SampleData(**kwargs["SAMPLES"][-1])
			kwargs["SAMPLES"]
		finally:
			return RowDict(**kwargs)
	except:
		raise ValueError(f"Bad VCF row: {row!r}")

@overload
def openVCF(filename : str, mode : Literal["r"]) -> "ReadVCF": ...
@overload
def openVCF(filename : str, mode : Literal["w"]) -> "CreateVCF": ...
def openVCF(filename : str, mode : str):
	from VariantCallFixer.ReadVCF import ReadVCF
	from VariantCallFixer.CreateVCF import CreateVCF
	match mode:
		case "r":
			return ReadVCF(filename=filename)
		case "w":
			return CreateVCF(filename=filename)
		case "a":
			raise NotImplementedError("Appending/building on a .vcf file is not yet implemented!")
		case _:
			raise ValueError(f"openVCF: {mode!r} is not a recognized file mode.")

@overload
def getSNPdata(filename, key : str="POS") -> Generator[tuple[int,str], None, None]: ...
@overload
def getSNPdata(filename, key : list) -> Generator[tuple[tuple[Any],str], None, None]: ...
@overload
def getSNPdata(filename, key : str, values : str="REF") -> Generator[tuple[Any,str], None, None]: ...
@overload
def getSNPdata(filename, key : list, values : list[str]=["REF"]) -> Generator[tuple[tuple[Any],tuple[int,tuple[str|int|tuple[str]|dict]]], None, None]: ...
def getSNPdata(filename, key="POS", values="REF"):
	'''getSNPdata() -> {POS : (CALLED, ...)}
	'''
	with openVCF(filename, "r") as reader:
		if isinstance(key, Iterable):
			if isinstance(values, Iterable):
				func = lambda entry : (tuple(entry[k] for k in key), tuple(entry[v] for v in values))
			else:
				func = lambda entry : (tuple(entry[k] for k in key), entry[values])
		else:
			if isinstance(values, Iterable):
				func = lambda entry : (entry[key], tuple(entry[v] for v in values))
			else:
				func = lambda entry : (entry[key], entry[values])
			
		for entry in reader:
			yield func(entry)

try:
	from VariantCallFixer.ReadVCF import ReadVCF
	from VariantCallFixer.CreateVCF import CreateVCF
except ImportError:
	pass