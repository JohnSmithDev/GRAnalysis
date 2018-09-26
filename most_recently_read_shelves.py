#!/usr/bin/env python3
"""
Output a list of shelves, ordered by when a book from a shelf was most recently
read.
"""

from utils.arguments import parse_args
from utils.export_reader import read_file
from utils.transformers import LastReadReport

if __name__ == '__main__':
    args = parse_args('Display when a book from all shelves was most recently read')
    books = read_file(args=args)
    lrr = LastReadReport(books, 'user_shelves')
    lrr.process().render()
