#!/usr/bin/env python3
"""
Support functions for book data from Goodreads.  Typically this is validation,
sanitisation or presention of (mostly text) fields.

This functionality was originally within the book module, but has been factored
out as it may be of use more generally, particularly if you are doing some
analysis at a more macro level, where you don't have enough data to populate a
Book object.
"""

from datetime import date
import re

def date_from_string(ds):
    """Turn a string of format yyyy/mm/dd into a Python date object"""
    # This is now used for the command-line filters, so we also support -
    # as a separator
    separator = '/'
    if '-' in ds:
        separator = '-'
    if ds:
        dbits = [int(z) for z in ds.split(separator)]
        return date(dbits[0], dbits[1], dbits[2])
    else:
        return None

def formatted_month(dt, separator='-'):
        return '%04d%s%02d' % (dt.year, separator,
                               dt.month)

def remove_excess_whitespace(txt):
    return re.sub(' +', ' ', txt.strip())



def strip_prefixes(txt, prefixes):
    if not txt:
        return None
    txt = txt.strip()
    for prefix in prefixes:
        if txt.startswith(prefix):
            strip_len = len(prefix)
            txt = txt[strip_len:]
    return txt

def strip_suffixes(txt, suffixes):
    if not txt:
        return None
    txt = txt.strip()
    for suffix in suffixes:
        if txt.endswith(suffix):
            strip_len = -len(suffix)
            txt = txt[:strip_len]
    return txt

def sanitise_publisher(pub):
    """
    Remove extraneous text from publisher name, primarily to aid reports that
    group books from a publisher together.

    This is a bit of a losing battle, but hopefully we'll catch many of the
    easy ones.
    """
    return strip_suffixes(pub, (' PLC', ' and Company', ' Limited', ' Ltd', ' LLC',
                                ' Books', ' UK', ' Press', ' Digital',
                                ' Publishing', ' Publishers',
                                ' Publishing Co', ' Publishing Group'))
