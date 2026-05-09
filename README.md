# schedule_reader
A set of functions to read eclipse format DATA file and include files and extract well data from SCHEDULE section; like WELSPECS, COMPDAT, WCONHIST, WCONPROD or WLIST keywords.  
  
Using the following functions, the corresponding keywords are recognized and the corresponding parameters names are set as columns labels:
- DATES and TSTEP with `dates2df` (TSTEP are transformed into the corresponding datetime)
- DATES bounds with `get_start_date` and `get_end_date`
- WELSPECS with `welspec2df` 
- COMPDAT with `compdat2df`
- WCONHIST with `wconhist2df`
- WCONPROD with `wconprod2df`
- WCONINJH with `wconinjh2df`
- WCONINJE with `wconinje2df` 
- WLIST with `wlist2df`
  
These functions must be provided with the path to .DATA file or include file as argument.  
Any other SCHEDULE section keyword can be extracted, but the columns will not be labelled, using the function keyword2df providing the path to the file and requested keyword as arguments.

Returns a DataFrame with the extracted data, associated to its respective date from DATES keyword.

## Release 0.7.23 (2026-05-09)
- Improved 'C*', 'W*', 'G*', 'U*' keywords parser to better catch block terminations.

## Release 0.7.22 (2026-05-09)
- Improved keyword detection to avoid 

## Release 0.7.21 (2026-05-09)
- Refactored keyword matching logic to use exact matching via `_keyword()` instead of string prefix matching.
    - Fixed critical bug where `TSTEPCRIT` was incorrectly routed to `TSTEP` handler due to prefix collision.
    - Eliminated potential prefix collision issues with other keywords (`TIME`, `DATES`, `COMPDAT`, `WELSPEC*`, `WCON*`, etc.).
- Improved parser robustness through consistent exact keyword matching.

## Release 0.7.20 (2026-05-09)
- Normalized `dates2df()` to always return a pandas DataFrame.
- Normalized `get_start_date()` and `get_end_date()` to always return `pandas.Timestamp` (or `None`).

## Release 0.7.19 (2026-05-09)
- Added shape-based skip handling for ECHELON SCHEDULE keywords (`COLORING`, `SOLVER`, `TSTEPCRIT`, `TUNINGDP`, `TUNING`, `EXPTSOLV`).
- Improved block keyword termination handling to respect slash-terminated records with inline comments.
- Fixed `TUNING` parsing so all three records are captured correctly across continuation lines.

## Release 0.7.17 (2026-05-09)
- Fixed Python 3.7 compatibility in file path handling.
- Fixed a `TUNING` keyword membership bug caused by a one-item tuple typo.
- Declared the pandas dependency explicitly in package metadata.
- Added Python 3.12, 3.13, and 3.14 classifiers.
- Added a public `get_end_date` helper and documented the date helper API.

## Release 0.7.16 (2026-05-03)
- Fixed TSTEP date conversion to use cumulative increments.
- Fixed parsing issues in WELSPECL and WELLSPEC records.
- Improved robustness for SKIP blocks, EOF handling, and inline comment parsing.
- Fixed COMPDAT/COMPDATL default I/J resolution and several keyword-table None guards.
- Improved VFPINJ parsing initialization and general parser stability.

## To install this package:  
Install it from the <a href="https://pypi.org/project/schedule-reader/">pypi.org</a> repository:  
`pip install schedule-reader`  
or upgrade to the latest version:  
`pip install --upgrade schedule-reader`  
