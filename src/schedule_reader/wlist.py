import pandas as pd
from .dates import parse_dates
from .schedule_keywords import extract_keyword


def extract_wlist(schedule_dict:dict) -> pd.DataFrame:
    """
    Shortcut for `extract_keyword` for the WLIST keyword.
    Extract the WLIST keyword from the schedule dictionary and return a DataFrame of WLIST data by DATES.

    Params:
        schedule_dict: dict
            shedule dictionary prepared by the .data_reader.read_data function

    Return:
        pandas.DataFrame
    """
    wlist_columns = ['date', 'list', 'operation'] + [f"well{str(w).zfill(2)}" for w in range(1000)]
    wlist_table = extract_keyword(schedule_dict, 'WLIST', wlist_columns)  # {}
    if len(wlist_table) > 0:
        wlist_table['date'] = parse_dates(
            wlist_table['date'].to_list())  # to parse dates exactly as stated by DATES eclipse format
        wlist_table['list'] = [wlist.strip("'") for wlist in wlist_table['list']]
        wlist_table['list'] = wlist_table['list'].astype('category')
        wlist_table.replace('1*', None, inplace=True)
        wlist_table.replace("'1*'", None, inplace=True)
        wlist_table = wlist_table.dropna(axis=1, how='all')
    return wlist_table