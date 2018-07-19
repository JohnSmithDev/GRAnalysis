#!/usr/bin/env python3
"""
Show which authors have the best average ranking.  Ignores authors for whom
only a single book has been read.
"""

from __future__ import division

from collections import defaultdict
from functools import cmp_to_key
import logging
import pdb

from utils.export_reader import TEST_FILE, read_file, only_read_books

if __name__ == '__main__':

    read_count = defaultdict(int)
    author_cumulative_rating = defaultdict(int)
    for book in read_file(TEST_FILE, filter_funcs=[only_read_books]):
        br = book.rating
        if br:
            read_count[book.author] += 1
            author_cumulative_rating[book.author] += br

    author_stats = []
    for author, rdr in read_count.items():
        rd = read_count[author]
        if rd > 1:
            av = author_cumulative_rating[author] / rd
            author_stats.append((author, av , rd))


    def comparator(a, b):
        if a[1] == b[1]:
            return abs(b[2]) - abs(a[2])
        else:
            return int(1000 * (b[1] - a[1])) # Has to be an int for some reason


    for stat in sorted(author_stats, key=cmp_to_key(comparator)):
        # Standard deviation would be good too, to gauge (un)reliability
        print('%-30s : %.2f / Books read: %3d' % (stat[0], stat[1], stat[2]))

