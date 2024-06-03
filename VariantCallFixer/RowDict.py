
from VariantCallFixer.Globals import *
from collections import UserDict

class RowDict(UserDict):
	CHROM : str
	POS : int
	ID : str
	REF : str
	ALT : tuple
	QUAL : int
	FILTER : str
	INFO : dict
	# FORMAT : list
	# SAMPLES : list

	def __getattr__(self, name):
		if name in FULL_COLUMNS:
			return self[name]
		else:
			# To get the same error message as usual.
			return self.__getattribute__(name)