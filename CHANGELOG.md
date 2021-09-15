[← README](README.md) 


# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2021-09-14

### Added	
- Added support for TS-0032's resource type short names.
- The output directory is created if it doesn't exist.
- If both *--csv* and *--list-duplicates* are specified together then a CSV file with the duplicate attributes is written as well.
- CSV files now have a header row.

### Changed
- The *--outdir* argument replaces the *--outFile* argument.
- Tables and CSV output are now sorted by attribute names
- In the generated *attributes.json* file: *categories*, *occursIn*, and *documents* are sorted.


## [1.0.2] - 2021-07-12

### Added	
- Added support for TS-0022's resource type short names.


## [1.0.1] - 2021-07-07

### Fixed
- Empty rows don't stop further table processing anymore.


## [1.0.0] - 2021-06-07

### Added
- Initial release
