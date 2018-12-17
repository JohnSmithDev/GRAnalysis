#!/usr/bin/env python3

from utils.arguments import parse_args
from utils.export_reader import read_file
from utils.transformers import get_keys_to_books_dict, percentages_report

if __name__ == '__main__':
    args = parse_args('Show percentages of types of book',
                      'f')
    books = read_file(args=args)
    key_attribute = 'user_shelves'
    # key_attribute = 'rating'
    percentages_report(books, key_attribute)
