
from VariantCallFixer.Globals import *
from VariantCallFixer.RowDict import RowDict
from VariantCallFixer.Functions import splitRow, rowFromBytes

class ReadVCF(VCFIOWrapper):
	entryRows : list[int]
	rowsBySelection : dict[str,dict[str|int, set[int]]]
	columns : list[str] = ["CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO", "FORMAT", "SAMPLES"]

	sampleNames : list[str]
	byteToRow : dict[int,int]

	def __init__(self, filename : str):
		super().__init__(filename, mode="rb")

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
				pass # Meta row
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
			rowLength = len(row)
			rowNumber += 1
			self.byteToRow[startOfRow] = rowNumber
			self.entryRows.append(startOfRow)

			rowDict = splitRow(row)

			if rowDict is None:
				LOGGER.error("Bad row in VCF file '{filename}' Row #{n}".format(filename=filename, n=rowNumber))
				raise ValueError("Bad row in VCF file '{filename}' Row #{n}".format(filename=filename, n=rowNumber))
			
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
		self.file.seek(self.entryRows[0])
		return (rowFromBytes(row.rstrip()) for row in self.file)

	def where(self, CHROM : str | list[str]=None, POS : int|list[int]=None, REF : str | list[str]=None, ALT : str | list[str]=None, QUAL : int | list[int]=None, FILTER : str | list[str]=None, INFO : str | list[str]=None, FORMAT=None) -> list[RowDict]:
		"""Gets dictionary of VCF row values, interpreted into pythonic types as well as it can. Dictionary can be
		queried using keys (or attributes) of the same names as the keyword-arguments for this method."""
		
		flags = {c:locals()[c] for c in self.columns if locals()[c] is not None}
		if len(flags) == 0:
			LOGGER.debug("ReadVCF.where() not given any keyword arguments to search by.")
			return None
		
		# Needs to find intersect of row sets.
		sets : list[set] = []
		for flag, value in flags.items():
			if type(value) in [list, tuple]:
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
		
		rows : list[RowDict] = []
		for rowStart in rowStarts:
			self.file.seek(rowStart)
			try:
				rows.append(rowFromBytes(self.file.readline().rstrip()))
			except:
				LOGGER.error("Bad row in VCF file '{filename}' Row #{n}".format(filename=self.file.name, n=self.byteToRow[rowStart]))
				raise ValueError("Bad row in VCF file '{filename}' Row #{n}".format(filename=self.file.name, n=self.byteToRow[rowStart]))

		return rows