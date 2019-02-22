#!/usr/bin/env python3
"""
Show average page count for a particular dimension
"""

# from __future__ import division

from os.path import basename
import sys

from collections import namedtuple
# from functools import cmp_to_key
# from statistics import stdev # Python 3.4+ (apparently)

from utils.export_reader import read_file, only_read_and_rated_books
from utils.arguments import parse_args
from utils.transformers import calculate_average_metric


def sort_value_by_reverse_pagination(z):
    return -z[1]
def sort_value_by_key(z):
    return z[0]
def sort_value_by_integer_key(z):
    val = z[0]
    if isinstance(val, int):
        return val
    else:
        # Presumably the rogue value i.e. '*Bad/missing pagination*'
        return -9999


PatternConfig = namedtuple('PatternConfig',
                           'key_attribute, filter_functions, sort_function, '
                           'include_missing_pagination')

PATTERN_CONFIGS = {
    'shelf': PatternConfig('shelves', [], sort_value_by_reverse_pagination, True),
    'decade': PatternConfig('decade', [], sort_value_by_key, True),
    'year': PatternConfig('year', [], sort_value_by_integer_key, True),
    'rating': PatternConfig('rating_as_stars', [only_read_and_rated_books],
                            sort_value_by_key, False),
    'author': PatternConfig('author', [], sort_value_by_reverse_pagination, True)
}


if __name__ == '__main__':
    script_name = basename(sys.argv[0])
    for p, cfg in PATTERN_CONFIGS.items():
        if p in script_name:
            key_attribute_name = p
            config = cfg
            break
    else:
        raise Exception('No attribute found in script name')

    # TODO: support enumeration/ranking (-e)
    args = parse_args('Show average page count by %s,'
                      ' by decade of publication, and rating' % key_attribute_name,
                      supported_args='fl')

    books = read_file(filter_funcs=config.filter_functions, args=args)
    raw_data = calculate_average_metric(books, config.key_attribute, 'pagination',
                                       include_missing_pagination=config.include_missing_pagination)
    data = sorted(raw_data, key=config.sort_function)

    if args.limit:
        data = data[:args.limit]
    for k, v, c in data:
        print('%-30s: %5d (%d)' % (k, v, c))

