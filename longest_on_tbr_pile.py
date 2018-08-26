#!/usr/bin/env python3
"""
Output list of sorted books that have been read ordered by how long they were
TBR, as measured by date added vs date read.

Obviously this is highly dependent on how accurately you record your reading
activity, and - maybe more importantly - doesn't include any books you haven't
yet read (or are currently reading), which may well be many more than are listed
here.
"""

from functools import cmp_to_key

from utils.arguments import create_parser, validate_args
from utils.export_reader import read_file, only_read_books, \
    only_unread_books

MIN_PERIOD = 31

def output_report(books, min_period=None, max_books=None, output_function=print):
    for i, bk in enumerate(books):
        if (min_period and bk.days_on_tbr_pile < min_period) or \
           (max_books and i >= max_books):
            break
        output_function('%4d. %-60s - Days on TBR pile: %4d' %
                        (i+1, bk.title[:58], bk.days_on_tbr_pile))


def report(books, label, min_period, max_books, output_function=print):
    def comparator(book_a, book_b):
        return book_b.days_on_tbr_pile - book_a.days_on_tbr_pile

    output_function('== %s ==' % (label))
    sorted_books = sorted(books, key=cmp_to_key(comparator))
    output_report(sorted_books, min_period, max_books, output_function)


if __name__ == '__main__':
    parser = create_parser('Show which books have languished the longest on the TBR pile',
                      supported_args='fl')
    parser.add_argument('-p', dest='min_period', type=int, nargs='?',
                        default=31, help='Minimum period to report in (in days)')
    args = parser.parse_args()
    validate_args(args)

    if args.filters:
        shelves_label = ' / '.join(args.filters) + ' '
    else:
        shelves_label = ''

    def only_valid_dates(bk):
        # This is mainly for the benefit of books that were read long ago and
        # retroactively added to GoodReads
        return bk.date_added and bk.date_read and (bk.date_read > bk.date_added)

    report(read_file(args=args, filter_funcs=[only_read_books, only_valid_dates]),
           'Read %sbooks' % (shelves_label), args.min_period, args.limit)

    print()

    report(read_file(args=args, filter_funcs=[only_unread_books]),
                     'Unread %sbooks' % (shelves_label),
           args.min_period, args.limit)
