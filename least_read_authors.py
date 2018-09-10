#!/usr/bin/env python3
"""
Show which authors are least read (in terms of books read/books owned)
"""

from utils.arguments import parse_args
from utils.export_reader import read_file
from utils.transformers import ReadVsUnreadStats

if __name__ == '__main__':
    args = parse_args('Show which authors are least read (in terms of books read/books owned)',
                      'a')

    books = read_file(args=args)
    ReadVsUnreadStats(books, 'all_authors' if args.all_authors else 'author').process().render()
