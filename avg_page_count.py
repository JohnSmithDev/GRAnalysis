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
from utils.transformers import calculate_average_metric



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


