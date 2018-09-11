#!/usr/bin/env python3
"""
Classes/functions to transform raw data for reports
"""

from __future__ import division

from collections import defaultdict, namedtuple
from functools import cmp_to_key

from utils.display import render_ratings_as_bar

# TODO (maybe): ReadVsUnreadStats() and best_ranked_report() have different
#               defaults for ignore_single_book_groups - this could be
#               confusing?  The reasoning for the current status quo is:
#               * For ReadVsUnread groups, any number of read or unread is
#                 relevant
#               * For group ranking, only having a single rank is not considered
#                 sufficient representation to be meaningful

ReadVsUnreadStat = namedtuple('ReadVsUnreadStat', 'key, percentage_read, difference')
def compare_rvustat(a, b):
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


# TODO: rename to be less similar to the namedtuple above
class ReadVsUnreadStats(object):
    def __init__(self, books, key_attribute, ignore_single_book_groups=True,
                 ignore_undefined_book_groups=True):
        # Would be nice to use counters, but I dunno if that's possible for two
        # counters and a generator?
        self.unread_count = defaultdict(int)
        self.read_count = defaultdict(int)
        self.grouping_count = defaultdict(int) # More efficient than unioning keys of the count dicts?
        self.ignore_single_book_groups = ignore_single_book_groups

        for book in books:
            for key in book.property_as_sequence(key_attribute):
                if key or not ignore_undefined_book_groups:
                    self.grouping_count[key] += 1
                    if book.is_unread:
                        self.unread_count[key] += 1
                    else:
                        self.read_count[key] += 1

    def process(self):
        self.stats = []
        for key in self.grouping_count:
            rd = self.read_count[key]
            ur = self.unread_count[key]
            if self.ignore_single_book_groups and (rd + ur) == 1:
                continue
            try:
                stat = ReadVsUnreadStat(key, int(100 * (rd / (rd+ur))) , rd - ur)
                self.stats.append(stat)
            except ZeroDivisionError as err:
                # Q: Can this actually happen, or am I just being over-paranoid?
                logging.warning('%s has %d read, %d unread' % (key, rd, ur))
        return self # For method chaining

    def render(self, output_function=print):
        for stat in sorted(self.stats, key=cmp_to_key(compare_rvustat)):
            output_function('%-30s : %5d%% %+3d %3d' % (str(stat[0])[:30], stat[1], stat[2],
                                             self.grouping_count[stat[0]]))




def best_ranked_report(books, key_attribute, output_function=print, sort_by_ranking=True,
                       ignore_single_book_groups=False,
                       ignore_undefined_book_groups=True):
    read_count = defaultdict(int)
    cumulative_rating = defaultdict(int)

    # TODO: This seems an ideal use case for NamedTuple
    rating_groupings = defaultdict(lambda: [None, 0,0,0,0,0])
    for book in books:
        br = book.rating
        if br:
            for key in book.property_as_sequence(key_attribute):
                if key or not ignore_undefined_book_groups:
                    read_count[key] += 1
                    cumulative_rating[key] += br
                    rating_groupings[key][br] += 1

    stats = []
    for k, rdr in read_count.items():
        rd = read_count[k]
        av = cumulative_rating[k] / rd
        stats.append((k, av , rd))

    def comparator(a, b):
        if a[1] == b[1]:
            return abs(b[2]) - abs(a[2])
        else:
            return int(1000 * (b[1] - a[1])) # Has to be an int for some reason


    if sort_by_ranking:
        sorting_key=cmp_to_key(comparator)
    else:
        # Sort by name order
        sorting_key=lambda z: z[0]
    for stat in sorted(stats, key=sorting_key):
        # Standard deviation would be good too, to gauge (un)reliability
        bars = render_ratings_as_bar(rating_groupings[stat[0]])

        if not ignore_single_book_groups or stat[2] > 1:
            output_function('%-30s : %.2f %4d %s' % (stat[0], stat[1], stat[2], bars))


def get_keys_to_books_dict(books, key_attribute, output_function=print, sort_by_ranking=True,
                       ignore_single_book_groups=False,
                       ignore_undefined_book_groups=True):
    """
    Return a dictionary mapping some keys (e.g. shelves, dictionaries, etc)
    to sets of Books
    """

    ret_dict = defaultdict(set)
    for book in books:
        for key in book.property_as_sequence(key_attribute):
            if key or not ignore_undefined_book_groups:
                ret_dict[key].add(book)
    return ret_dict
