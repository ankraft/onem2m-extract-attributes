#
#	extractAttributes.py
#
#	(c) 2021 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	Extract attribute shortnames and other information from oneM2M's specification Word documents.
#

from __future__ import annotations
import argparse, json, csv, os
from copy import deepcopy
from dataclasses import dataclass, asdict
from typing import Any, List, Dict, Set, Union
from docx import Document
from docx.table import Table
import docx.opc.exceptions
from unidecode import unidecode
from rich.console import Console
from rich.progress import Progress, TextColumn, BarColumn
from rich.console import Console
from rich.table import Table


# TODO Table/output sorting choices

@dataclass
class AttributeTable:
	headers:list
	attribute:int
	shortname:int
	occursIn:int
	category:str

@dataclass
class Attribute:
	"""	Datastruture for an attribute, including shortname, longname, category etc.
	"""
	shortname: str
	attribute: str
	occurences:int
	occursIn:Set
	categories:Set
	documents:Set

	def asDict(self) -> dict:
		"""	Return this dataclass as a dictionary.
		"""
		return 	{	'shortname' :	self.shortname,
					'attribute' :	self.attribute,
					'occursIn' :	[ v for v in self.occursIn ],
					'categories' :	[ v for v in self.categories ],
					'documents' :	[ v for v in self.documents ]
				}

Attributes = Dict[str, Attribute]

#	Rich console for pretty printing
console = Console()

#	List of AttributeTable that define the various table headers to find the shortname tables inside the documents, and the
# 	offsets for the shortname, attribute, etc columns. 
#
# 	The following definitions may need to be updated and extended when new tables are added to the specification documents.

attributeTables:list[AttributeTable] = [

	# TS-0004
	AttributeTable(headers=['Parameter Name', 'XSD long name', 'Occurs in', 'Short Name'],	attribute=1, shortname=3, occursIn=2,  category='Primitive Parameters'),
	AttributeTable(headers=['Root Element Name', 'Occurs in', 'Short Name'], 				attribute=0, shortname=2, occursIn=1,  category='Primitive Root Elements'),
	AttributeTable(headers=['Attribute Name', 'Occurs in', 'Short Name'], 					attribute=0, shortname=2, occursIn=1,  category='Resource Attributes'),
	AttributeTable(headers=['Resource Type Name', 'Short Name'], 							attribute=0, shortname=1, occursIn=-1, category='Resource Types'),
	AttributeTable(headers=['Member Name', 'Occurs in', 'Short Name'],						attribute=0, shortname=2, occursIn=1,  category='Complex Data Types'),
	AttributeTable(headers=['Member Name', 'Short Name'],									attribute=0, shortname=1, occursIn=-1, category='Trigger Payload Fields'),

	# TS-0023
	AttributeTable(headers=['Argument Name', 'Occurs in', 'Short Name'],					attribute=0, shortname=2, occursIn=1,  category='Action Arguments'),
	AttributeTable(headers=['Returned Value Name', 'Occurs in', 'Short Name'],				attribute=0, shortname=2, occursIn=1,  category='Action Return Values'),

	# TS-0022
	AttributeTable(headers=['Attribute Name', 'Occurs in', 'Short Name', 'Notes'], 			attribute=0, shortname=2, occursIn=1,  category='Common and Field Device Configuration'),
	AttributeTable(headers=['Member Name', 'Occurs in', 'Short Name', 'Notes'],				attribute=0, shortname=2, occursIn=1,  category='Complex Data Types'),
]



def findAttributeTable(table:Table) -> Union[AttributeTable, None]:
	"""	Search and return a fitting AttributeTable for the given document table.
		Return `None` if no fitting entry could be found.
	"""
	try:
		row0 = table.rows[0]
		for snt in attributeTables:
			if len(snt.headers) != len(row0.cells):
				continue
			idx = 0
			isMatch = True
			while isMatch and idx < len(snt.headers):
				isMatch = row0.cells[idx].text == snt.headers[idx]
				idx += 1
			if isMatch:
				return snt
	except:
		pass
	return None


