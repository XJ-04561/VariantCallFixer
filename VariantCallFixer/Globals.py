
from typing import TextIO, BinaryIO, overload
import time, logging

EXAMPLE_VCF_HEADER = """##fileformat=VCFv4.3
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

VCF_HEADER = """##fileformat=VCFv4.3
##fileDate={dateYYYYMMDD}
##source=MetaCanSNPer
##reference=file://{refPath}
##contig=<ID={chrom},URL=file://{refPath}>
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO
"""

COLUMNS = ["CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO"]
OPTIONAL_COLUMNS = ["FORMAT"]
VCF_ROW =       "{CHROM}	{POS}	{ID}	{REF}	{ALT}	{QUAL}	{FILTER}	{INFO}"
SEPARATORS = [(0, ";"), (1, ":"), (2, "|"), (3, ",")]
CONDITIONS = {">":"__gt__", "<":"__lt__", ">=":"__ge__", "<=":"__le__", "==":"__eq__", "!=":"__ne__"}
LOGGER = logging.Logger("VariantCallFixer")


class VCFIOWrapper:
	file : BinaryIO|TextIO

	def __init__(self, filename, mode):
		LOGGER.debug(f"Opening vcf file: open({filename!r}, {mode!r})")
		self.file = open(filename, mode)
	
	def __del__(self):
		try:
			self.file.close()
		except:
			pass

	def __enter__(self):
		return self
	
	def __exit__(self, *args, **kwargs):
		self.file.close()
	
	def close(self):
		self.file.close()

class RowDict(dict): pass
class ReadVCF(VCFIOWrapper): pass
class CreateVCF(VCFIOWrapper): pass