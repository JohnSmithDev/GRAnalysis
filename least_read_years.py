#!/usr/bin/env python3
"""
Show which years are least read (in terms of books read/books owned).

Additionally report on which years have no books.  (Skipping large gaps,
presumed to be the oldest time periods where relatively few books will be
owned for most people.)
"""

from utils.export_reader import TEST_FILE, read_file
from utils.transformers import ReadVsUnreadStats

MAX_GAP_TO_REPORT_ON = 10

if __name__ == '__main__':
    stats = ReadVsUnreadStats(read_file(TEST_FILE), 'year',
                      ignore_single_book_groups=False)

    stats.process().render()

    years = sorted(stats.grouping_count.keys())

    prev_year = years[0]
    for year in years[1:]:
        if year != prev_year + 1 and \
           year - prev_year < MAX_GAP_TO_REPORT_ON:
            if year == prev_year + 2:
                print('# No books in list that were published in %d' % (year - 1))
            else:
                print('# No books in list that were published between %d and %d' %
                      (prev_year + 1, year - 1))
        prev_year = year
