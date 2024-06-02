

from typing import Generator
from VariantCallFixer.Globals import *


# def interpretIterable(string : str, seps=SEPARATORS):
# 	if string.startswith("[") and string.endswith("]"):
# 		string = string[1:-1]
# 		for i, s in seps:
# 			if s in string:
# 				return [interpret(subString, seps=seps[i+1:]) for subString in string.split(s)]
# 		return [interpret(string, seps=[])]
# 	else:
# 		for i, s in seps:
# 			if s in string:
# 				return [interpret(subString, seps=seps[i+1:]) for subString in string.split(s)]
# 		return string

# def interpret(string : str|bytes, seps=SEPARATORS):
# 	"""Interprets anything with decimals in it or surrounded by [ ] as a list of items. Attempts to convert to int,
# 	then float, and then to decode with utf-8."""
# 	if type(string) is bytes:
# 		string : str = string.decode("utf-8")
# 	out = interpretIterable(string, seps=seps)
# 	if out != string:
# 		return out
	
# 	try:
# 		return int(string)
# 	except:
# 		pass

# 	try:
# 		return float(string)
# 	except:
# 		pass

# 	return string

# def splitRow(row : bytes) -> dict[str,bytes]:
# 	cells = [interpret(cell, seps=[]) for cell in row.strip().split(b"\t")]
# 	rowDict = dict(zip(COLUMNS, cells))
# 	if len(cells) > len(COLUMNS):
# 		rowDict["FORMAT"] = cells[len(COLUMNS)]
# 		rowDict["SAMPLES"] = cells[len(COLUMNS)+1:]
# 	elif len(cells) < len(COLUMNS):
# 		return None
	
# 	return rowDict

# @lru_cache(300)
# def rowFromBytes(row : bytes):
# 	from VariantCallFixer.RowDict import RowDict
# 	rowDict = splitRow(row)
# 	return RowDict(rowDict)

@lru_cache(300)
def rowFromBytes(row : bytes):
	from VariantCallFixer.RowDict import RowDict
	import itertools
	kwargs = {}
	try:
		row = row.decode("utf-8").rstrip()
		for col, name, convFunc in zip(row.split("\t", 8), COLUMNS, COLUMN_TYPES):
			if col == ".":
				kwargs[name] = None
			else:
				kwargs[name] = convFunc(col)
		# FORMAT, *SAMPLES = row.decode("utf-8").rstrip().split("\t")[len(COLUMNS):]
		# SAMPLES = []
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
def getSNPdata(filename, key : str="POS", values : Iterable[str]=["REF"]) -> Generator[tuple[int,tuple[str|int|tuple[str]|dict]], None, None]: ...
def getSNPdata(filename, key="POS", values=["REF"]):
	'''getSNPdata() -> {POS : (CALLED, ...)}
	'''
	with openVCF(filename, "r") as reader:
		if len(values) == 1:
			for entry in reader:
				yield (entry[key], entry[values[0]])
				# Called Base is in the "REF" field	
		else:
			for entry in reader:
				yield (entry[key], tuple(entry[value] for value in values))
				# Called Base is in the "REF" field

try:
	from VariantCallFixer.ReadVCF import ReadVCF
	from VariantCallFixer.CreateVCF import CreateVCF
except ImportError:
	pass