#!/usr/bin/env python3
"""
Show average page count for shelves and by decade of publication
"""

from __future__ import division

from collections import defaultdict
# from functools import cmp_to_key
# from statistics import stdev # Python 3.4+ (apparently)

from utils.export_reader import read_file, only_read_and_rated_books
from utils.arguments import parse_args

def calculate_average_metric(books, keys_func, metric,
                             include_missing_pagination=True):
    """
    Calculate the average value of a particular metric (currently either
    pagination or rating), grouped by a particular key/dimension.
    * keys_func is either the name of a property to group by, or a function
      that takes a Book object as an argument and returns some value derived
      from it.  Note that these can either be scalar values or iterables,
      in the latter case all values in the iterable will be incremented
      accordingly (e.g. a list of shelves a book is on)
    """
    ROGUE_KEY = '*Bad/missing %s*' % (metric)

    book_count = defaultdict(int)
    metric_count = defaultdict(int)

    for book in books:
        val = getattr(book, metric)

        # TODO: I think this keys related code can be simplied using the
        # Book.property_as_*() methods?
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
        elif include_missing_pagination:
            book_count[ROGUE_KEY] += 1
            metric_count[ROGUE_KEY] += 0
    avgs = []
    for k, numerator in metric_count.items():
        avgs.append((k,  numerator / book_count[k], book_count[k]))

    return avgs


if __name__ == '__main__':
    args = parse_args('Show average page count for shelves, by decade of publication, and rating',
                      supported_args='f')

    print('== Average page count by shelf ==')
    for k, v, c in sorted(calculate_average_metric(read_file(args=args),
                                                       'shelves', 'pagination'),
                          key=lambda z: -z[1]):
        print('%-30s: %5d (%d)' % (k, v, c))

    print()

    print('== Average page count by decade ==')
    for k, v, c in sorted(calculate_average_metric(read_file(args=args),
                                                       'decade', 'pagination'),
                          key=lambda z: z[0]):
        print('%-30s: %5d (%d)' % (k, v, c))

    print()

    print('== Average page count by rating ==')
    for k, v, c in sorted(calculate_average_metric(
            read_file(filter_funcs=[only_read_and_rated_books], args=args),
            'padded_rating_as_stars', 'pagination', include_missing_pagination=False),
                          key=lambda z: z[0]):
        print('%-30s: %5d (%d)' % (k, v, c))


