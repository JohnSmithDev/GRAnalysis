#!/usr/bin/env python3
"""
Show average page count for shelves and by decade of publication
"""

from __future__ import division

from collections import defaultdict, Counter
from functools import cmp_to_key
import logging
import pdb
# from statistics import stdev # Python 3.4+ (apparently)
import sys


from utils.export_reader import TEST_FILE, read_file

def calculate_average_metric(file, keys_func, metric,
                             inclusive_filters=None,
                             exclusive_filters=None):
    """
    Calculate the average value of a particular metric (currently either
    pagination or rating), grouped by a particular key/dimension, optionally
    including or excluding particular books.
    * keys_func is either the name of a property to group by, or a function
      that takes a Book object as an argument and returns some value derived
      from it.  Note that these can either be scalar values or iterables,
      in the latter case all values in the iterable will be incremented
      accordingly (e.g. a list of shelves a book is on)
    """
    ROGUE_KEY = '*Bad/missing %s*' % (metric)

    book_count = defaultdict(int)
    metric_count = defaultdict(int)
    for book in read_file(TEST_FILE):
        if inclusive_filters:
            unwanted = False
            for filter_func in inclusive_filters:
                if not filter_func(book):
                    unwanted = True
                    break
            if unwanted:
                continue
        if exclusive_filters:
            wanted = True
            for filter_func in exclusive_filters:
                if filter_func(book):
                    wanted = False
                    break
            if not wanted:
                continue

        val = getattr(book, metric)

        try:
            # Try keys_func as a property of a book object
            keys = getattr(book, keys_func)
        except TypeError:
            # Otherwise assume it's a function
            keys = keys_func(book)
        if val is not None: # Ignore books with no/undefined value
            try:
                book_count[keys] += 1
                metric_count[keys] += val
            except TypeError:
                # Assume a list (or iterable) of keys
                for subkey in keys:
                    book_count[subkey] += 1
                    metric_count[subkey] += val
        else:
            book_count[ROGUE_KEY] += 1
            metric_count[ROGUE_KEY] += 0
    avgs = []
    for k, numerator in metric_count.items():
        avgs.append((k,  numerator / book_count[k], book_count[k]))

    return avgs

### A couple of convenience wrappers follow - these are probably the
### only useful variants you'd actually want to use, unless you need extra
### filtering

def calculate_average_pagination(filename, grouping):
    return calculate_average_metric(filename, grouping, 'pagination')

def calculate_average_rating(filename, grouping):
    def is_read(book):
        return book.status == 'read'
    return calculate_average_metric(filename, grouping, 'rating',
                                    inclusive_filters=[is_read])



if __name__ == '__main__':

    print('== Average page count by shelf ==')
    for k, v, c in sorted(calculate_average_pagination(TEST_FILE, 'shelves'),
                          key=lambda z: -z[1]):
        print('%-30s: %5d (%d)' % (k, v, c))

    print()

    print('== Average page count by decade ==')
    for k, v, c in sorted(calculate_average_pagination(TEST_FILE, 'decade'),
                          key=lambda z: z[0]):
        print('%-30s: %5d (%d)' % (k, v, c))


