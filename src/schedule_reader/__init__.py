"""
A set of functions to read and process the schedule data from a .DATA file, including functions to extract the WELSPECS, COMPDAT, WCONPROD, WCONINJE, WCONHIST, WCONINJH, and WLIST keywords from the schedule dictionary and return a DataFrame of the corresponding data by DATES. Also includes functions to read and process the property keywords in the .DATA file, such as DIMENS, PORO, PERMX, etc.

developed by: Martin Araya
email: martinaraya@gmail.com
"""

from genericpath import isfile

import pandas as pd

from .data_reader import read_data
from .welspec import extract_welspecs, extract_welspecl, extract_wellspec, extract_welspec2
from .compdat import extract_compdat, extract_compdatl, extract_compdat2
from .wcon import extract_wconprod, extract_wconinje, extract_wconhist, extract_wconinjh
from .gcon import extract_gconinje, extract_gconprod
from .wlist import extract_wlist
from .property_keywords import read_keyword_from_include, expand_keyword, ijk_index, get_dimens
from .schedule_keywords import extract_keyword
from .dates_tstep import extract_dates, get_first_date
from .counter import start_counter

__all__ = ['compdat2df', 'welspecs2df', 'property2df', 'start_counter', 'dates2df', 'get_start_date', 'keyword2df', 'wconprod2df', 'wconinje2df', 'wconhist2df', 'wconinjh2df', 'wlist2df', 'gconprod2df', 'gconinje2df']
__version__ = '0.7.10'
__release__ = 20260228


def dates2df(path, encoding='cp1252', verbose=False):
    """
    Extract the DATES keyword from the schedule data and return a DataFrame of the corresponding data.
    Parse the TSTEP keyword to extract the time step information and merge it with the DATES data to create a DataFrame with the DATES and corresponding time step information.
    Args:        
        path (str or dict): The path to the .DATA file or a dictionary containing the schedule data.
        encoding (str, optional): The encoding of the .DATA file. Defaults to 'cp1252'.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.
    Returns:        
        pd.DataFrame: A DataFrame containing the DATES data.
    """
    if type(path) is dict:
        return extract_dates(path, keyword='DATES')
    return extract_dates(read_data(path, encoding=encoding, verbose=verbose))

def get_start_date(path, encoding='cp1252', verbose=False):
    """
    Get the start date from the DATES keyword in the schedule data. If the DATES keyword is not found, return None.
    Args:
        path (str or dict): The path to the .DATA file or a dictionary containing the schedule data.
        encoding (str, optional): The encoding of the .DATA file. Defaults to 'cp1252'.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.
    Returns:
        pd.Timestamp or None: The start date from the DATES keyword, or None if the DATES keyword is not found.
    """
    if type(path) is dict:
        return get_first_date(path, verbose=verbose)
    
    import os
    if not os.path.isfile(path):
        raise FileNotFoundError(f"The file {path} does not exist.")
    
    from .helpers import remove_inline_comment
    from .time_parser import parse_dates
    with open(path, 'r', encoding=encoding) as f:
        datafile = f.readlines()
    datafile = [remove_inline_comment(line) for line in datafile]
    if 'START' in ''.join(datafile):
        start_date = datafile[[remove_inline_comment(line) for line in datafile].index('START') + 1].replace('/', '').strip()
        if verbose:
            print(f"Found START date: {start_date}")
        return parse_dates([start_date])[0]
    else:
        if verbose:
            print("No START date found in the schedule data. Attempting to extract from DATES keyword...")
        start_date = get_first_date(read_data(path, encoding=encoding, verbose=verbose), verbose=verbose)
        if verbose and start_date is not None:
            print(f"Start date extracted from DATES keyword: {start_date}")
        elif verbose:
            print("No dates found in the schedule dictionary.")
        return start_date

