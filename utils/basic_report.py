"""
This is the "engine" for the report historically called shelf_intersection.py -
however the shelf-intersection code is now generic and available in most (all?)
reports, and so that's a bit of a useless name now.

It provides basic sorting and grouping of books, but no real aggregation,
analysis or display functionality.
"""

import sys

from utils.helpers import generate_enumeration_prefix_format

GROUP_SEPARATOR = '---'

def process_books(books, args, output_function=print):
    prefix_format = '%d. '
    if args.sort_properties:
        # TODO: support reverse sort (by prefixing prop name with ~?)
        #       Q: how would be do strings?  Have to go into cmp etc?
        def custom_sort_key(z):
            return [getattr(z, prop) for prop in args.sort_properties]
        # BUG: this blows up if one value is None, e.g. a book without a rating
        b = sorted(books, key=custom_sort_key)
        books = b
    else:
        def custom_sort_key(z): # Dummy function to simplify later code
            return None
        if args.enumerate_output:
            # Only convert what may be a generator to a len()able object if we
            # have to
            b = list(books)
            books = b

    if args.enumerate_output:
        prefix_format = generate_enumeration_prefix_format(books)


    prefix = ''
    prev_sort_value = None
    for i, book in enumerate(books):
        sort_value = custom_sort_key(book)
        if args.inline_separator_with_breaks and sort_value != prev_sort_value \
            and sort_value:
            output_function(GROUP_SEPARATOR)
            output_function('/'.join([str(z) for z in sort_value]))
        prev_sort_value = sort_value
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

        # args.properties doesn't work especially well with inline output -
        # you'd be better off using a custom format
        for prop in args.properties:
            try:
                val = getattr(book, prop)
            except Exception as err:
                # Avoid blowing up on stuff like days_on_tbr_pile on unread
                # books
                val = 'Error (%s)' % (err)
            output_function('  %-20s : %s' % (prop, val))


def output_grouped_lists(output_bits, item_separator, output_function=print):
    def output_sublist(lst):
        if not lst:
            return
        output_function('%s: %s' % (lst[0], item_separator.join(lst[1:])))
    sublist = []
    for item in output_bits:
        if item == GROUP_SEPARATOR:
            output_sublist(sublist)
            sublist = []
        else:
            sublist.append(item)
    output_sublist(sublist)
