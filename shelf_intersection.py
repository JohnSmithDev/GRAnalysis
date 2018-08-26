#!/usr/bin/env python3
"""
List all books that are a member of one or more specified shelves, and
not a memmber of any shelves prefixed with ! or ~

Example usage:
  ./shelf_intersection.py -f to-read -f science-fiction -f ~british-author
returns all unread SF novels not written by British authors.

No checking is done on the validity/existence of the specified shelves.

Hint: !foo arguments are liable to confuse your shell (unless you quote/backslash
      them), so ~foo is recommended for convenience.

"""
from utils.export_reader import read_file
from utils.arguments import parse_args

if __name__ == '__main__':
    args = parse_args('List all books that are a member of one or more specified shelves, and ' +
                      'not a memmber of any shelves prefixed with ! or ~',
                      supported_args='f')
    for book in read_file(args=args):
        print(book)