def compdat2df(path, encoding='cp1252', verbose=False):
    """
    Extract the COMPDAT keyword from the schedule data and return a DataFrame of the corresponding data by DATES.
    Args:        
        path (str or dict): The path to the .DATA file or a dictionary containing the schedule data.
        encoding (str, optional): The encoding of the .DATA file. Defaults to 'cp1252'.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.
    Returns:        
        pd.DataFrame: A DataFrame containing the COMPDAT data by DATES.
    """
    if type(path) is dict:
        return extract_compdat2(path)
    return extract_compdat2(read_data(path, encoding=encoding, verbose=verbose))

def welspecs2df(path, encoding='cp1252', verbose=False):
    """
    Extract the WELSPECS keyword from the schedule data and return a DataFrame of the corresponding data by DATES.
    Args:        
        path (str or dict): The path to the .DATA file or a dictionary containing the schedule data.
        encoding (str, optional): The encoding of the .DATA file. Defaults to 'cp1252'.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.
    Returns:        
        pd.DataFrame: A DataFrame containing the WELSPECS data by DATES.
    """
    if type(path) is dict:
        return extract_welspec2(path)
    return extract_welspec2(read_data(path, encoding=encoding, verbose=verbose))

def wconprod2df(path, encoding='cp1252', verbose=False):
    """
    Extract the WCONPROD keyword from the schedule data and return a DataFrame of the corresponding data by DATES.
    Args:        
        path (str or dict): The path to the .DATA file or a dictionary containing the schedule data.
        encoding (str, optional): The encoding of the .DATA file. Defaults to 'cp1252'.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.
    Returns:        
        pd.DataFrame: A DataFrame containing the WCONPROD data by DATES.
    """
    if type(path) is dict:
        return extract_wconprod(path)
    return extract_wconprod(read_data(path, encoding=encoding, verbose=verbose))

def wconinje2df(path, encoding='cp1252', verbose=False):
    """
    Extract the WCONINJE keyword from the schedule data and return a DataFrame of the corresponding data by DATES.
    Args:        
        path (str or dict): The path to the .DATA file or a dictionary containing the schedule data.
        encoding (str, optional): The encoding of the .DATA file. Defaults to 'cp1252'.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.
    Returns:        
        pd.DataFrame: A DataFrame containing the WCONINJE data by DATES.
    """
    if type(path) is dict:
        return extract_wconinje(path)
    return extract_wconinje(read_data(path, encoding=encoding, verbose=verbose))

def wconhist2df(path, encoding='cp1252', verbose=False):
    """
    Extract the WCONHIST keyword from the schedule data and return a DataFrame of the corresponding data by DATES.
    Args:        
        path (str or dict): The path to the .DATA file or a dictionary containing the schedule data.
        encoding (str, optional): The encoding of the .DATA file. Defaults to 'cp1252'.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.   
    Returns:        
        pd.DataFrame: A DataFrame containing the WCONHIST data by DATES.
    """
    if type(path) is dict:
        return extract_wconhist(path)
    return extract_wconhist(read_data(path, encoding=encoding, verbose=verbose))

def wconinjh2df(path, encoding='cp1252', verbose=False):
    """
    Extract the WCONINJH keyword from the schedule data and return a DataFrame of the corresponding data by DATES.
    Args:
        path (str or dict): The path to the .DATA file or a dictionary containing the schedule data.
        encoding (str, optional): The encoding of the .DATA file. Defaults to 'cp1252'.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.
    Returns:        
            pd.DataFrame: A DataFrame containing the WCONINJH data by DATES.
    """
    if type(path) is dict:
        return extract_wconinjh(path)
    return extract_wconinjh(read_data(path, encoding=encoding, verbose=verbose))

def wlist2df(path, encoding='cp1252', verbose=False):
    """
    Extract the WLIST keyword from the schedule data and return a DataFrame of the corresponding data by DATES.
    Args:
        path (str or dict): The path to the .DATA file or a dictionary containing the schedule data.
        encoding (str, optional): The encoding of the .DATA file. Defaults to 'cp1252'.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.
    Returns:        
        pd.DataFrame: A DataFrame containing the WLIST data by DATES.
    """
    
    if type(path) is dict:
        return extract_wlist(path)
    return extract_wlist(read_data(path, encoding=encoding, verbose=verbose))

