

from typing import Generator
from VariantCallFixer.Globals import *

def interpretIterable(string : str, seps=SEPARATORS):
	if string.startswith("[") and string.endswith("]"):
		string = string[1:-1]
		for i, s in seps:
			if s in string:
				return [interpret(subString, seps=seps[i+1:]) for subString in string.split(s)]
		return [interpret(string, seps=[])]
	else:
		for i, s in seps:
			if s in string:
				return [interpret(subString, seps=seps[i+1:]) for subString in string.split(s)]
		return string

def interpret(string : str|bytes, seps=SEPARATORS):
	"""Interprets anything with decimals in it or surrounded by [ ] as a list of items. Attempts to convert to int,
	then float, and then to decode with utf-8."""
	if type(string) is bytes:
		string : str = string.decode("utf-8")
	out = interpretIterable(string, seps=seps)
	if out != string:
		return out
	
	try:
		return int(string)
	except:
		pass

	try:
		return float(string)
	except:
		pass

	return string

def splitRow(row : bytes) -> dict[str,bytes]:
	cells = [interpret(cell, seps=[]) for cell in row.strip().split(b"\t")]
	rowDict = dict(zip(COLUMNS, cells))
	if len(cells) > len(COLUMNS):
		rowDict["FORMAT"] = cells[len(COLUMNS)]
		rowDict["SAMPLES"] = cells[len(COLUMNS)+1:]
	elif len(cells) < len(COLUMNS):
		return None
	
	return rowDict

def rowFromBytes(row : bytes):
	from VariantCallFixer.RowDict import RowDict
	rowDict = splitRow(row)
	if rowDict is None:
		LOGGER.warning("Bad row in VCF file.")
		raise ValueError("Bad row in VCF file.")
	return RowDict(rowDict)

def openVCF(filename : str, mode : str, referenceFile : str=None) -> ReadVCF|CreateVCF:
	from VariantCallFixer.ReadVCF import ReadVCF
	from VariantCallFixer.CreateVCF import CreateVCF
	if mode == "r":
		return ReadVCF(filename=filename)
	elif mode == "a":
		raise NotImplementedError("Appending/building on a .vcf file is not yet implemented!")
	elif mode == "w":
		if referenceFile is None:
			raise TypeError("Missing keyword argument 'referenceFile' required to create a .vcf")
		return CreateVCF(filename=filename, referenceFile=referenceFile)
	else:
		raise ValueError(f"openVCF: {mode!r} is not a recognized file mode.")

def getSNPdata(filename, key="POS", values=["REF"]) -> Generator[tuple[int,tuple[str,None]], None, None]:
	'''getSNPdata() -> {POS : (CALLED, ...)}
	'''
	with openVCF(filename, "r") as reader:
		for entry in reader:
			yield (entry[key], tuple(entry[value] for value in values))
			# Called Base is in the "REF" field