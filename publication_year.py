#!/usr/bin/env python3
"""
Output list of books ordered by publication year.

NB: I believe this data in the export is not reliable (in part, this script
has been written to ascertain this).  UPDATE: looks like either "Year
Published" or "Original Publication Year" can be empty, but not both - at
least based on the books I own.
"""

from utils.arguments import create_parser, validate_args
from utils.export_reader import read_file


if __name__ == '__main__':
    parser = create_parser('Output list of books ordered by publication year.',
                           supported_args='f')
    parser.add_argument('-s', dest='space_between_years', action='store_true',
                        help='Output blank line between years')
    args = parser.parse_args()
    validate_args(args)

    books_in_pub_date_order = sorted(read_file(args=args),
                                     key=lambda z: z.year or 9999)
    prev_year = None
    for b in books_in_pub_date_order:
        if args.space_between_years and prev_year is not None and b.year != prev_year:
            print()
        print('%s %-5s : %s' % (b.year or '????',
                              b.rating * '*' if b.rating else '',
                              b))
        prev_year = b.year

