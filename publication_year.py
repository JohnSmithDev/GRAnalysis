#!/usr/bin/env python3
"""
Output list of books ordered by publication year.

NB: I believe this data in the export is not reliable (in part, this script
has been written to ascertain this).  UPDATE: looks like either "Year
Published" or "Original Publication Year" can be empty, but not both - at
least based on the books I own.
"""

from __future__ import division

from collections import defaultdict
from functools import cmp_to_key
import logging
import pdb

from goodreads_export_reader import TEST_FILE, read_file


def render_ratings_as_bar(ratings, width=50, unicode=False):
    total = sum(ratings[1:]) # Skip 0th item as we don't have 0 scores
    bits = []
    bodge_width = width - 1

    def unicode_bar_mapper(num):
        # https://en.wikipedia.org/wiki/Block_Elements
        return [None,    # 0 is not valid
                u'\u2581', # Lower one eight block
                u'\u2582', # Lower one quarter block
                u'\u2584', # Lower half block
                u'\u2586', # Lower three quarters block
                u'\u2588'][num] # Full block

    char_mapper = unicode_bar_mapper if unicode else str

    def bitlen(b):
        return sum([len(z) for z in b])

    while bitlen(bits) < width:
        # logging.warning('%f, %s, %d' % (bodge_width, bits, bitlen(bits)))
        bodge_width += 1
        bits = [char_mapper(z) * int(ratings[z] * (bodge_width/total))
                for z in range(1, 6)]

    return ''.join(bits)[:width]


if __name__ == '__main__':
    def comparator(a, b):
        # print(a, b)
        # return int(a[1] - b[1])

        if a[1] == b[1]:
            return abs(b[2]) - abs(a[2])
        else:
            return int(1000 * (b[1] - a[1])) # Has to be an int for some reason

    books_in_pub_date_order = sorted(read_file(TEST_FILE),
                                     key=lambda z: z.year or 9999)
    for b in books_in_pub_date_order:
        print('%s %-5s : %s' % (b.year or '????',
                              b.rating * '*' if b.rating else '',
                              b))
