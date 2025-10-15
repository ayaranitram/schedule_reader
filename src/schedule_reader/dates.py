import pandas as pd
from .helpers import remove_inline_comment


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
    dates_keyword = [remove_inline_comment(each).strip('/ ').replace('-', ' ').replace('/', ' ')
                     for each in dates_keyword
                     if not each.strip().upper().startswith('DATES') and not each.strip().startswith('/')]

    # parse dates lines
    return pd.to_datetime(dates_keyword, format='mixed', dayfirst=True).values