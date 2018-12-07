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

import sys

from utils.export_reader import read_file
from utils.arguments import create_parser, validate_args

if __name__ == '__main__':
    parser = create_parser('List all books that are a member of one or more specified shelves, ' +
                      'and not a memmber of any shelves prefixed with ! or ~',
                      supported_args='fs')
    parser.add_argument('-m', dest='format', nargs='?',
                        help='Custom output format e.g. "{title} by {author}"')
    parser.add_argument('-p', dest='properties', action='append', default=[],
                        help='List value of property/properties')
    parser.add_argument('-P', dest='property_names', action='store_true',
                        help='List all property names')
    args = parser.parse_args()
    validate_args(args)

    books = read_file(args=args)
    if args.sort_properties:
        # TODO: support reverse sort (by prefixing prop name with ~?)
        #       Q: how would be do strings?  Have to go into cmp etc?
        def custom_sort_key(z):
            return [getattr(z, prop) for prop in args.sort_properties]
        # b = sorted(books, key=lambda z: getattr(z, args.sort_properties[0]))
        b = sorted(books, key=custom_sort_key)
        books = b

    for book in books:
        if args.property_names:
            try:
                print('\n'.join(book._properties()))
                sys.exit(1)
            except ValueError:
                continue
        if args.format:
            print(book.custom_format(args.format))
        else:
            print(book)
        for prop in args.properties:
            try:
                val = getattr(book, prop)
            except Exception as err:
                # Avoid blowing up on stuff like days_on_tbr_pile on unread
                # books
                val = 'Error (%s)' % (err)
            print('  %-20s : %s' % (prop, val))
