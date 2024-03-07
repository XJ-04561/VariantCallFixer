
from VariantCallFixer.Globals import *
from VariantCallFixer.Functions import interpret

class RowDict(dict):
	CHROM : str
	POS : int
	ID : str
	REF : str
	ALT : list
	QUAL : int
	FILTER : str
	INFO : list
	FORMAT : list
	SAMPLES : list

	@property
	def CHROM(self): return self["CHROM"]
	@property
	def POS(self): return self["POS"]
	@property
	def ID(self): return self["ID"]
	@property
	def REF(self): return self["REF"]
	@property
	def ALT(self): return self["ALT"]
	@property
	def QUAL(self): return self["QUAL"]
	@property
	def FILTER(self): return self["FILTER"]
	@property
	def INFO(self): return self["INFO"]
	@property
	def FORMAT(self): return self["FORMAT"]
	@property
	def SAMPLES(self): return self["SAMPLES"]

	@INFO.setter
	def INFO(self, value : str):
		f = lambda p: (p[0], interpret(p[1]))
		self["INFO"] = dict([f(variable.split("=", maxsplit=1)) for variable in value.split(";")])

	@FORMAT.setter
	def FORMAT(self, value : str):
		self["FORMAT"] = value.split(":")

	@SAMPLES.setter
	def SAMPLES(self, samples : str):
		self["SAMPLES"] = [{k:v for k, v in zip(self["FORMAT"], interpret(sample))} for sample in samples]

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.INFO = self["INFO"]
		self.FORMAT = self["FORMAT"]
		self.SAMPLES = self["SAMPLES"]