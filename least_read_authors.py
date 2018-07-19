#!/usr/bin/env python3
"""
Show which authors are least read (in terms of books read/books owned)
"""

from __future__ import division

from collections import defaultdict
from functools import cmp_to_key
import logging
import pdb

from utils.export_reader import TEST_FILE, read_file



if __name__ == '__main__':
    IGNORE_SINGLE_BOOK_AUTHORS = True

    # Would be nice to use counters, but I dunno if that's possible for two
    # counters and a generator?
    unread_count = defaultdict(int)
    read_count = defaultdict(int)
    author_count = defaultdict(int) # More efficient than unioning keys of the count dicts?
    for book in read_file(TEST_FILE):
        author_count[book.author] += 1
        if book.status in ('currently-reading', 'read'):
            read_count[book.author] += 1
        else:
            unread_count[book.author] += 1

    author_stats = []
    for author in author_count:
        rd = read_count[author]
        ur = unread_count[author]
        if IGNORE_SINGLE_BOOK_AUTHORS and (rd + ur) == 1:
            continue
        # print('%-30s : %5d%% %3d' % (author, read_count[author], unread_count[author]))
        try:
            author_stats.append((author, int(100 * (rd / (rd+ur))) , rd - ur))
        except ZeroDivisionError as err:
            # pdb.set_trace()
            logging.warning('%s has %d read, %d unread' % (author, rd, ur))

    def comparator(a, b):
        # print(a, b)
        # return int(a[1] - b[1])

        if a[1] == b[1]:
            return abs(b[2]) - abs(a[2])
        else:
            return a[1] - b[1]


    for stat in sorted(author_stats, key=cmp_to_key(comparator)):
        print('%-30s : %5d%% %3d %3d' % (stat[0], stat[1], stat[2], author_count[stat[0]]))

