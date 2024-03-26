
from VariantCallFixer.Globals import *
from VariantCallFixer.Functions import splitRow, rowFromBytes

class ReadVCF(VCFIOWrapper):

	header : dict[str,str]
	entryRows : list[int]
	rowsBySelection : dict[str,dict[str|int, set[int]]]
	columns : list[str] = ["CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO", "FORMAT", "SAMPLES"]

	sampleNames : list[str]
	byteToRow : dict[int,int]
	file : BinaryIO

	def __init__(self, filename : str):
		super().__init__(filename, mode="rb")

		self.header = {}
		self.entryRows = []
		self.byteToRow = {}
		self.rowsBySelection = {c:{} for c in self.columns}

		startOfRow = 0
		rowNumber = 0
		# Pass through Header
		for row in self.file:
			rowLength = len(row)
			rowNumber += 1
			self.byteToRow[startOfRow] = rowNumber
			if row.startswith(b"##"):
				name, value = row[2:].split(b"=", 1)
				if name.isalnum():
					self.header[name.decode("utf-8").strip()] = value.decode("utf-8").strip()
			elif row.startswith(b"#"):
				l = len("#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO")
				if len(row) >= l and len(row) <= l+3:
					self.sampleNames = []
				else:
					self.sampleNames = row[l+len("FORMAT	"):].strip().decode("utf-8").split("\t")
				startOfRow += rowLength
				break

			startOfRow += rowLength

		# Start Indexing the entries.
		for row in self.file:
			rowDict = splitRow(row)

			if rowDict is None:
				LOGGER.error(f"Bad row in VCF file '{filename}' Row #{rowNumber}")
				raise ValueError(f"Bad row in VCF file '{filename}' Row #{rowNumber}")
			
			rowLength = len(row)
			rowNumber += 1
			self.byteToRow[startOfRow] = rowNumber
			self.entryRows.append(startOfRow)

			for key in self.columns:
				if key in ["INFO", "FORMAT", "SAMPLES"]: continue

				if key in rowDict:
					try:
						if rowDict[key] in self.rowsBySelection[key]:
							self.rowsBySelection[key][rowDict[key]].add(startOfRow)
						else:
							self.rowsBySelection[key][rowDict[key]] = {startOfRow}
					except TypeError:
						# list is not hashable, skip those for now.
						pass

			startOfRow += rowLength

	def __iter__(self):
		if len(self.entryRows) > 0:
			self.file.seek(self.entryRows[0])
			return (rowFromBytes(row.rstrip()) for row in self.file)
		else:
			return iter([])

	def where(self, *args, **kwargs) -> list[RowDict]:
		"""```python
		def where(self,
			CHROM : str | list[str],
			POS : int | list[int],
			ID : str,
			REF : str | list[str],
			ALT : str | list[str],
			QUAL : int | list[int],
			FILTER : str | list[str],
			INFO : tuple[str,str,Any] | list[tuple[str,str,Any]],
			FORMAT : tuple[str,str,Any] | list[tuple[str,str,Any]],
			rawOut : bool=False) -> list[RowDict]:
		```
		Gets dictionary of VCF row values, interpreted into pythonic types as well as it can. Dictionary can be
		queried using keys (or attributes) of the same names as the keyword-arguments for this method.
		
		INFO and FORMAT selectors are not yet implemented!
		"""


		rawOut = kwargs.pop("rawOut", False)
		
		if not set(kwargs.keys()).issubset(self.columns):
			raise TypeError(f"ReadVCF.where() got (an) unexpected keyword argument(s) {', '.join(set(kwargs.keys()).difference(self.columns))}'")
		elif len(args)>0 and set(self.columns[:len(args)]).issubset(kwargs.keys()):
			raise TypeError(f"ReadVCF.where() was given values for a column through both positional and keyword arguments. Offending Columns: {', '.join(set(self.columns[:len(args)]).intersection(kwargs.keys()))}")
		
		flags = dict(zip(self.columns, args)) | kwargs
		if len(flags) == 0:
			LOGGER.debug("ReadVCF.where() not given any keyword arguments to search by.")
			return None
		
		# Needs to find intersect of row sets.
		sets : list[set] = []
		for flag, value in flags.items():
			if type(value) is list:
				s = set()
				for key in value:
					s |= self.rowsBySelection[flag][key]
				sets.append(s)
			else:
				sets.append(self.rowsBySelection[flag][value])
		
		try:
			rowStarts = sorted(list(set.intersection(*sets)))
		except:
			LOGGER.warning("ReadVCF.where() was unable to find any rows that match the given query.")
			rowStarts = []
		
		rows : list = []
		for rowStart in rowStarts:
			self.file.seek(rowStart)
			try:
				if not rawOut:
					rows.append(rowFromBytes(self.file.readline().rstrip()))
				else:
					rows.append(self.file.readline().rstrip().decode("utf-8"))
			except:
				LOGGER.error("Bad row in VCF file '{filename}' Row #{n}".format(filename=self.file.name, n=self.byteToRow[rowStart]))
				raise ValueError("Bad row in VCF file '{filename}' Row #{n}".format(filename=self.file.name, n=self.byteToRow[rowStart]))

		return rows