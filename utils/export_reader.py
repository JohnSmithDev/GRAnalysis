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

from utils.book import Book, date_from_string, NotOwnedAtSpecifiedDateError


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

def create_comparison_filter(property, comparison, string_value):
    # Note that we don't support value/comparison/property order for filter
    # command line arguments

    def fltr(bk):
        actual_val = getattr(bk, property)
        # Strictly speaking the "plural" vals version is unnecessary here,
        # because the only property that can have multiple values is shelves,
        # and that is supported by create_shelf_filter() and omitting any
        # property name and comparison operator.  However, it may be more user
        # friendly to support '-f user_shelves = non-fiction'?
        actual_vals = bk.property_as_sequence(property)

        if actual_vals and actual_vals[0]:
            type_to_cast_to = type(actual_vals[0])
            # TODO: something similar for boolean properties, although
            # we also need to change the comparisons below from = to is...
            if type_to_cast_to == date:
                value = date_from_string(string_value)
            else:
                value = type_to_cast_to(string_value)
        else:
            # Typically this will be on books where the relevant  property is None
            # e.g. missing pagination in the data export, rating or read_date on
            #      an unread book
            # TODO (probably): downgrade to warning
            logging.error("Unable to compare %s %s %s %s for %s - ignoring" %
                            (property, string_value, comparison,
                             actual_val, bk.title))
            return False

        if comparison in ('=', '=='):
            return value in actual_vals
        elif comparison in ('!=', '<>'):
            return not value in actual_vals
        elif comparison in ('~', '~=', '=~'):
            for av in actual_vals:
                if re.search(value, av, re.IGNORECASE):
                    return True
            return False
        elif comparison in ('~!', '!~'):
            for av in actual_vals:
                if re.search(value, av, re.IGNORECASE):
                    return False
            return True
        elif comparison == '>':
            return actual_val > value
        elif comparison in ('>=', '=>'):
            return actual_val >= value
        elif comparison == '<':
            return actual_val < value
        elif comparison in ('<=', '=<'):
            return actual_val <= value

        raise ValueError('Unknown comparison operator "%s' % (comparison))

    return fltr

def create_filter(filter_string):
    comparison_regex = re.search('\s*(\w+)\s*([!=<>~]+)\s*(\S+)\s*', filter_string)
    if comparison_regex:
        return create_comparison_filter(comparison_regex.group(1),
                                        comparison_regex.group(2),
                                        comparison_regex.group(3))
    else:
        return create_shelf_filter(filter_string)

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
                    filter_funcs.append(create_filter(filter_string))
        except AttributeError as err:
            # logging.error(err)
            pass # The calling script doesn't support (user-defined) filters


    try:
        effective_date = args.date
    except AttributeError:
        effective_date = None
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for line_num, row in enumerate(reader):
            try:
                bk = Book(row, as_of_date=effective_date)
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
            except NotOwnedAtSpecifiedDateError:
                pass
            except Exception as err:
                logging.error('Blew up on line %d: %s/%s' % (line_num, err, type(err)))
                raise(err)
                # pdb.set_trace()


