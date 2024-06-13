


def test_creation():
	
	from VariantCallFixer import openVCF, Fileformat, FileDate, Source, Reference, Contig, FILE

	f = openVCF("test.vcf", "w")

	f.addMeta(Fileformat("VCFv4.3"))
	f.addMeta(FileDate())
	f.addMeta(Source("MyApp"))
	f.addMeta(Reference(FILE("/home/XJ-04561/.local/MetaCanSNPer/References/francisella_tularensis/ASM898v1.fna")))
	f.addMeta(Contig(ID="AJ749949.2", URL=FILE("/home/XJ-04561/.local/MetaCanSNPer/References/francisella_tularensis/ASM898v1.fna")))

	assert not f.DUMPED

	f.dump()

	assert f.DUMPED

	exc = None
	try:
		f.addMeta()
	except IOError as e:
		exc = e
	assert isinstance(exc, IOError)

	f.addEntry(CHROM="AJ749949.2", POS=2385, REF="N", ALT=tuple("ATCG"))

	f.close()

def test_read():
	
	import time
	from VariantCallFixer import openVCF, ReadVCF, RowDict, Fileformat, FileDate, Source, Reference, Contig, FILE, TagDict

	f = openVCF("test.vcf", "r")

	assert f.header[Fileformat] == "VCFv4.3"
	assert f.header[FileDate] == "{:0>4}{:0>2}{:0>2}".format(*(time.localtime()[:3]))
	assert f.header[Source] == "MyApp"
	assert f.header[Reference] == FILE("/home/XJ-04561/.local/MetaCanSNPer/References/francisella_tularensis/ASM898v1.fna")
	
	expected = TagDict(ID="AJ749949.2", URL=FILE("/home/XJ-04561/.local/MetaCanSNPer/References/francisella_tularensis/ASM898v1.fna"))
	for key, value in expected.items():
		assert f.header[Contig][0][key] == value

	assert f.entries == 1

	assert list(f)

	rows = f.where(POS=2385)
	assert rows

	rows = f.where(POS=2385)
	assert rows
	assert rows[0]["REF"] == "N"
	assert set(rows[0]["ALT"]) == {"A", "T", "C", "G"}

	rows = f.where(POS=2384)
	assert not rows

	rows = f.where(POS=2386)
	assert not rows
