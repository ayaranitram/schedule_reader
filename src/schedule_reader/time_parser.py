"""
A function to parse the DATES keyword in the .SCHEDULE file and return a pandas Series of datetime objects.

developed by: Martin Araya
email: martinaraya@gmail.com
"""

import pandas as pd
from .helpers import remove_inline_comment

__version__ = '0.7.1'
__release__ = 20260228

def parse_dates(dates_keyword):
    """
    receives a string of date(s) or list of string(s) and attempt to parse it according to DATES eclipse format: DD 'MMM' YYYY HH:MM:SS 

    Parameters:
        dates_keyword: str or list of str

    Return:
        pandas.Series of dtype datetime64[ns]
    """
    if type(dates_keyword) is str:
        if '\n' in dates_keyword:
            dates_keyword = dates_keyword.split('\n')
        else:
            dates_keyword = [dates_keyword]

    # removes 'DATES' keyword or ending slash '/'
    # remove '/' or '-' in the date string
    dates_keyword = [each if not isinstance(each, str) else 
                     remove_inline_comment(each).strip('/ ').replace('-', ' ').replace('/', ' ')
                     for each in dates_keyword
                     if not str(each).strip().upper().startswith('DATES') and not str(each).strip().startswith('/')]

    # parse dates lines
    return pd.to_datetime(dates_keyword, format='mixed', dayfirst=True).values


def tstep_to_dates(tstep, start_date):
    """
    converts a list of time steps to a list of datetime objects, given a start date.

    Parameters:
        tstep: list of int or float
        start_date: str or datetime
    Return:
        pandas.Series of dtype datetime64[ns]
    """
    start_date = pd.to_datetime(start_date, format='mixed', dayfirst=True)
    return pd.Series([start_date + pd.Timedelta(days=each) for each in tstep], dtype='datetime64[ns]')
