# oneM2M Extract Attributes

Extract attributes, short and long names, categories, and more from the oneM2M specification documents.

This script takes the oneM2M specification documents and searches for the short name definition tables. 
It then generates a JSON structure that contains the attributes, short names, categories and other information.
It optionally can also generate CSV (Comma Separated Values) files for easy mappings and can a report on duplicate attribute definitions.

## Installation

- The script requires [Python 3.8][python] or better to run.
- It is recommend to use a virtual environment like [pyenv][pyenv].
- Download or clone this repository.
- Install additionally required Python modules with the following command:

		python3 -m pip install -r requirements.txt


## Running

### Preparing the input documents

The script accepts documents in **docx** format. If necessary existing documents need to be converted to this format, e.g. by opening and saving them as "docx" documents. Other formats, for example Word's old "doc" format, are not supported.

### Command line arguments

The following listing provides an overview and some explanations for 
```text
usage: extractAttributes.py [-h] [--outfile OUTFILENAME] [--csv] [--list | --list-duplicates] document [document ...]

positional arguments:
  document              documents to parse

optional arguments:
  -h, --help            show this help message and exit
  --outfile OUTFILENAME, -o OUTFILENAME
                        specify output filename (default: attributes.json)
  --csv, -c             additionally generate shortname csv files (default: False)
  --list, -l            list all found attributes (default: False)
  --list-duplicates, -ld
                        list only duplicate attributes (default: False)
```

### Examples

With the following command the script reads the document ```TS-0022-Field_Device_Configuration-V4_2_0.docx``` as input and generates the file ```attributes.json``` (the default) with the attribute definitions in the same directory.

> ```python3 src/extractAttributes.py TS-0022-Field_Device_Configuration-V4_2_0.docx```

The following command can be used to read and process all ```.docx``` documents in the same directory, and then generate the file ```oneM2M-attributes.json``` in the sub-directory *out*.

> ```python3 src/extractAttributes.py *.docx -o out/oneM2M-attributes.json```

The following command is similar to the previous example, but in addition also generates *CVS* files, one for each input document. These CSV files will have the same filenames as their respective input documents, but the extension ".csv" and are stored in the same location as other output documents.

> ```python3 src/extractAttributes.py *.docx --csv -o out/oneM2M-attributes.json```

With the next command one can, in addition to the attribute's JSON file, list the result on the screen. Duplicate definitions are marked in red.

> ```python3 src/extractAttributes.py *.docx --list```

This output could be to much when one only wants to check for duplicates. Therefore, the following command can be used to list only the duplicate definitions on the screen.

> ```python3 src/extractAttributes.py *.docx --list-duplicates```

<br/>

## Adapting the script for new and updated specification documents

The script identifies the relevant tables in the specification documents by searching for their headlines. When new tables are added to the specification documents the definitions found in the map ```attributeTables``` may need to be updated and extended.


## Changes

See the [CHANGELOG.md][changelog] file.


## License
This project is licensed under the terms of the [BSD 3-Clause License][bsd-3-clause].


[bsd-3-clause]: https://opensource.org/licenses/BSD-3-Clause
[changelog]: CHANGELOG.md
[pyenv]: https://github.com/pyenv/pyenv
[python]: https://www.python.org