def gconprod2df(path, encoding='cp1252', verbose=False):
    """
    Extract the GCONPROD keyword from the schedule data and return a DataFrame of the corresponding data by DATES.
    Args:        
        path (str or dict): The path to the .DATA file or a dictionary containing the schedule data.
        encoding (str, optional): The encoding of the .DATA file. Defaults to 'cp1252'.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.
    Returns:        
        pd.DataFrame: A DataFrame containing the GCONPROD data by DATES.
    """
    if type(path) is dict:
        return extract_gconprod(path)
    return extract_gconprod(read_data(path, encoding=encoding, verbose=verbose))

def gconinje2df(path, encoding='cp1252', verbose=False):
    """
    Extract the GCONINJE keyword from the schedule data and return a DataFrame of the corresponding data by DATES.
    Args:        
        path (str or dict): The path to the .DATA file or a dictionary containing the schedule data.
        encoding (str, optional): The encoding of the .DATA file. Defaults to 'cp1252'.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.
    Returns:        
        pd.DataFrame: A DataFrame containing the GCONINJE data by DATES.
    """
    if type(path) is dict:
        return extract_gconinje(path)
    return extract_gconinje(read_data(path, encoding=encoding, verbose=verbose))

def keyword2df(path, keyword, record_names=[], encoding='cp1252', verbose=False):
    """
    Extract a specified keyword from the schedule data and return a DataFrame of the corresponding data by DATES.
    Args:        
        path (str or dict): The path to the .DATA file or a dictionary containing the schedule data.
        keyword (str): The keyword to extract.
        record_names (list, optional): A list of record names to extract. Defaults to [].
        encoding (str, optional): The encoding of the .DATA file. Defaults to 'cp1252'.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.
    Returns:        
        pd.DataFrame: A DataFrame containing the extracted keyword data by DATES.
    """
    record_names = None if len(record_names) == 0 else record_names
    if type(path) is dict:
        return extract_keyword(path, keyword=keyword, record_names=record_names)
    return extract_keyword(
        read_data(path, encoding=encoding, verbose=verbose),
        keyword=keyword, record_names=record_names)

def property2df(path, keyword, dimens=(None, None, None), encoding='cp1252', verbose=False, parse_to=None):       
    """
    Extract a specified property keyword from the schedule data and return a DataFrame of the corresponding data by DATES.
    Args:
        path (str or dict): The path to the .DATA file or a dictionary containing the schedule data.
        keyword (str): The property keyword to extract.
        dimens (tuple, optional): A tuple containing the dimensions of the property data in the format (I, J, K). Defaults to (None, None, None).
        encoding (str, optional): The encoding of the .DATA file. Defaults to 'cp1252'.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.
        parse_to (type, optional): The type to parse the property data to. Defaults to None, which will parse to int if the keyword ends with 'NUM' and float otherwise.
    Returns:        
        pd.DataFrame: A DataFrame containing the extracted property keyword data by DATES.
    """
    keyword_data = expand_keyword(read_keyword_from_include(path, keyword, encoding=encoding))
    if dimens[0] is not None and dimens[1] is not None and dimens[2] is not None:
        cells = ijk_index(dimens[0], dimens[1], dimens[2])
        output = pd.Series(
            keyword_data.split(),
            index=pd.MultiIndex.from_tuples(cells),
            name=keyword).reset_index()
        output.columns = ['I', 'J', 'K', keyword]
        output[['I', 'J', 'K']] = output[['I', 'J', 'K']].astype(int)
        if parse_to is None:
            parse_to = int if keyword.endswith('NUM') else float
        output[keyword] = output[keyword].astype(parse_to)
        return output
    else:
        return keyword_data