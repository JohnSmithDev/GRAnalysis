#!/usr/bin/env python3
"""
Show average ranking of shelves, with a bar chart breaking down the rankings
"""

from __future__ import division

from collections import defaultdict
from functools import cmp_to_key
import logging
import pdb

from utils.export_reader import TEST_FILE, read_file, only_read_books
from utils.display import render_ratings_as_bar


if __name__ == '__main__':

    read_count = defaultdict(int)
    cumulative_rating = defaultdict(int)
    rating_groupings = defaultdict(lambda: [None, 0,0,0,0,0])
    for book in read_file(TEST_FILE, filter_funcs=[only_read_books]):
        br = book.rating
        if br:
            for shelf in book.shelves:
                read_count[shelf] += 1
                cumulative_rating[shelf] += br
                rating_groupings[shelf][br] += 1

    stats = []
    for k, rdr in read_count.items():
        rd = read_count[k]
        av = cumulative_rating[k] / rd
        stats.append((k, av , rd))

    def comparator(a, b):
        # print(a, b)
        # return int(a[1] - b[1])

        if a[1] == b[1]:
            return abs(b[2]) - abs(a[2])
        else:
            return int(1000 * (b[1] - a[1])) # Has to be an int for some reason


    # for stat in sorted(stats, cmp=comparator): # Python 2
    for stat in sorted(stats, key=cmp_to_key(comparator)):
        # Standard deviation would be good too, to gauge (un)reliability
        bars = render_ratings_as_bar(rating_groupings[stat[0]], unicode=True)

        print('%-30s : %.2f %4d %s' % (stat[0], stat[1], stat[2], bars))

