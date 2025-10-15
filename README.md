# schedule_reader
A set of functions to read eclipse format DATA file and include files and extract well data from SCHEDULE section; like WELSPECS, COMPDAT, WCONHIST, WCONPROD or WLIST keywords.  
  
The following keywords are recognized and the corresponding parameters names are set as columns labels:
- WELSPECS with `welspec2df` 
- COMPDAT with `compdat2df`
- WCONHIST with `wconhist2df`
- WCONPROD with `wconprod2df`
- WCONINJH with `wconinjh2df`
- WCONINJE with `wconinje2df` 
- WLIST with `wlist2df`

function with the path to .DATA file or include file as argument
  
Any other SCHEDULE section keyword can be extracted, but the columns will no be labelled, using the function keyword2df providing the path to the file and requested keyword as arguments.

Returns a DataFrame with the extracted data, associated to its respective date from DATES keyword.
