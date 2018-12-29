#!/usr/bin/env python3
"""
Show average ranking of shelves, with a bar chart breaking down the rankings
"""

from __future__ import division

from collections import defaultdict
from functools import cmp_to_key

from utils.arguments import parse_args
from utils.export_reader import read_file, only_read_books
from utils.transformers import best_ranked_report


if __name__ == '__main__':
    args = parse_args('Show average rating of shelves, with a bar chart breaking down the rankings',
                      supported_args='f')
    books = read_file(args=args, filter_funcs=[only_read_books])
    best_ranked_report(books, 'shelves')
