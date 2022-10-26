#!/usr/bin/env python3
"""
Show which authors you have read the most, whether by number of books or pages.

Replicates the functionality removed from the GR site in January 2019, but adds
extra stuff such as showing the average rating, rating breakdown, filtering,
all contributing authors, etc.
"""

from utils.arguments import create_parser, validate_args
from utils.export_reader import read_file, only_read_books
from utils.transformers import best_ranked_report


if __name__ == '__main__':
    parser = create_parser('Show the most read authors, along with rating average and breakdown',
                           supported_args='aef', report_on='author')

    parser.add_argument('-p', dest='by_page_count', action='store_true',
                        help='Rank by total pages read (default is by number of books read)')
    args = parser.parse_args()
    validate_args(args)

    books = read_file(args=args, filter_funcs=[only_read_books])

    if args.by_page_count:
        sort_metric = '~number_of_pages'
        ignore_singles = False
    else:
        sort_metric = '~number_of_books_rated'
        ignore_singles = True

    best_ranked_report(books, 'all_authors' if args.all_authors else 'author',
                       sort_metric=sort_metric,
                       ignore_single_book_groups=ignore_singles,
                       enumerate_output=args.enumerate_output)
