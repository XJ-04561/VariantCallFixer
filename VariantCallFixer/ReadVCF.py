
from VariantCallFixer.Globals import *
import VariantCallFixer.Globals as Globals
from VariantCallFixer.Functions import rowFromBytes
from VariantCallFixer.HeaderEntries import HeaderEntry
from VariantCallFixer.VCFSection import VCFHeader

_BASE_FLAGS = {i:Ditto for i in range(10)}
_INDEX_TO_NAME = dict(enumerate(["CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO", "FORMAT", "SAMPLES"]))

class ReadVCF(VCFIOWrapper):

	header : dict[str,str]
	entryRows : list[int]
	entriesStart : int
	rowsBySelection : dict[str,dict[str|int, set[int]]]
	columns : list[str] = ["CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO", "FORMAT", "SAMPLES"]
	cols : int
	entries : int

	sampleNames : list[str]
	byteToRow : dict[int,int]
	file : BinaryIO

	def __init__(self, filename : str, *, logger : logging.Logger=None):
		super().__init__(filename, mode="rb", logger=logger)

		self.header = VCFHeader()
		self.entryRows = []
		self.byteToRow = {}
		self.rowsBySelection = {c:{} for c in self.columns}

		startOfRow = 0
		rowNumber = 0
		# Pass through Header
		for row in self.file:
			self.byteToRow[startOfRow] = rowNumber
			rowNumber += 1
			startOfRow += len(row)
			if row.startswith(b"##"):
				try:
					entry = HeaderEntry.parse(row.strip())
				except UnicodeEncodeError:
					raise UnicodeEncodeError("File contains utf-8 illegal characters.")
				else:
					self.header.append(entry)
			elif row.startswith(b"#"):
				_, *self.sampleNames = row.decode("utf-8")[len(COLUMN_HEADER):].rstrip().split("\t")
				self.cols = 8 + (1+len(self.sampleNames))*(bool(self.sampleNames))
				break
			else:
				raise ValueError(f"Entry row encountered before column header: {filename!r} Row #{rowNumber}")
		self.entriesStart = startOfRow

		# Start Indexing the entries.
		self.entries  = 0
		for row in self.file:
			if not row.strip():
				break
			
			self.byteToRow[startOfRow] = rowNumber
			self.entryRows.append(startOfRow)

			self.entries += 1
			rowNumber += 1
		
		# File should be EOF
		for row in self.file:
			self.LOG.error(f"Empty rows in VCF file must be at the end of the file. Row inside file content was empty: {filename!r} Row #{rowNumber}")
			raise ValueError(f"Empty rows in VCF file must be at the end of the file. Row inside file content was empty: {filename!r} Row #{rowNumber}")

	def __iter__(self) -> Generator["RowDict", None, None]:
		if self.entries > 0:
			self.file.seek(self.entryRows[0])
			for i, row in zip(range(self.entries), self.file):
				yield rowFromBytes(row.rstrip())
	
	@overload
	def __getitem__(self, key : tuple) -> Generator[tuple[Any], None, None]: ...
	@overload
	def __getitem__(self, key : Any) -> Generator[Any, None, None]: ...
	def __getitem__(self, key):
		if isinstance(key, tuple):
			for row in self:
				yield tuple(row.get(k) for k in key)
		else:
			for row in self:
				yield row.get(key)

	@overload
	def where(self, *, CHROM : str, POS : int, ID : str, REF : str, ALT : str|Iterable[str], QUAL : int, FILTER : str) -> list["RowDict"]: ...
	def where(self, **kwargs):
		"""Gets dictionary of VCF row values, interpreted into pythonic types as well as it can. Dictionary can be
		queried using keys (or attributes) of the same names as the keyword-arguments for this method.
		"""

		if not self.entries:
			return []
		
		if "ALT" in kwargs and not isinstance(kwargs["ALT"], str):
			kwargs["ALT"] = ", ".join(kwargs["ALT"])
		
		criteria = {name:str(kwargs[name]).encode("utf-8") for name in kwargs}
		
		self.file.seek(self.entriesStart)
		results = []
		for i, row in zip(range(self.entries), self.file):
			if all(COLUMNS[j] not in kwargs or value == criteria[COLUMNS[j]] for j, value in zip(range(7), row.rstrip().split(b"\t"))):
				results.append(rowFromBytes(row.rstrip()))

		return results

try:
	from VariantCallFixer.RowDict import RowDict
except ImportError:
	pass