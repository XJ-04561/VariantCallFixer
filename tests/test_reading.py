
from VariantCallFixer.Functions import *
from VariantCallFixer import *

def test_genotype_query():
	reader = openVCF("SCHUS4.2_FSC458.vcf", "r")
	byteReader = open("SCHUS4.2_FSC458.vcf", "rb")
	byteReader.seek(reader.entriesStart)
	for row, byteRow in zip(reader, byteReader):
		assert isinstance(row, RowDict)
		*_, format, sample = byteRow.strip().decode("utf-8").split("\t")
		assert row.SAMPLES[0].names == format
		assert ":".join(row.FORMAT) == format
		try:
			assert str(row.SAMPLES[0]) == sample
		except:
			for x,y in zip(str(row.SAMPLES[0]).split(":"), sample.split(":")):
				if "." not in x:
					assert x == y
		
		for name in row.FORMAT:
			assert row[name] == getattr(row, name)
			print(row[name])

def test_query_data():

	reader = openVCF("SCHUS4.2_FSC458.vcf", "r")
	outFile = open("SCHUS4.2_FSC458_bases.txt", "w")
	t = "\t"
	print(f"{t.join('ATCG')}\tCALLED BASE", file=outFile)
	for pos, chrom, baseCounts in reader["POS", "CHROM", "AD"]:
		assert isinstance(pos, int)
		assert isinstance(chrom, str)
		assert isinstance(baseCounts, tuple)
		assert len(baseCounts) == 1
		assert len(baseCounts[0]) == 4
		baseCounts = sum(baseCounts)
		print(f"{t.join(map(str, baseCounts))}\t{'ATCG'[max(enumerate(baseCounts), key=lambda x:x[1])[0]]}", file=outFile)