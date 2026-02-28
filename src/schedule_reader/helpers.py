"""
A helper function to remove inline comments from a keyword line, and a helper function to extract the I and J coordinates for a well from its WELSPECS definition when they are defaulted in the COMPDAT keyword. Also, a shortcut function to extract the COMPDAT keyword from the schedule dictionary and return a DataFrame of COMPDAT data by DATES.

developed by: Martin Araya
email: martinaraya@gmail.com
"""

__version__ = '0.7.0'
__release__ = 20260228

def remove_inline_comment(line:str) -> str:
    """
    Receives a keyword string line and remove the comments.
    Args:
        line: str
    Returns:
        str
    """
    if line.strip().startswith('--'):
        return line

    _cut = {len(line): None}
    for each in ['--', '/', '"', "'"]:
        if each in line:
            _cut[line.index(each)] = each
    
    done = False
    for quotation in ['"', "'"]:
        if _cut[min(_cut)] == quotation:
            _open = min(_cut)
            _close = _open + line[_open+1:].index(quotation) + 1
            if '/' in line[_close:]:
                _cut = _close + line[_close:].index('/') + 1
                done = True
            break
    
    if not done:
        if _cut[min(_cut)] == '/':
            _cut = min(_cut) + 1
        elif _cut[min(_cut)] == '--':
            _cut = min(_cut)
        else:
            _cut = len(line)
    return line[:_cut].strip()