#!/usr/bin/env python3
"""
Show year-by-year (read or added) stats over shelves (or other dimension derived
from symlinked filename)
"""

from os.path import basename
import sys

from utils.arguments import create_parser, validate_args
from utils.export_reader import read_file
from utils.year_on_year import YearOnYearReport


# This report is only interesting on dimensions with a reasonable number of
# items, so I don't *think* author, publisher, publication year etc need to
# be supported.
pattern_to_key = {
    'shelf': 'shelves',
    'decade': 'decade',
    'rating': 'rating_as_stars'
}

if __name__ == '__main__':
    script_name = basename(sys.argv[0])
    for p, k in pattern_to_key.items():
        if p in script_name:
            key_attribute_name = p
            key_attribute = k
            break
    else:
        raise Exception('No attribute found in script name')

    # key_attribute = 'shelves' # Should be user_shelves if year_key == year_read

    parser = create_parser('Show year-on-year-stats by %s' % key_attribute_name,
                           'f')
    parser.add_argument('-p', dest='do_percentages', action='store_true',
                        help='Display percentages rather than counts')
    parser.add_argument('-r', dest='do_year_read', action='store_true',
                        help='Display by year read (default is by year added)')
    parser.add_argument('-t', dest='do_totals', action='store_true',
                        help='Also show total books per year')
    args = parser.parse_args()
    validate_args(args)
    if args.do_year_read:
        year_key = 'year_read'
    else:
        year_key = 'year_added'

    books = read_file(args=args)
    report = YearOnYearReport(key_attribute, year_key)
    report.process(books)
    report.render(do_percentages=args.do_percentages,
                  do_totals=args.do_totals)
