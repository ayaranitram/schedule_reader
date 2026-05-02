# schedule_reader
A set of functions to read eclipse format DATA file and include files and extract well data from SCHEDULE section; like WELSPECS, COMPDAT, WCONHIST, WCONPROD or WLIST keywords.  
  
Using the following functions, the corresponding keywords are recognized and the corresponding parameters names are set as columns labels:
- DATES and TSTEP with `dates2df` (TSTEP are transformed into the corresponding datetime)
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