def processDocuments(documents:list[str], outFilename:str, csvOut:bool) -> Attributes|None:

	docs 							= {}
	ptasks 							= {}
	snCount							= 0
	attributes:dict[str, Attribute]	= {}

	with Progress(	TextColumn('[progress.description]{task.description}'),
					BarColumn(),
					TextColumn('[progress.percentage]{task.percentage:>3.0f}%'),
					speed_estimate_period=2.0) as progress:

		# Preparing tasks for progress
		readTask 	= progress.add_task(f'Reading document{"s" if len(documents)>1 else ""} ...', total=len(documents))

		#
		#	Read the input documents and add tasks for each of them
		#

		for d in documents:
			try:
				docs[d] = Document(d)
				ptasks[d] = progress.add_task(f'Processing {d} ...', total=1000)
				progress.update(readTask, advance=1)
			except docx.opc.exceptions.PackageNotFoundError as e:
				progress.stop()
				progress.remove_task(readTask)
				console.print(f'[red]Input document "{d}" is not a .docx file')
				return None
			except Exception as e:
				progress.stop()
				progress.remove_task(readTask)
				console.print(f'[red]Error reading file "{d}"')
				console.print_exception()
				return None
		
		# Add additional task
		checkTask	= progress.add_task('Checking results ...', total=2)
		writeTask	= progress.add_task('Writing files ...', total=2+len(documents) if csvOut else 2)

		#
		#	Process documents
		#

		for docName, doc in docs.items():
			processTask = ptasks[docName]

			# Process the document
			progress.update(processTask, total=len(doc.tables))
			for table in doc.tables:
				progress.update(processTask, advance=1)
				if (snt := findAttributeTable(table)) is None:
					continue

				headersLen = len(snt.headers)
				for r in table.rows[1:]:
					cells = r.cells
					if cells[0].text.lower().startswith('note:') or len(r.cells) != headersLen:	# Skip note cells
						continue

					# Extract names and do a bit of transformations
					attribute = unidecode(cells[snt.attribute].text).strip()
					shortname = unidecode(cells[snt.shortname].text.replace('*', '').lower())
					occursIn = map(str.strip, unidecode(cells[snt.occursIn].text).split(',')) if snt.occursIn > -1 else ['n/a']	# Split and strip 'occurs in' entries
					
					# Don't process empty shortnames
					if not shortname:	
						break

					# Create or update entry for shortname
					if shortname in attributes:
						entry = attributes[shortname]
						for v in occursIn:
							entry.occursIn.add(v)
						entry.categories.add(snt.category)
						entry.documents.add(docName)
						entry.occurences += 1
					else:
						entry = Attribute(	shortname=shortname,
											attribute=attribute,
											occurences=1,
											occursIn=set([ v for v in occursIn ]),
											categories=set([ snt.category ]),
											documents=set([ docName ])
										)
					
					attributes[shortname] = entry
					snCount += 1
				continue

		#
		#	Further tests
		#
		progress.update(checkTask, advance=1)

		# count duplicates
		countDuplicates = 0
		for shortname,attribute in attributes.items():
			countDuplicates += 1 if attribute.occurences > 1 else 0
		progress.update(checkTask, advance=1)

		#
		#	generate outputs
		#

		# Write JSON output to a file
		progress.update(writeTask, advance=1)
		outFilename += '.json' if not outFilename.endswith('.json') else ''	# fix output filename's extension

		with open(outFilename, 'w') as jsonFile:
			json.dump([ v.asDict() for v in attributes.values()], jsonFile, indent=4)

		# Write output to CSV files
		if csvOut:
			for docName, doc in docs.items():			# Individually for each input file
				progress.update(writeTask, advance=1)
				# write a sorted list of attribute / shortnames to a csv file
				with open(f'{os.path.dirname(outFilename)}{os.sep}{docName.rsplit(".", 1)[0] + ".csv"}', 'w') as csvFile:
					csv.writer(csvFile).writerows(	
						sorted(
							[ [attr.attribute, attr.shortname] for attr in attributes.values() if docName in attr.documents ],
							key=lambda x: x[0].lower() ))

		progress.update(writeTask, advance=1)

		#
		# finished. print further infos
		#

		progress.stop()
		console.print(f'Processed short names:      {snCount}')
		if countDuplicates > 0:
			console.print(f'Duplicate definitions:      {countDuplicates}')

	return attributes


def printAttributeTables(attributes:Attributes, duplicatesOnly:bool=True) -> None:
	"""	Print the found attributes to the console. Optionally print only duplicate entries.
	"""
	table = Table(show_lines=True, border_style='grey27')
	table.add_column('attribute', no_wrap=True)
	table.add_column('shortname', no_wrap=True, min_width=6)
	table.add_column('category', no_wrap=False)
	table.add_column('document(s)', no_wrap=False)
	for sn, attribute in attributes.items():
		if attribute.occurences > 1:
			table.add_row(attribute.attribute, sn, ', '.join(attribute.categories), f'[red]{", ".join(attribute.documents)}')
		elif not duplicatesOnly:
			table.add_row(attribute.attribute, sn, ', '.join(attribute.categories), ', '.join(attribute.documents))
	console.print(table)



if __name__ == '__main__':

	# Parse command line arguments
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--outfile', '-o', action='store', dest='outFilename', default='attributes.json', help='specify output filename')
	parser.add_argument('--csv', '-c', action='store_true', dest='csvOut', default=False, help='additionally generate shortname csv files')
	
	listArgs = parser.add_mutually_exclusive_group()
	listArgs.add_argument('--list', '-l', action='store_true', dest='list', default=False, help='list all found attributes')
	listArgs.add_argument('--list-duplicates', '-ld', action='store_true', dest='listDuplicates', default=False, help='list only duplicate attributes')

	parser.add_argument('document', nargs='+', help='documents to parse')
	args = parser.parse_args()

	# Process documents and print output
	if (attributes := processDocuments(sorted(args.document), args.outFilename, args.csvOut)) is None:
		exit(1)
	if args.list or args.listDuplicates:
		printAttributeTables(attributes, args.listDuplicates)
