#!/usr/bin/env python3
"""
Show which authors have the best average ranking.  Ignores authors for whom
only a single book has been read.
"""

from collections import defaultdict
from functools import cmp_to_key

from utils.arguments import parse_args
from utils.export_reader import read_file, only_read_books
from utils.transformers import best_ranked_report


if __name__ == '__main__':
    args = parse_args('Show average rating of authors, with a bar chart breaking down the rankings',
                      supported_args='af')
    books = read_file(args=args, filter_funcs=[only_read_books])
    best_ranked_report(books, 'all_authors' if args.all_authors else 'author',
                       ignore_single_book_groups=True)

