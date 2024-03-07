

from VariantCallFixer.Globals import *

class CreateVCF(VCFIOWrapper):
	meta : list[str]
	header : list[str] # Header for the VCF, contains names of samples and other columns

	def __init__(self, filename : str, referenceFile, newline : str="\n", chrom : str=None):
		super().__init__(filename, mode="w")
		self.newline = newline
		
		self.header = VCF_HEADER.format(chrom=chrom or open(referenceFile, "r").readline()[1:].split()[0], dateYYYYMMDD="{:0>4}{:0>2}{:0>2}".format(*(time.localtime()[:3])), refPath=referenceFile)
		self.file.write(self.header)
			
	def add(self, CHROM : str=".", POS : str=".", ID : str=".", REF : str=".", ALT : str=".", QUAL : str=".", FILTER : str=".", INFO : str="."):
		self.file.write( f"{CHROM}\t{POS}\t{ID}\t{REF}\t{ALT}\t{QUAL}\t{FILTER}\t{INFO}\n")