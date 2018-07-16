#!/usr/bin/env python3
"""
Show average page count for shelves and by decade of publication
"""

from __future__ import division

from collections import defaultdict, Counter
from functools import cmp_to_key
import logging
import pdb
import sys

from goodreads_export_reader import TEST_FILE, read_file

def calculate_average_page_counts(file, keys_func=None):
    ROGUE_KEY = '*Bad/missing pagination*'

    book_count = defaultdict(int)
    page_count = defaultdict(int)
    for book in read_file(TEST_FILE):
        pg = book.pagination
        keys = keys_func(book)
        if pg is not None: # Ignore books with no pagination value
            for subkey in keys:
                book_count[subkey] += 1
                page_count[subkey] += pg
        else:
            book_count[ROGUE_KEY] += 1
            page_count[ROGUE_KEY] += 0
    avgs = []
    for k, numerator in page_count.items():
        avgs.append((k,  int(numerator / book_count[k]), book_count[k]))

    return avgs


if __name__ == '__main__':

    def by_shelves(book):
        return book.shelves

    for k, v, c in sorted(calculate_average_page_counts(TEST_FILE, by_shelves),
                       key=lambda z: -z[1]):
        print('%-30s: %5d (%d)' % (k, v, c))

    print()

    def by_decade(book):
        return [book.decade]

    for k, v, c in sorted(calculate_average_page_counts(TEST_FILE, by_decade),
                       key=lambda z: z[0]):
        print('%-30s: %5d (%d)' % (k, v, c))


