
from threading import Lock
from VariantCallFixer.Globals import *
from VariantCallFixer.HeaderEntries import *
from VariantCallFixer.VCFSection import VCFHeader, VCFBody

class CreateVCF(VCFIOWrapper):

	DUMPED : bool = False

	file : TextIO
	meta : list[str]
	header : list[str] # Header for the VCF, contains names of samples and other columns
	body : list[str]

	def __init__(self, filename : str, newline : str="\n", *, logger : logging.Logger=None):
		super().__init__(filename, mode="w", logger=logger)
		self.writeLock = Lock()
		self.newline = newline
		
		self.header = VCFHeader()
		self.body = VCFBody()
	
	def dump(self):
		with self.writeLock:
			if not self.DUMPED:
				if Fileformat("") not in self.header:
					self.header.insert(0, Fileformat("VCF4.3"))
				if FileDate() not in self.header:
					self.header.insert(1, FileDate())
				
				self.file.write(format(self.header, self.newline))
				self.file.write(COLUMN_HEADER)
				self.file.write((self.newline+format(self.body, self.newline)).rstrip())
				
				self.DUMPED = True
	
	@overload
	def add(self, *, CHROM : str=".", POS : str=".", ID : str=".", REF : str=".", ALT : str=".", QUAL : str=".", FILTER : str=".", INFO : str="."): ...
	@overload
	def add(self, *headerEntries : HeaderEntry): ...

	def add(self, *args, **kwargs):
		"""A shorthand for both .addMeta and .addEntry."""
		if args and kwargs:
			raise ValueError(f"VCFIOWrapper.add() takes either positional arguments or keyword arguments, not both.")
		elif args:
			return self.addMeta(*args)
		elif kwargs:
			return self.addEntry(**kwargs)
	
	def addMeta(self, *headerEntries : HeaderEntry):
		with self.writeLock:
			if self.DUMPED:
				raise IOError("Can't edit the header after having dumped header to file. This restriction is due to "
				  "having to re write all entries of the file in order to append to the header. If you wish to force "
				  "an entry into the header, create a new VCF with the proper header, and copy over the entries onto "
				  "the new file.")
			elif any(not isinstance(x, HeaderEntry) for x in headerEntries):
				raise TypeError(f"The header may only contain proper 'HeaderEntry' objects.")
			for entry in headerEntries:
				self.header.append(entry)

	def addEntry(self, *, CHROM : str=".", POS : str=".", ID : str=".", REF : str=".", ALT : str|Iterable[str]=".", QUAL : str=".", FILTER : str=".", INFO : str="."):
		with self.writeLock:
			if self.DUMPED:
				self.file.write( f"{self.newline}{CHROM}\t{POS}\t{ID}\t{REF}\t{ALT if isinstance(ALT, str) else ','.join(ALT)}\t{QUAL}\t{FILTER}\t{INFO}")
			else:
				self.body.append( f"{CHROM}\t{POS}\t{ID}\t{REF}\t{ALT if isinstance(ALT, str) else ','.join(ALT)}\t{QUAL}\t{FILTER}\t{INFO}")
	
	def save(self):
		"""Alias for "CreateVCF.dump()"."""
		self.dump()