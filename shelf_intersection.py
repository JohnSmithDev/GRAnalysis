#!/usr/bin/env python3
"""
List all books that are a member of one or more specified shelves, and
not a memmber of any shelves prefixed with ! or ~

Example usage:
  ./shelf_intersection.py to-read science-fiction ~british-author
returns all unread SF novels not written by British authors.

No checking is done on the validity/existence of the specified shelves.

Hint: !foo arguments are liable to confuse your shell (unless you quote/backslash
      them), so ~foo is recommended for convenience.

"""
import logging
import pdb
import sys

from goodreads_export_reader import TEST_FILE, read_file

def split_filters(shelves):
    """
    Given an iterable of filters, return 2 lists, the first of inclusive filters,
    the second of exclusive filters.  The leading ! or ~ on the latter will be
    stripped off.

    >>> split_filters(['yeah', '!nope', 'yep', '!nay'])
    set('yeah', 'yep'), set('nope', 'nay')
    """
    inc, exc = set(), set()
    for shelf in shelves:
        if shelf[0] in ('!', '~'):
            exc.add(shelf[1:])
        else:
            inc.add(shelf)
    return inc, exc


if __name__ == '__main__':
    inc_shelves, exc_shelves = split_filters(sys.argv[1:])
    if not inc_shelves and not exc_shelves:
        logging.error('Must specify at least one shelf')
        sys.exit(1)
    for book in read_file(TEST_FILE):
        if inc_shelves.issubset(book.shelves) and exc_shelves.isdisjoint(book.shelves):
            print(book)


