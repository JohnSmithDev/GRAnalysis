#!/usr/bin/env python3
"""
Show which years are least read (in terms of books read/books owned).

Additionally report on which years have no books.  (Skipping large gaps,
presumed to be the oldest time periods where relatively few books will be
owned for most people.)
"""

from utils.arguments import create_parser, validate_args
from utils.export_reader import read_file
from utils.transformers import ReadVsUnreadStats

MAX_GAP_TO_REPORT_ON = 10

if __name__ == '__main__':
    parser = create_parser('Show which years are least read (in terms of books read/books owned)')
    parser.add_argument('-g', dest='max_gap', type=int, nargs='?',
                        default=10, help='Only report gaps of N or fewer years')
    args = parser.parse_args()
    validate_args(args)


    books = read_file(args=args)
    stats = ReadVsUnreadStats(books, 'year',
                      ignore_single_book_groups=False)

    stats.process().render()

    years = sorted(stats.grouping_count.keys())

    prev_year = years[0]
    for year in years[1:]:
        # Q: I think there may be an off-by-one error here w.r.t. args.max_gap?
        if year != prev_year + 1 and \
           year - prev_year <= args.max_gap:
            if year == prev_year + 2:
                print('# No books in list which were published in %d' % (year - 1))
            else:
                print('# No books in list which were published between %d and %d' %
                      (prev_year + 1, year - 1))
        prev_year = year
