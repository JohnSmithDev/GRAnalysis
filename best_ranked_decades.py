#!/usr/bin/env python3
"""
Show which decades have best average rankings
"""

from __future__ import division

from collections import defaultdict
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
        bd = book.decade
        if br:
            read_count[bd] += 1
            cumulative_rating[bd] += br
            rating_groupings[bd][br] += 1

    stats = []
    for k, rdr in read_count.items():
        rd = read_count[k]
        if rd > 1:
            av = cumulative_rating[k] / rd
            stats.append((k, av , rd))

    # for stat in sorted(stats, cmp=comparator): # Python 2
    for stat in sorted(stats, key=lambda z: z[0]):
        # Standard deviation would be good too, to gauge (un)reliability
        bars = render_ratings_as_bar(rating_groupings[stat[0]], unicode=True)

        print('%-30s : %.2f %4d %s' % (stat[0], stat[1], stat[2], bars))


