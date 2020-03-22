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

def remove_excess_whitespace(txt, include_all_whitespace_chars=False):
    """
    Set include_all_whitespace_chars to True to include newlines, tabs etc.
    (That should be irrelevant in the context of the GR CSV export, but is
    useful for some other projects that import this library.
    """
    stuff_to_replace = '\s+' if include_all_whitespace_chars else ' +'
    return re.sub(stuff_to_replace, ' ', txt.strip())

def eradicate_excess_whitespace(txt):
    """A more extreme version of eradicate_excess_whitespace"""
    return remove_excess_whitespace(txt, include_all_whitespace_chars=True)


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

def clean_title(title):
    """Remove any parenthesized series from a book title"""
    # TODO: This will return the wrong thing on a hypothetical title like
    # 'Was (Not) Was (Volume 1' - use something like the regexes in
    # .series_and_volume() to do the right thing
    if title.endswith(')'):
        no_parens =  title.split('(')[0].strip()
    else:
        no_parens = title
    if no_parens.endswith(':'): # Seen on a title from a different website
        no_parens = no_parens[:-1]
    return no_parens

def goodreads_book_url(book_id):
    return 'https://www.goodreads.com/book/show/%d' % (book_id)
