#!/usr/bin/env python3
"""
Date helper functions
"""

#MONTH_LETTERS = [None,'J', 'F', 'M', 'A', 'M', 'J',
#                 'J', 'A', 'S', 'O', 'N', 'D']
MONTH_ABBREVIATIONS = [None,
                       'Jan', 'Feb', 'Mar',
                       'Apr', 'May', 'Jun',
                       'Jul', 'Aug', 'Sep',
                       'Oct', 'Nov', 'Dec']
def first_char_or_none(txt):
    try:
        return txt[0]
    except TypeError:
        return None
MONTH_LETTERS = [first_char_or_none(z) for z in MONTH_ABBREVIATIONS]

def monthstring(y, m, separator='-'): # Is this duplication of code elsewhere?
    return '%04d%s%02d' % (y, separator, m)

def month_as_tuple(y, m):
    return y, m

def pad_month_list(months, formatter=month_as_tuple):
    """
    Given a list of months (strings of format yyyy-mm), yield a sequence of
    months with any gaps filled in
    """

    min_year, min_month = [int(z) for z in min(months).split('-')]
    max_year, max_month = [int(z) for z in max(months).split('-')]

    ret = []
    if min_year == max_year:
        prev = None
        for m in range(min_month, max_month+1):
            yield formatter(min_year, m)
    else:
        for m in range(min_month, 13): # Do min_year
            yield formatter(min_year, m)
        for y in range(min_year+1, max_year): # intermediate years (if any)
            for m in range(1, 13):
                yield formatter(y, m)
        for m in range(1, max_month+1): # max year
            yield formatter(max_year, m)

def pad_month_list_as_tuples(months):
    return pad_month_list(months, formatter=month_as_tuple)

def pad_month_list_as_strings(months):
    return pad_month_list(months, formatter=monthstring)
