#!/usr/bin/env python
"""
Show which authors are least read (in terms of books read/books owned)
"""

from __future__ import division

from collections import defaultdict
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

    read_count = defaultdict(int)
    cumulative_rating = defaultdict(int)
    rating_groupings = defaultdict(lambda: [None, 0,0,0,0,0])
    for book in read_file(TEST_FILE):
        br = book.rating
        if book.status in ('read') and br:
            for shelf in book.shelves:
                read_count[shelf] += 1
                cumulative_rating[shelf] += br
                rating_groupings[shelf][br] += 1

    stats = []
    for k, rdr in read_count.items():
        rd = read_count[k]
        if rd > 1:
            av = cumulative_rating[k] / rd
            stats.append((k, av , rd))


    def comparator(a, b):
        # print(a, b)
        # return int(a[1] - b[1])

        if a[1] == b[1]:
            return abs(b[2]) - abs(a[2])
        else:
            return int(1000 * (b[1] - a[1])) # Has to be an int for some reason


    for stat in sorted(stats, cmp=comparator):
        # Standard deviation would be good too, to gauge (un)reliability
        bars = render_ratings_as_bar(rating_groupings[stat[0]], unicode=True)

        print('%-30s : %.2f %4d %s' % (stat[0], stat[1], stat[2], bars))


