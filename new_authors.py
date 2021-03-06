#!/usr/bin/env python3
"""
Report on the number/proportion of new authors you've read each year
"""

from collections import namedtuple, defaultdict
from datetime import date

from utils.arguments import create_parser, validate_args
from utils.export_reader import read_file, only_read_books

START_OF_HISTORY = date(1970,1,1) # Rogue value to allow sorting to work

VERBOSE = False

YearStats = namedtuple('YearStats', 'year, new_authors, all_authors, all_books')

def output_stat(stat, output_function=print):
    if stat.all_books != 0:
        print('%s: Read %d new authors, out of %d authors (%d%%) and %d books (%d%%)' %
              (stat.year or '{unknown-year}',
               stat.new_authors,
               stat.all_authors, (100 * stat.new_authors / stat.all_authors),
               stat.all_books, (100 * stat.new_authors / stat.all_books)))


def report_stats(books, output_function=print):

    # Maps author name to first year read; we don't currently do anything with the latter
    read_authors = {}

    year_to_books = defaultdict(list)
    for book in books:
        year_to_books[str(book.year_read or '')].append(book)

    prev_author_count = 0
    for year, year_books in sorted(year_to_books.items()):
        year_authors = set()
        for book in year_books:
            year_authors.add(book.author)
            if book.author not in read_authors:
                if VERBOSE:
                    output_function(book)
                read_authors[book.author] = book.year

        stat = YearStats(year, len(read_authors) - prev_author_count,
                         len(year_authors), len(year_books))
        output_stat(stat, output_function)
        prev_author_count = len(read_authors)


if __name__ == '__main__':
    parser = create_parser('List all books matching filters, optionally ordered ' +
                           'and/or grouped.~',
                           supported_args='f', report_on='book')
    args = parser.parse_args()
    validate_args(args)

    # TODO: would be good for read_file() to do the sorting (if it's set in args)
    books = read_file(args=args, filter_funcs=[only_read_books])

    def custom_sort_key(z):
        return getattr(z, 'date_read') or START_OF_HISTORY

    sorted_books = sorted(books, key=custom_sort_key)

    report_stats(sorted_books)

