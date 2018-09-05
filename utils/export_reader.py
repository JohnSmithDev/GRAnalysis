#!/usr/bin/env python3
"""
Library to read the CSV export that GoodReads makes available
"""

import csv
from datetime import date
import logging
import os
import pdb
import re
import sys

from utils.book import Book


TODAY = date.today() # Assumption: anything using this lib will never run over multiple days

# Q: Does this affect logging behaviour in other modules?  (I tried setting
# up a custom logger, but it was ****ing me around, and I couldn't be ****d
# to fix it properly)
logging.getLogger().setLevel(logging.ERROR)



### Some commonly used filters for use with read_file()
def only_read_books(bk):
    return bk.is_read
def only_unread_books(bk):
    return bk.is_unread
def only_read_and_rated_books(bk):
    return bk.is_read and bk.rating is not None and bk.rating > 0

def create_shelf_filter(filter_string):
    """
    Factory function to return functions that reject books that are (or aren't
    as appropriate, based on ! or ~ prefix) on a particular shelf.
    """

    def fltr(bk):
        if filter_string[0] in ('!', '~'):
            if filter_string[1:] in bk.shelves:
                return False
        else:
            if filter_string not in bk.shelves:
                return False
        return True

    return fltr

def read_file(filename=None, filter_funcs=None, args=None):
    """
    Read a GR export CSV file, and yield a series of Book objects, optionally
    filtering out certain books.
    """

    if args:
        if args.csv_file:
            filename = args.csv_file
        try:
            if args.filters:
                if filter_funcs:
                    filter_funcs = filter_funcs[:] # copy, so we don't mangle the original
                else:
                    filter_funcs = []
                for filter_string in args.filters:
                    filter_funcs.append(create_shelf_filter(filter_string))
        except AttributeError:
            pass # The calling script doesn't support (user-defined) filters

    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for line_num, row in enumerate(reader):
            try:
                bk = Book(row)
                wanted = True
                if filter_funcs:
                    for fn in filter_funcs:
                        if not fn(bk):
                            wanted = False
                            break
                if wanted:
                    yield bk
                else:
                    logging.debug("Skipping %s" % (bk))
            except Exception as err:
                logging.error('Blew up on line %d: %s/%s' % (line_num, err, type(err)))
                pdb.set_trace()


