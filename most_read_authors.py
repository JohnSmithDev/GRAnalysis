#!/usr/bin/env python3
"""
Show which authors you have read the most.  Replicates the functionality
removed from the GR site in January 2019, but adds extra stuff such as showing
the average rating, rating breakdown, filtering, all authors, etc.
"""

from collections import defaultdict
from functools import cmp_to_key

from utils.arguments import parse_args
from utils.export_reader import read_file, only_read_books
from utils.transformers import best_ranked_report


if __name__ == '__main__':
    args = parse_args('Show the most read authors, along with rating average and breakdown',
                      supported_args='aef', report_on='author')

    books = read_file(args=args, filter_funcs=[only_read_books])
    best_ranked_report(books, 'all_authors' if args.all_authors else 'author',
                       sort_metric='~number_of_books_rated',
                       ignore_single_book_groups=True,
                       enumerate_output=args.enumerate_output)


