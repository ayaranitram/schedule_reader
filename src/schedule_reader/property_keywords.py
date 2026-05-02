"""
A set of functions to read and process the property keywords in the .DATA file, such as DIMENS, PORO, PERMX, etc. These functions can be used to extract the data from the keywords and return it in a format that can be easily used for further analysis.

developed by: Martin Araya
email: martinaraya@gmail.com
"""

import pandas as pd

__all__ = ['read_keyword_from_include', 'expand_keyword', 'ijk_index', 'get_dimens']
__version__ = '0.7.16'
__release__ = 20260503

def read_keyword_from_include(path, keyword=None, encoding='cp1252'):
    """
    reads the ASCII include file from the `path`, looks for the `keyword` and extracts its data.

    Returns:

    """
    with open(path, 'r', encoding='cp1252') as f:
        keyword_data = ''.join(f.readlines())

    if keyword not in keyword_data:
        raise ValueError(f"The requested keyword {keyword} is not in this file {path}")

    i = keyword_data.index(keyword)
    f = keyword_data.index('/', i)
    keyword_data = keyword_data[i + len(keyword): f].strip()

    while '--' in keyword_data:
        i = keyword_data.index('--')
        f = keyword_data.index('\n', i)
        keyword_data = keyword_data[:i] + keyword_data[f + 1:]

    return keyword_data


def expand_keyword(string):
    """
    received the string readout from the property keyword and return the string property expanded.
    """
    result = []
    for each in string.split():
        if '*' in each:
            parts = each.split('*', 1)
            if parts[0].isdigit():
                result.extend([parts[1]] * int(parts[0]))
            else:
                result.append(each)  # wildcard name like 'P*', not a repetition
        else:
            result.append(each)
    return ' '.join(result)


def ijk_index(i, j=None, k=None):
    if j is None and k is None and hasattr(i, '__iter__') and len(i) == 3 \
            and i[0] is not None and i[1] is not None and i[2] is not None:
        i, j, k = i[0], i[1], i[2]
    elif j is None or k is None:
        raise ValueError(f"must provide i, j, k or a tuple of (i, j, k), but received i={i}, j={j}, k={k}")

    cells = [(i_, j_, k_)
             for k_ in range(1, k + 1)
             for j_ in range(1, j + 1)
             for i_ in range(1, i + 1)
             ]
    return pd.MultiIndex.from_tuples(cells)


def get_dimens(path, encoding='cp1252'):
    """
    reads the ASCII .DATA file and returns a three items tuple with the DIMENS keyword data.
    """
    with open(path, 'r', encoding='cp1252') as f:
        keyword_data = ''.join(f.readlines())

    keyword = 'DIMENS'
    if keyword not in keyword_data:
        return (None, None, None)

    i = keyword_data.index(keyword)
    f = keyword_data.index('/', i)
    keyword_data = keyword_data[i + len(keyword): f].strip()

    return tuple(int(x) for x in keyword_data.split())
