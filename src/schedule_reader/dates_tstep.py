"""
This module contains helper functions to extract and parse the DATES keyword from the schedule dictionary.

developed by: Martin Araya
email: martinaraya@gmail.com
"""

from ast import main

import pandas as pd
from .time_parser import parse_dates
from .schedule_keywords import extract_keyword

__version__ = '0.2.0'
__release__ = 20260228


def extract_dates(schedule_dict:dict) -> pd.Series:
    """
    Shortcut for `parse_dates` function. Extract the DATES keyword from the schedule dictionary and return a Series of datetime objects.

    Params:
        schedule_dict: dict
            shedule dictionary prepared by the .data_reader.read_data function
    Return:
        pandas.Series of dtype datetime64[ns]
    """
    dates_keyword = extract_keyword(schedule_dict, 'DATES', ['DATES'])
    if len(dates_keyword) > 0:
        dates_keyword = parse_dates(dates_keyword)
    return dates_keyword

def get_first_date(schedule_dict:dict, verbose=False) -> pd.Timestamp:
    """
    Get the start date from the DATES keyword in the schedule dictionary. If the DATES keyword is not found, return None.

    Params:
        schedule_dict: dict
            shedule dictionary prepared by the .data_reader.read_data function  
    Return:
        pandas.Timestamp or None
    """
    if verbose:
        print("Extracting DATES keyword to find the start date...")
    dates = extract_dates(schedule_dict)
    if len(dates) > 0:
        start_date = dates.min()
        if verbose:
            print(f"Start date found: {start_date}")
        return start_date
    else:
        if verbose:
            print("No dates found in the schedule dictionary.")
        return None