#!/usr/bin/env python
"""
Classes/functions to transform raw data for reports
"""

from collections import defaultdict, Sequence
from functools import cmp_to_key


class ReadVsUnreadStats(object):
    def __init__(self, books, key_attribute, ignore_single_book_groups=True):

        # Would be nice to use counters, but I dunno if that's possible for two
        # counters and a generator?
        self.unread_count = defaultdict(int)
        self.read_count = defaultdict(int)
        self.grouping_count = defaultdict(int) # More efficient than unioning keys of the count dicts?
        self.ignore_single_book_groups = ignore_single_book_groups

        for book in books:
            for shelf in book.property_as_sequence(key_attribute):
                if shelf not in ('currently-reading', 'read', 'to-read'):
                    self.grouping_count[shelf] += 1
                    if book.status in ('currently-reading', 'read'):
                        self.read_count[shelf] += 1
                    else:
                        self.unread_count[shelf] += 1

    def process(self):
        self.stats = []
        for key in self.grouping_count:
            rd = self.read_count[key]
            ur = self.unread_count[key]
            if self.ignore_single_book_groups and (rd + ur) == 1:
                continue
            # print('%-30s : %5d%% %3d' % (author, read_count[author], unread_count[author]))
            try:
                self.stats.append((key, int(100 * (rd / (rd+ur))) , rd - ur))
            except ZeroDivisionError as err:
                # pdb.set_trace()
                logging.warning('%s has %d read, %d unread' % (key, rd, ur))
        return self # For chaining

    def render(self, output_function=print):
        def comparator(a, b):
            # print(a, b)
            # return int(a[1] - b[1])

            if a[1] == b[1]:
                diff_difference = abs(b[2]) - abs(a[2])
                if diff_difference == 0:
                    return 1 if a[0] > b[0] else -1 # Use the key as a last resort
                else:
                    return diff_difference
            else:
                return a[1] - b[1]

        for stat in sorted(self.stats, key=cmp_to_key(comparator)):
            output_function('%-30s : %5d%% %+3d %3d' % (stat[0], stat[1], stat[2],
                                             self.grouping_count[stat[0]]))
