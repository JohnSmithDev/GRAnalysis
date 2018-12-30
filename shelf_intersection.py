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

import math
import sys

from utils.export_reader import read_file
from utils.arguments import create_parser, validate_args

if __name__ == '__main__':
    parser = create_parser('List all books that are a member of one or more specified shelves, ' +
                      'and not a memmber of any shelves prefixed with ! or ~',
                      supported_args='efs')
    parser.add_argument('-e', dest='enumerate_output', action='store_true',
                        help='Enumerate (i.e. prepend a counter) each book"')
    parser.add_argument('-i', dest='inline_separator', nargs='?',
                        help='Output results inline, separated by supplied value"')
    parser.add_argument('-m', dest='format', nargs='?',
                        help='Custom output format e.g. "{title} by {author}"')
    parser.add_argument('-p', dest='properties', action='append', default=[],
                        help='List value of property/properties')
    parser.add_argument('-P', dest='property_names', action='store_true',
                        help='List all property names')
    args = parser.parse_args()
    validate_args(args)

    prefix_format = '%d. '
    books = read_file(args=args)
    if args.sort_properties:
        # TODO: support reverse sort (by prefixing prop name with ~?)
        #       Q: how would be do strings?  Have to go into cmp etc?
        def custom_sort_key(z):
            return [getattr(z, prop) for prop in args.sort_properties]
        b = sorted(books, key=custom_sort_key)
        books = b
        prefix_format = '%%%dd. ' % (math.ceil(math.log(len(books), 10)))


    if args.inline_separator:
        output_bits = []
        def output_function(txt):
            output_bits.append(txt)
    else:
        output_function = print

    prefix = ''
    for i, book in enumerate(books):
        if args.property_names:
            try:
                output_function('\n'.join(book._properties()))
                sys.exit(1)
            except ValueError:
                continue
        if args.enumerate_output:
            prefix = prefix_format % (i + 1)
        if args.format:
            output_function('%s%s' % (prefix, book.custom_format(args.format)))
        else:
            output_function('%s%s' % (prefix, book))
        for prop in args.properties:
            try:
                val = getattr(book, prop)
            except Exception as err:
                # Avoid blowing up on stuff like days_on_tbr_pile on unread
                # books
                val = 'Error (%s)' % (err)
            output_function('  %-20s : %s' % (prop, val))

    if args.inline_separator:
        print(args.inline_separator.join(output_bits))
