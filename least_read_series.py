#!/usr/bin/env python3
"""
Show which series are least read (in terms of books read vs books owned).

Note that this is only in terms of the books in the series you have recorded
in GoodReads, AFAIK there's no way of getting the complete series from the CSV
data.  (May be available via the API though - I haven't checked?)
"""

from utils.arguments import parse_args
from utils.export_reader import read_file
from utils.transformers import ReadVsUnreadStats

if __name__ == '__main__':
   args = parse_args('Show which series are least read (in terms of books read/books owned)')

   books = read_file(args=args)
   ReadVsUnreadStats(books, 'series',
                     ignore_single_book_groups=True).process().render()

