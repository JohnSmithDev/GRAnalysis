#!/usr/bin/env python3
"""
Show which decades are least read (in terms of books read/books owned)
"""

from utils.arguments import parse_args
from utils.export_reader import read_file
from utils.transformers import ReadVsUnreadReport

if __name__ == '__main__':
    args = parse_args('Show which decades are least read (in terms of books read/books owned)')

    books = read_file(args=args)
    ReadVsUnreadReport(books, 'decade',
                       ignore_single_book_groups=False).process().render()
