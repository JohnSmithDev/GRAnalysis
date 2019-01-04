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

import logging
import sys

from utils.arguments import create_parser, validate_args
from utils.basic_report import process_books, output_grouped_lists
from utils.export_reader import read_file

if __name__ == '__main__':
    parser = create_parser('List all books matching filters, optionally ordered ' +
                      'and/or grouped.~',
                      supported_args='efs')
    parser.add_argument('-e', dest='enumerate_output', action='store_true',
                        help='Enumerate (i.e. prepend a counter) each book"')
    parser.add_argument('-i', dest='inline_separator', nargs='?',
                        help='Output results inline, separated by supplied value"')
    parser.add_argument('-I', dest='inline_separator_with_breaks', nargs='?',
                        help='As -i, but do line breaks when sort value (-s changes)"')
    parser.add_argument('-m', dest='format', nargs='?',
                        help='Custom output format e.g. "{title} by {author}"')
    parser.add_argument('-p', dest='properties', action='append', default=[],
                        help='List value of property/properties')
    parser.add_argument('-P', dest='property_names', action='store_true',
                        help='List all property names')
    args = parser.parse_args()
    validate_args(args)

    if args.inline_separator_with_breaks and not args.sort_properties:
        logging.error("Must specify sort properties (-s) when using -I")
        sys.exit(1)

    if args.inline_separator or args.inline_separator_with_breaks:
        separator = args.inline_separator or args.inline_separator_with_breaks
        output_bits = []
        def output_function(txt):
            output_bits.append(txt)
    else:
        output_function = print
        separator = None

    process_books(read_file(args=args), args, output_function)

    if separator:
        if args.inline_separator:
            print(separator.join(output_bits))
        else:
            output_grouped_lists(output_bits, separator)
