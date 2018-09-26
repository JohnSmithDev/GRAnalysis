#!/usr/bin/env python3
"""
Output a list of shelves, ordered by when a book from a shelf was most recently
read.
"""

from utils.arguments import parse_args
from utils.export_reader import read_file
from utils.transformers import last_read_report

if __name__ == '__main__':
    args = parse_args('Display when a book from all shelves was most recently read')
    books = read_file(args=args)
    last_read_report(books, 'user_shelves')
