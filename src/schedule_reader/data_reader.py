"""
A function to read the .DATA file, look for schedule section and return a dictionary of keywords and its records on order of appearance.

developed by: Martin Araya
email: martinaraya@gmail.com
"""

from .counter import Counter
from .helpers import remove_inline_comment
from .property_keywords import expand_keyword
from .time_parser import tstep_to_dates, time_to_dates
from os.path import exists

__version__ = '0.7.16'
__release__ = 20260503

def read_data(filepath: str, *, encoding: str='cp1252', verbose: bool=False,
              start_date: str=None, paths: dict={}, folder: str=None, counter: Counter=None, main=True,
              concatenate_lines=True) -> dict:
    """
    reads the .DATA file, look for schedule section and returns a dictionary of keywords and its records on order of appearance.

    Params:
        filepath: str
            the path to the .DATA or schedule include file
        paths: dict {str: str}, optional
            dictionary of the paths described by PATHS keyword. If the .DATA is provided this data is automatically extracted.
        start_date: str, optional
            the start date of the simulation
            if None, it will be read from keyword START or set by default to 01 JAN 1900
        folder: str, optional
            tha absolute path to the folder where the .DATA file is located. If the .DATA is provided this data is automatically extracted.
        encoding: str
            The encoding format of input text files. For files with especial characters, it might be convenient to use 'cp1252' or 'latin1'.
        verbose: bool
            set it False to skip printing messages.
        counter: an instance of the Counter class, should not be provided by the user!
            internal counter provided by the same function recursive calls when reading include files.

    Return:
        dict of dicts of keywords and their records
            {i: {keyword: [records]}}
    """

    def _keyword():
        return datafile[line].split()[0].upper()

    def _keyword_end():
        if line >= len(datafile):
            return True
        return datafile[line].strip().startswith('/')
    
    def _keyword_end_1record():
        return datafile[line].strip().endswith('/')

    def _comment_line():
        return datafile[line].strip().startswith('--')

    def _empty_line():
        return len(datafile[line].strip()) == 0

    def _line_data():
        return _this_line().rstrip('/ ')
    
    def _this_line():
        return remove_inline_comment(datafile[line])

    def _last_date():
        extracted_dates = [k_ for k_ in extracted
                           if list(extracted[k_].keys())[0] == 'DATES' and extracted[k_]['DATES'] is not False]
        if len(extracted_dates) == 0:
            return start_date
        else:
            return extracted[max(extracted_dates)]['DATES']

    skip0_keywords = ('ECHO', 'NOECHO', 'SKIPREST', 'ENDSKIP', 'RPTONLY', 'RPTONLYO', 'SAVENOW')
    skip_set_keywords = ('SKIP', 'SKIP100', 'SKIP300')
    skip1_keywords = ('NEXT', 'NEXTSTEP', 'LIFTOPT', 'GCONTOL', 'GUIDERAT', 'WLIMTOL', 'RPTSCHED', 'FILEUNIT', 'CVCRIT',
                      'TITLE')
    skip3_keywords = ('TUNING')

    # check file exists
    if not exists(filepath):
        newfilepath = f"{folder}{'' if folder.endswith('/') else '/'}{filepath.strip('"').strip("'").strip('"')}"
        if exists(newfilepath):
            filepath = newfilepath
        else:
            print(f"{folder}{'' if folder.endswith('/') else '/'}{filepath}")
            raise ValueError(f"The file doesn't exists: {filepath}")
    filepath = filepath.replace('\\', '/')
    if folder is None:
        folder = '/'.join(filepath.split('/')[:-1]) + '/'
        if verbose:
            print(f"parent folder: {folder}")

    # clean verbose parameter
    if verbose is None:
        verbose = True
    else:
        verbose = bool(verbose)

    # read and clean the main file
    if verbose:
        print('Reading the file:', filepath)
    with open(filepath, 'r', encoding=encoding) as f:
        datafile = f.readlines()
    datafile = [remove_inline_comment(line) for line in datafile]

    # initialize the counter
    if counter is None:
        counter = Counter()
    if verbose:
        keywords_before = counter.curr()
        print(f"{counter.curr()} keywords found until now")

    # if the file is the .DATA, look for START and PATHS keywords
    if filepath.upper().endswith('.DATA'):

        # looks for START
        if main and start_date is None and 'START' in ''.join(datafile):
            start_date = datafile[[remove_inline_comment(line) for line in datafile].index('START') + 1].replace('/', '').strip()
            if verbose:
                print(f"Found START date: {start_date}")

        # looks for PATHS and update dictionary if PATHS found
        if main and len(paths) == 0 and 'PATHS' in datafile:
            line = datafile.index('PATHS') + 1
            while not _keyword_end():
                paths.update({datafile[line].strip().strip('/').split()[0].strip("'"):
                                  datafile[line].strip().strip('/').split()[1].strip("'")})
                line += 1
            if verbose:
                print('Found PATHS keyword:\n', "\n   ".join([k + ":" + v for k, v in paths.items()]))

        # jump to SCHEDULE keyword line
        schedule_line = None
        if main and 'SCHEDULE' in datafile:
            schedule_line = datafile.index('SCHEDULE')
        else:
            schedule_line = [line.split()[0].upper().startswith('SCHEDULE') if len(line) > 0 else False for line in
                             datafile]
            schedule_line = schedule_line.index(True) if True in schedule_line else None
        if schedule_line is None:
            schedule_line = 0  # read the entire file
            # raise ValueError("'SCHEDULE' keyword not found in this DATA file.")
        if verbose:
            if main and schedule_line == 0:
                print(
                    f"SCHEDULE keyword not found in this DATA, will proceed to read everything line by line... it could take some time...")
            else:
                print(f"found SCHEDULE keyword in line {schedule_line}")
    else:
        schedule_line = 0

    # initialize the extracted dictionary, where every read keyword will be stored
    if not main:
        extracted = {}
    elif start_date is None:  # is main file
        # empty dictionary, START date by default and can be updated at the end of the loop
        extracted = {counter(): {'DATES': '01 JAN 1900'}}
        start_date = '01 JAN 1900'
        if verbose:
            print(f"START keyword not found, will start dates from default value '01 JAN 1900'")
    else:  # is main file and start_date is not None
        # START date is the first keyword in the dictionary
        extracted = {counter(): {'DATES': start_date}}

    # start reading the file, from the schedule_line if found
    line = schedule_line
    skip_ = False
    while line < len(datafile):  # read every line until the end


        # skip lines as indicated by SKIP keywords
        if skip_ and not datafile[line].upper().startswith('ENDSKIP'):
            line += 1
            continue
        elif skip_ and datafile[line].upper().startswith('ENDSKIP'):
            line += 1
            skip_ = False
            continue

        # skip empty and comment lines
        if _empty_line() or _comment_line():
            line += 1
            continue


        # terminate reading if END keyword is found
        if datafile[line].upper().startswith('END') and len(_line_data().split()[0]) == 3:
            if verbose:
                print(f"found END keyword in line {line}, terminating reading...")
            break


        # if a DATES is found
        elif datafile[line].upper().startswith('DATES'):
            line += 1
            if verbose:
                print("found DATES keyword")
                _counter0 = counter.curr() + 1

            # read all the dates within DATES until the closing /
            while not _keyword_end():
                # skip empty and commented lines
                if _empty_line() or _comment_line():
                    line += 1
                    continue

                extracted[counter()] = {'DATES': str(_line_data())}
                line += 1
            line += 1  # keyword end line
            if verbose:
                print(f" {' until '.join(set([extracted[_counter0]['DATES'], extracted[counter.curr()]['DATES']]))}")


        # if TSTEP is found, it will be converted to DATES using the last date found as start date
        elif datafile[line].upper().startswith('TSTEP'):
            line += 1
            if verbose:
                print("found TSTEP keyword")
                _counter0 = counter.curr() + 1

            # get the last date found to use as start date for TSTEP conversion
            last_date_for_tsteps = _last_date()
            # read all the TSTEP lines until the closing /
            read_tstep_lines = True
            while read_tstep_lines:
                # skip empty and commented lines
                if _empty_line() or _comment_line():
                    line += 1
                    continue

                tstep = [float(y) for x in _line_data().split() for y in expand_keyword(x).split()]
                dates = tstep_to_dates(tstep, last_date_for_tsteps)
                for i, date in enumerate(dates):
                    extracted[counter()] = {'DATES': str(date)}
                last_date_for_tsteps = dates.iloc[-1]  # update start date for next continuation line
                read_tstep_lines = not _keyword_end_1record()

            line += 1  # keyword end line
            if verbose:
                print(f" converted {len(tstep)} TSTEP to DATES, advancing date to {extracted[counter.curr()]['DATES']}")
        

        # if TIME is found, it will be converted to DATES using the START date as reference
        elif datafile[line].upper().startswith('TIME'):
            line += 1
            if verbose:
                print("found TIME keyword")
                _counter0 = counter.curr() + 1

            # TIME keyword specifies absolute times (days since START), unlike TSTEP which are increments
            # read all the TIME lines until the closing /
            read_time_lines = True
            while read_time_lines:
                # skip empty and commented lines
                if _empty_line() or _comment_line():
                    line += 1
                    continue

                time = [float(y) for x in _line_data().split() for y in expand_keyword(x).split()]
                dates = time_to_dates(time, start_date)
                for i, date in enumerate(dates):
                    extracted[counter()] = {'DATES': str(date)}
                read_time_lines = not _keyword_end_1record()

            line += 1  # keyword end line
            if verbose:
                print(f" converted {len(time)} TIME to DATES, advancing date to {extracted[counter.curr()]['DATES']}")


        # if COMPDAT is found
        elif datafile[line].upper().startswith('COMPDAT'):
            line += 1
            key_columns = 14
            if verbose:
                print("found COMPDAT keyword")
                _counter0 = counter.curr() + 1

            # read all the COMPDAT lines until the closing /
            while not _keyword_end():
                # skip empty or commented lines
                if _empty_line() or _comment_line():
                    line += 1
                    continue

                if not concatenate_lines and '/' not in datafile[line]:
                    raise ValueError(
                        f"Error format in keyword COMPDAT in line {line + 1} in file {filepath}. Missing / at the end of the line.")

                # append lines until line slash
                compdat_line = _line_data().split()
                while line < len(datafile) and '/' not in _this_line():
                    line += 1
                    if line < len(datafile):
                        compdat_line += _line_data().split()
                line += 1

                # complete default values at the end if requered
                if len(compdat_line) < key_columns:
                    compdat_line_expanded = []
                    for each in compdat_line:
                        if len(each) >= 2 and each.endswith('*') and each[:-1].isdigit():
                            compdat_line_expanded = compdat_line_expanded + (['1*'] * int(each[:-1]))
                        else:
                            compdat_line_expanded.append(each)
                    compdat_line_expanded = compdat_line_expanded + (
                                ['1*'] * (key_columns - len(compdat_line_expanded)))
                    compdat_line = compdat_line_expanded
                extracted[counter()] = {'COMPDAT': compdat_line}

            line += 1  # keyword end line
            if verbose:
                print(
                    f" for wells: {', '.join(set([extracted[i_]['COMPDAT'][0] for i_ in range(_counter0, counter.curr() + 1)]))}")


        # if COMPDATL or COMPDATM is found
        elif datafile[line].upper().startswith('COMPDATL') or datafile[line].upper().startswith('COMPDATM'):
            line += 1
            key_columns = 15
            if verbose:
                print("found COMPDATL keyword")
                _counter0 = counter.curr() + 1

            # read all the COMPDATL lines until the closing /
            while not _keyword_end():
                # skip empty or commented lines
                if _empty_line() or _comment_line():
                    line += 1
                    continue

                if not concatenate_lines and '/' not in datafile[line]:
                    raise ValueError(
                        f"Error format in keyword COMPDATL in line {line + 1} in file {filepath}. Missing / at the end of the line.")

                # append lines until line slash
                compdatl_line = _line_data().split()
                while line < len(datafile) and '/' not in _this_line():
                    line += 1
                    if line < len(datafile):
                        compdatl_line += _line_data().split()
                line += 1

                # complete default values at the end if requered
                if len(compdatl_line) < key_columns:
                    compdatl_line_expanded = []
                    for each in compdatl_line:
                        if len(each) >= 2 and each.endswith('*') and each[:-1].isdigit():
                            compdatl_line_expanded = compdatl_line_expanded + (['1*'] * int(each[:-1]))
                        else:
                            compdatl_line_expanded.append(each)
                    compdatl_line_expanded = compdatl_line_expanded + (
                                ['1*'] * (key_columns - len(compdatl_line_expanded)))
                    compdatl_line = compdatl_line_expanded
                extracted[counter()] = {'COMPDATL': compdatl_line}

            line += 1  # keyword end line
            if verbose:
                print(
                    f" for wells: {', '.join(set([extracted[i_]['COMPDATL'][0] for i_ in range(_counter0, counter.curr() + 1)]))}")


        # if WELSPECS is found
        elif datafile[line].upper().startswith('WELSPECS'):
            line += 1
            key_columns = 17
            if verbose:
                print("found WELSPECS keyword")
                _counter0 = counter.curr() + 1

            while not _keyword_end():

                # skip empty or commented lines
                if _empty_line() or _comment_line():
                    line += 1
                    continue

                if not concatenate_lines and '/' not in datafile[line]:
                    raise ValueError(
                        f"Error format in keyword WELSPECS in line {line + 1} in file {filepath}. Missing / at the end of the line.")
                
                # append lines until line slash
                welspecs_line = _line_data().split()
                while line < len(datafile) and '/' not in _this_line():
                    line += 1
                    if line < len(datafile):
                        welspecs_line += _line_data().split()
                line += 1

                # complete default values at the end if requered
                if len(welspecs_line) < key_columns:
                    welspecs_line_expanded = []
                    for each in welspecs_line:
                        if len(each) >= 2 and each.endswith('*') and each[:-1].isdigit():
                            welspecs_line_expanded = welspecs_line_expanded + (['1*'] * int(each[:-1]))
                        else:
                            welspecs_line_expanded.append(each)
                    welspecs_line_expanded = welspecs_line_expanded + (
                                ['1*'] * (key_columns - len(welspecs_line_expanded)))
                    welspecs_line = welspecs_line_expanded
                extracted[counter()] = {'WELSPECS': welspecs_line}

            line += 1  # keyword end line
            if verbose:
                print(
                    f" for wells: {', '.join(set([extracted[i_]['WELSPECS'][0] for i_ in range(_counter0, counter.curr() + 1)]))}")


        # if WELSPECL is found
        elif datafile[line].upper().startswith('WELSPECL'):
            line += 1
            key_columns = 18
            if verbose:
                print("found WELSPECL keyword")
                _counter0 = counter.curr() + 1

            while not _keyword_end():

                # skip empty or commented lines
                if _empty_line() or _comment_line():
                    line += 1
                    continue

                if not concatenate_lines and '/' not in datafile[line]:
                    raise ValueError(
                        f"Error format in keyword WELSPECL in line {line + 1} in file {filepath}. Missing / at the end of the line.")

                # append lines until line slash
                welspecl_line = _line_data().split()
                while line < len(datafile) and '/' not in _this_line():
                    line += 1
                    if line < len(datafile):
                        welspecl_line += _line_data().split()
                line += 1

                # complete default values at the end if requered
                if len(welspecl_line) < key_columns:
                    welspecl_line_expanded = []
                    for each in welspecl_line:
                        if len(each) >= 2 and each.endswith('*') and each[:-1].isdigit():
                            welspecl_line_expanded = welspecl_line_expanded + (['1*'] * int(each[:-1]))
                        else:
                            welspecl_line_expanded.append(each)
                    welspecl_line_expanded = welspecl_line_expanded + (
                                ['1*'] * (key_columns - len(welspecl_line_expanded)))
                    welspecl_line = welspecl_line_expanded
                extracted[counter()] = {'WELSPECL': welspecl_line}

            line += 1  # keyword end line
            if verbose:
                print(
                    f" for wells: {', '.join(set([extracted[i_]['WELSPECL'][0] for i_ in range(_counter0, counter.curr() + 1)]))}")


        # if WELLSPEC is found
        elif datafile[line].upper().startswith('WELLSPEC'):
            line += 1
            key_columns = 7
            if verbose:
                print("found WELLSPEC keyword")
                _counter0 = counter.curr() + 1

            while not _keyword_end():

                # skip empty or commented lines
                if _empty_line() or _comment_line():
                    line += 1
                    continue

                if not concatenate_lines and '/' not in datafile[line]:
                    raise ValueError(
                        f"Error format in keyword WELLSPEC in line {line + 1} in file {filepath}. Missing / at the end of the line.")

                # append lines until line slash
                wellspec_line = _line_data().split()
                while line < len(datafile) and '/' not in _this_line():
                    line += 1
                    if line < len(datafile):
                        wellspec_line += _line_data().split()
                line += 1

                # complete default values at the end if requered
                if len(wellspec_line) < key_columns:
                    wellspec_line_expanded = []
                    for each in wellspec_line:
                        if len(each) >= 2 and each.endswith('*') and each[:-1].isdigit():
                            wellspec_line_expanded = wellspec_line_expanded + (['1*'] * int(each[:-1]))
                        else:
                            wellspec_line_expanded.append(each)
                    wellspec_line_expanded = wellspec_line_expanded + (
                                ['1*'] * (key_columns - len(wellspec_line_expanded)))
                    wellspec_line = wellspec_line_expanded
                extracted[counter()] = {'WELLSPEC': wellspec_line}

            line += 1  # keyword end line
            if verbose:
                print(
                    f" for wells: {', '.join(set([extracted[i_]['WELLSPEC'][0] for i_ in range(_counter0, counter.curr() + 1)]))}")


        # if WCONPROD is found
        elif datafile[line].upper().startswith('WCONPROD'):
            line += 1
            key_columns = 20
            if verbose:
                print("found WCONPROD keyword")
                _counter0 = counter.curr() + 1

            while not _keyword_end():

                # skip empty or commented lines
                if _empty_line() or _comment_line():
                    line += 1
                    continue

                if not concatenate_lines and '/' not in datafile[line]:
                    raise ValueError(
                        f"Error format in keyword WCONPROD in line {line + 1} in file {filepath}. Missing / at the end of the line.")

                # append lines until line slash
                wconprod_line = _line_data().split()
                while line < len(datafile) and '/' not in _this_line():
                    line += 1
                    if line < len(datafile):
                        wconprod_line += _line_data().split()
                line += 1

                # complete default values at the end if requered
                if len(wconprod_line) < key_columns:
                    wconprod_line_expanded = []
                    for each in wconprod_line:
                        if len(each) >= 2 and each.endswith('*') and each[:-1].isdigit():
                            wconprod_line_expanded = wconprod_line_expanded + (['1*'] * int(each[:-1]))
                        else:
                            wconprod_line_expanded.append(each)
                    wconprod_line_expanded = wconprod_line_expanded + (
                                ['1*'] * (key_columns - len(wconprod_line_expanded)))
                    wconprod_line = wconprod_line_expanded
                extracted[counter()] = {'WCONPROD': wconprod_line}

            line += 1  # keyword end line
            if verbose:
                print(
                    f" for wells: {', '.join(set([extracted[i_]['WCONPROD'][0] for i_ in range(_counter0, counter.curr() + 1)]))}")


        # if WCONHIST is found
        elif datafile[line].upper().startswith('WCONHIST'):
            line += 1
            key_columns = 12
            if verbose:
                print("found WCONHIST keyword")
                _counter0 = counter.curr() + 1

            while not _keyword_end():

                # skip empty or commented lines
                if _empty_line() or _comment_line():
                    line += 1
                    continue

                if not concatenate_lines and '/' not in datafile[line]:
                    raise ValueError(
                        f"Error format in keyword WCONHIST in line {line + 1} in file {filepath}. Missing / at the end of the line.")

              # append lines until line slash
                wconhist_line = _line_data().split()
                while line < len(datafile) and '/' not in _this_line():
                    line += 1
                    if line < len(datafile):
                        wconhist_line += _line_data().split()
                line += 1

                # complete default values at the end if requered
                if len(wconhist_line) < key_columns:
                    wconhist_line_expanded = []
                    for each in wconhist_line:
                        if len(each) >= 2 and each.endswith('*') and each[:-1].isdigit():
                            wconhist_line_expanded = wconhist_line_expanded + (['1*'] * int(each[:-1]))
                        else:
                            wconhist_line_expanded.append(each)
                    wconhist_line_expanded = wconhist_line_expanded + (
                                ['1*'] * (key_columns - len(wconhist_line_expanded)))
                    wconhist_line = wconhist_line_expanded
                extracted[counter()] = {'WCONHIST': wconhist_line}

            line += 1  # keyword end line
            if verbose:
                print(
                    f" for wells: {', '.join(set([extracted[i_]['WCONHIST'][0] for i_ in range(_counter0, counter.curr() + 1)]))}")


        # if WCONINJE is found
        elif datafile[line].upper().startswith('WCONINJE'):
            line += 1
            key_columns = 15
            if verbose:
                print("found WCONINJE keyword")
                _counter0 = counter.curr() + 1

            while not _keyword_end():

                # skip empty or commented lines
                if _empty_line() or _comment_line():
                    line += 1
                    continue

                if not concatenate_lines and '/' not in datafile[line]:
                    raise ValueError(
                        f"Error format in keyword WCONINJE in line {line + 1} in file {filepath}. Missing / at the end of the line.")

                # append lines until line slash
                wconinje_line = _line_data().split()
                while line < len(datafile) and '/' not in _this_line():
                    line += 1
                    if line < len(datafile):
                        wconinje_line += _line_data().split()
                line += 1

                # complete default values at the end if requered
                if len(wconinje_line) < key_columns:
                    wconinje_line_expanded = []
                    for each in wconinje_line:
                        if len(each) >= 2 and each.endswith('*') and each[:-1].isdigit():
                            wconinje_line_expanded = wconinje_line_expanded + (['1*'] * int(each[:-1]))
                        else:
                            wconinje_line_expanded.append(each)
                    wconinje_line_expanded = wconinje_line_expanded + (
                                ['1*'] * (key_columns - len(wconinje_line_expanded)))
                    wconinje_line = wconinje_line_expanded
                extracted[counter()] = {'WCONINJE': wconinje_line}

            line += 1  # keyword end line
            if verbose:
                print(
                    f" for wells: {', '.join(set([extracted[i_]['WCONINJE'][0] for i_ in range(_counter0, counter.curr() + 1)]))}")


        # if WCONINJH is found
        elif datafile[line].upper().startswith('WCONINJH'):
            line += 1
            key_columns = 12
            if verbose:
                print("found WCONINJH keyword")
                _counter0 = counter.curr() + 1

            while not _keyword_end():

                # skip empty or commented lines
                if _empty_line() or _comment_line():
                    line += 1
                    continue

                if not concatenate_lines and '/' not in datafile[line]:
                    raise ValueError(
                        f"Error format in keyword WCONINJH in line {line + 1} in file {filepath}. Missing / at the end of the line.")

                # append lines until line slash
                wconinjh_line = _line_data().split()
                while line < len(datafile) and '/' not in _this_line():
                    line += 1
                    if line < len(datafile):
                        wconinjh_line += _line_data().split()
                line += 1

                # complete default values at the end if requered
                if len(wconinjh_line) < key_columns:
                    wconinjh_line_expanded = []
                    for each in wconinjh_line:
                        if len(each) >= 2 and each.endswith('*') and each[:-1].isdigit():
                            wconinjh_line_expanded = wconinjh_line_expanded + (['1*'] * int(each[:-1]))
                        else:
                            wconinjh_line_expanded.append(each)
                    wconinjh_line_expanded = wconinjh_line_expanded + (
                                ['1*'] * (key_columns - len(wconinjh_line_expanded)))
                    wconinjh_line = wconinjh_line_expanded
                extracted[counter()] = {'WCONINJH': wconinjh_line}

            line += 1  # keyword end line
            if verbose:
                print(
                    f" for wells: {', '.join(set([extracted[i_]['WCONINJH'][0] for i_ in range(_counter0, counter.curr() + 1)]))}")


        # if INCLUDE is found, will read the include file
        elif datafile[line].upper().startswith('INCLUDE'):
            line += 1
            if verbose:
                print(f"found INCLUDE file inside {filepath}:")

            # skip empty or commented lines
            while _empty_line() or _comment_line():
                line += 1

            include = datafile[line][::-1][datafile[line][::-1].index('/') + 1:][::-1].strip().strip("'")
            if verbose:
                print(include)
            
            if '$' in include:  # identify path from PATHS dictionary
                path_i = include.index('$')
                path_f = include.index('/', path_i)
                path_var = include[path_i: path_f]
                if path_var[1:] not in paths:
                    raise ValueError(f"Path variable '{path_var}' not defined in keyword PATHS.")
                include = folder + include[:path_i] + paths[path_var[1:]] + include[path_f:]
            elif include.startswith('../') or include.startswith('./'):
                include = folder + include

            # reading the include file recursively
            if verbose:
                print(f"reading include: {include}")
            include = read_data(include, paths=paths, folder=folder, verbose=verbose, start_date=_last_date(),
                                counter=counter, main=False)
            # load the returned keywords dictionary into this keywords dictionary
            extracted.update(include)
            line += 1


        # if RESERVOIRS is found, will read each reservoir data file recursively
        elif datafile[line].upper().startswith('RESERVOIRS'):
            line += 1
            if verbose:
                print(f"found RESERVOIRS keyword inside {filepath}:")

            reservoir_count = 0
            # read all reservoir records until the closing /
            while not _keyword_end():
                # skip empty or commented lines
                if _empty_line() or _comment_line():
                    line += 1
                    continue

                # parse the reservoir record
                record_fields = _line_data().split()
                if len(record_fields) < 3:
                    line += 1
                    continue
                
                # extract fields
                reservoir_file = record_fields[0].strip("'").strip('"')
                reservoir_name = record_fields[1].strip("'").strip('"') if len(record_fields) > 1 else ''
                num_ranks = int(record_fields[2]) if len(record_fields) > 2 else 1
                gpu_ids = [int(x) for x in record_fields[3:]] if len(record_fields) > 3 else []
                
                # store RESERVOIRS metadata
                extracted[counter()] = {
                    'RESERVOIRS': {
                        'file': reservoir_file,
                        'name': reservoir_name,
                        'num_ranks': num_ranks,
                        'gpu_ids': gpu_ids
                    }
                }
                
                if verbose:
                    print(f"  Reservoir: {reservoir_name} -> {reservoir_file}")
                
                # handle path substitution and relative paths (same as INCLUDE)
                if '$' in reservoir_file:  # identify path from PATHS dictionary
                    path_i = reservoir_file.index('$')
                    path_f = reservoir_file.index('/', path_i)
                    path_var = reservoir_file[path_i: path_f]
                    if path_var[1:] not in paths:
                        raise ValueError(f"Path variable '{path_var}' not defined in keyword PATHS.")
                    reservoir_file = folder + reservoir_file[:path_i] + paths[path_var[1:]] + reservoir_file[path_f:]
                elif reservoir_file.startswith('../') or reservoir_file.startswith('./'):
                    reservoir_file = folder + reservoir_file
                elif not reservoir_file.startswith('/'):
                    reservoir_file = folder + reservoir_file
                
                # reading the reservoir file recursively
                if verbose:
                    print(f"  reading reservoir data file: {reservoir_file}")
                reservoir_data = read_data(reservoir_file, paths=paths, folder=folder, verbose=verbose,
                                          start_date=_last_date(), counter=counter, main=False)
                # load the returned keywords dictionary into this keywords dictionary
                extracted.update(reservoir_data)
                reservoir_count += 1
                line += 1
            
            line += 1  # keyword end line
            if verbose:
                print(f"  loaded {reservoir_count} reservoir data files")


        # if SLAVES is found, will read each slave data file recursively
        elif datafile[line].upper().startswith('SLAVES'):
            line += 1
            if verbose:
                print(f"found SLAVES keyword inside {filepath}:")

            slave_count = 0
            # read all slave records until the closing /
            while not _keyword_end():
                # skip empty or commented lines
                if _empty_line() or _comment_line():
                    line += 1
                    continue

                # parse the slave record
                record_fields = _line_data().split()
                if len(record_fields) < 4:
                    line += 1
                    continue
                
                # extract fields
                slave_name = record_fields[0].strip("'").strip('"')
                basename = record_fields[1].strip("'").strip('"')
                hostname = record_fields[2].strip("'").strip('"') if len(record_fields) > 2 else '*'
                directory = record_fields[3].strip("'").strip('"') if len(record_fields) > 3 else ''
                num_procs = int(record_fields[4]) if len(record_fields) > 4 else 1
                
                # construct full path: directory/basename.DATA
                slave_file = f"{directory}{'/' if not directory.endswith('/') else ''}{basename}.DATA"
                
                # store SLAVES metadata
                extracted[counter()] = {
                    'SLAVES': {
                        'name': slave_name,
                        'file': slave_file,
                        'basename': basename,
                        'hostname': hostname,
                        'directory': directory,
                        'num_procs': num_procs
                    }
                }
                
                if verbose:
                    print(f"  Slave: {slave_name} -> {slave_file}")
                
                # handle path substitution and relative paths (same as INCLUDE)
                if '$' in slave_file:  # identify path from PATHS dictionary
                    path_i = slave_file.index('$')
                    path_f = slave_file.index('/', path_i)
                    path_var = slave_file[path_i: path_f]
                    if path_var[1:] not in paths:
                        raise ValueError(f"Path variable '{path_var}' not defined in keyword PATHS.")
                    slave_file = folder + slave_file[:path_i] + paths[path_var[1:]] + slave_file[path_f:]
                elif slave_file.startswith('../') or slave_file.startswith('./'):
                    slave_file = folder + slave_file
                elif not slave_file.startswith('/'):
                    slave_file = folder + slave_file
                
                # reading the slave file recursively
                if verbose:
                    print(f"  reading slave data file: {slave_file}")
                slave_data = read_data(slave_file, paths=paths, folder=folder, verbose=verbose,
                                      start_date=_last_date(), counter=counter, main=False)
                # load the returned keywords dictionary into this keywords dictionary
                extracted.update(slave_data)
                slave_count += 1
                line += 1
            
            line += 1  # keyword end line
            if verbose:
                print(f"  loaded {slave_count} slave data files")


        # read the listed keywords, that doesn't have and ending line with /
        elif _keyword() in skip_set_keywords:
            keyword_ = _keyword()
            if verbose:
                print(f"found {keyword_} keyword, activating skip mode")
            skip_ = True
            extracted[counter()] = {keyword_: None}
            line += 1
        elif _keyword() in skip0_keywords:
            keyword_ = _keyword()
            extracted[counter()] = {keyword_: None}
            if verbose:
                print(f"found {keyword_} keyword")
            line += 1
        elif _keyword() in skip1_keywords:
            keyword_ = _keyword()
            if verbose:
                print(f"found {keyword_} keyword")
            line += 1
            # skip empty or commented lines
            while _empty_line() or _comment_line():
                line += 1
            extracted[counter()] = {keyword_: _line_data()}
            line += 1
        elif _keyword() in skip3_keywords:
            keyword_ = _keyword()
            if verbose:
                print(f"found {keyword_} keyword")
            line += 1
            for i in range(3):
                # skip empty or commented lines
                while _empty_line() or _comment_line():
                    line += 1
                extracted[counter()] = {keyword_: _line_data()}
                line += 1


        # generic procedure to read any other COMPLETION, WELL, GROUP or USER DEFINED keyword (because they end with /)
        elif _keyword()[0] in 'CWGU':
            keyword_ = _keyword()
            line += 1
            _counter0 = counter.curr() + 1
            if verbose:
                print(f"found {keyword_} keyword")

            while not _keyword_end():

                # skip empty or commented lines
                if _empty_line() or _comment_line():
                    line += 1
                    continue

                # append lines until line slash
                keyword_line = _line_data().split()
                while line < len(datafile) and '/' not in _this_line():
                    line += 1
                    if line < len(datafile):
                        keyword_line += _line_data().split()

                # expand default values if needed
                keyword_line_expanded = []
                for each in keyword_line:
                    if len(each) >= 2 and each.endswith('*') and each[:-1].isdigit():
                        keyword_line_expanded = keyword_line_expanded + (['1*'] * int(each[:-1]))
                    else:
                        keyword_line_expanded.append(each)
                keyword_line = keyword_line_expanded
                extracted[counter()] = {keyword_: keyword_line}
                line += 1
            line += 1

            # expand default values at the end if needed
            keyword_max_ = [len(extracted[i_][keyword_]) for i_ in range(_counter0, counter.curr() + 1)]
            if len(keyword_max_) > 0:
                keyword_max_ = max([len(extracted[i_][keyword_]) for i_ in range(_counter0, counter.curr() + 1)])
                for each in range(_counter0, counter.curr() + 1):
                    keyword_line = extracted[each][keyword_]
                    if len(keyword_line) < keyword_max_:
                        extracted[each][keyword_] = keyword_line + (['1*'] * (keyword_max_ - len(keyword_line)))

            if verbose:
                print(
                    f" for: {', '.join(set([extracted[i_][keyword_][0] for i_ in range(_counter0, counter.curr() + 1)]))}")


        elif datafile[line].upper().startswith('VFPPROD'):
            keyword_ = _keyword()
            line += 1
            if verbose:
                print(f"found {keyword_} keyword")

            vfp_tables, vfp_records, vfp_line, vfp_data = 1, 6, [], ''
            while line < len(datafile) and vfp_tables > 0:

                if _empty_line() or _comment_line():
                    line += 1
                    continue

                vfp_data += datafile[line]

                if vfp_records > 0:
                    if '/' not in datafile[line]:
                        vfp_line += _line_data().split()
                    elif '/' in datafile[line]:
                        if vfp_records == 6:
                            vfp_line = []
                            vfp_records -= 1
                        else:
                            vfp_line += _line_data().split()
                            vfp_tables *= len(vfp_line)
                            vfp_line = []
                elif '/' in datafile[line]:
                    vfp_tables -= 1
                else:
                    pass
                line += 1
            extracted[counter()] = {keyword_: vfp_data}

        elif datafile[line].upper().startswith('VFPINJ'):
            keyword_ = _keyword()
            line += 1
            if verbose:
                print(f"found {keyword_} keyword")

            vfp_tables, vfp_records, vfp_line = 1, 3, []
            vfp_data = ''
            while line < len(datafile) and vfp_tables > 0:

                if _empty_line() or _comment_line():
                    line += 1
                    continue

                vfp_data += datafile[line]

                if vfp_records > 0:
                    if '/' not in datafile[line]:
                        vfp_line += _line_data().split()
                    elif '/' in datafile[line]:
                        if vfp_records == 3:
                            vfp_line = []
                            vfp_records -= 1
                        elif vfp_records == 2:
                            vfp_line += _line_data().split()
                            vfp_line = []
                            vfp_records -= 1
                        else:
                            vfp_line += _line_data().split()
                            vfp_tables = len(vfp_line)
                            vfp_line = []
                elif '/' in datafile[line]:
                    vfp_tables -= 1
                else:
                    pass
                line += 1
            extracted[counter()] = {keyword_: vfp_data}

        # skip everything else
        else:
            if verbose:
                print(f"skipping {datafile[line]}")
            line += 1

    if verbose:
        print(f"closing this file, {counter.curr() - keywords_before} keywords found here.")
        print()

    return extracted