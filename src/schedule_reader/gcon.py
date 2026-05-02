"""
A set of functions to extract the GCONPROD, and GCONINJE keywords from the schedule dictionary and return a DataFrame of group keyword data by DATES.
These functions are shortcuts for the `extract_keyword` function for each of the corresponding keywords, and they also perform some additional processing to clean and format the data.

developed by: Martin Araya
email: martinaraya@gmail.com
"""

import pandas as pd
from .time_parser import parse_dates
from .schedule_keywords import extract_keyword

__version__ = '0.7.16'
__release__ = 20260503

def extract_gconprod(schedule_dict:dict) -> pd.DataFrame:
    """
    Shortcut for `extract_keyword` for the GCONPROD keyword.
    Extract the GCONPROD keyword from the schedule dictionary and return a DataFrame of GCONPROD data by DATES.

    Params:
        schedule_dict: dict
            shedule dictionary prepared by the .data_reader.read_data function

    Return:
        pandas.DataFrame
    """
    gconprod_columns = ['date', 'group', 'control mode', 'OIL rate', 'WATER rate', 'GAS rate', 'LIQUID rate',
                        'procedure on exceeding maximum rate limit', 'respond to higher level', 'guide rate', 
                        'definition of guide rate', 'procedure on exceeding water rate limit', 
                        'procedure on exceeding gas rate limit', 'procedure on exceeding liquid rate limit',
                        'RESV rate', 'RESV balance fraction target', 'WET rate', 'calorific rate target',
                        'surf. gas balance fraction target', 'surf. water balance fraction target', 
                        'linear comb. rate limit', 'procedure on exceeding linear comb. rate limit']
    gconprod_table = extract_keyword(schedule_dict, 'GCONPROD', gconprod_columns)  # {}
    if gconprod_table is not None and len(gconprod_table) > 0:
        gconprod_table['date'] = parse_dates(
            gconprod_table['date'].to_list())  # to parse dates exactly as stated by DATES eclipse format
        gconprod_table['group'] = [group.strip("'") for group in gconprod_table['group']]
        gconprod_table['group'] = gconprod_table['group'].astype('category')
        gconprod_table = gconprod_table.replace('1*', None).replace("'1*'", None)
        gconprod_table['control mode'] = gconprod_table['control mode'].fillna('NONE')
        gconprod_table['procedure on exceeding maximum rate limit'] = gconprod_table['procedure on exceeding maximum rate limit'].fillna('NONE')
        gconprod_table['respond to higher level'] = gconprod_table['respond to higher level'].fillna('YES')
        gconprod_table['guide rate'] = gconprod_table['guide rate'].fillna('FIELD')
        gconprod_table['definition of guide rate'] = gconprod_table['definition of guide rate'].fillna(' ')
        gconprod_table['procedure on exceeding water rate limit'] = gconprod_table['procedure on exceeding water rate limit'].fillna('NONE')
        gconprod_table['procedure on exceeding gas rate limit'] = gconprod_table['procedure on exceeding gas rate limit'].fillna('NONE')
        gconprod_table['procedure on exceeding liquid rate limit'] = gconprod_table['procedure on exceeding liquid rate limit'].fillna('NONE')
        gconprod_table['procedure on exceeding linear comb. rate limit'] = gconprod_table['procedure on exceeding linear comb. rate limit'].fillna('NONE')

    return gconprod_table


def extract_gconinje(schedule_dict:dict) -> pd.DataFrame:
    """
    Shortcut for `extract_keyword` for the GCONINJE keyword.
    Extract the GCONINJE keyword from the schedule dictionary and return a DataFrame of GCONINJE data by DATES.

    Params:
        schedule_dict: dict
            shedule dictionary prepared by the .data_reader.read_data function

    Return:
        pandas.DataFrame
    """
    gconinje_columns = ['date', 'group', 'phase', 'control mode', 'SURFACE fluid rate',
                        'RESERVOIR fluid rate', 'reinjection fraction', 'voidage replacement fraction', 
                        'response to higher level', 'guide rate', 'definition of guide rate',
                        'reinjection group', 'voidage replacement group', 'wet gas injection rate']
    gconinje_table = extract_keyword(schedule_dict, 'GCONINJE', gconinje_columns)  # {}
    if gconinje_table is not None and len(gconinje_table) > 0:
        gconinje_table['date'] = parse_dates(
            gconinje_table['date'].to_list())  # to parse dates exactly as stated by DATES eclipse format
        gconinje_table['group'] = [group.strip("'") for group in gconinje_table['group']]
        gconinje_table['group'] = gconinje_table['group'].astype('category')
        gconinje_table = gconinje_table.replace('1*', None).replace("'1*'", None)
        gconinje_table['control mode'] = gconinje_table['control mode'].fillna('NONE')
        gconinje_table['response to higher level'] = gconinje_table['response to higher level'].fillna('YES')
        gconinje_table['definition of guide rate'] = gconinje_table['definition of guide rate'].fillna(' ')

    return gconinje_table
