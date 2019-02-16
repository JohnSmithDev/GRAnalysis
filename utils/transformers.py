#!/usr/bin/env python3
"""
Classes/functions to transform raw data for reports - perhaps 'engines' might
be a better name?
"""

from __future__ import division

from collections import defaultdict, namedtuple
from datetime import date
from functools import cmp_to_key
import logging
import math

from utils.display import render_ratings_as_bar
from utils.helpers import generate_enumeration_prefix_format

# TODO (maybe): ReadVsUnreadStats() and best_ranked_report() have different
#               defaults for ignore_single_book_groups - this could be
#               confusing?  The reasoning for the current status quo is:
#               * For ReadVsUnread groups, any number of read or unread is
#                 relevant
#               * For group ranking, only having a single rank is not considered
#                 sufficient representation to be meaningful

ReadVsUnreadStat = namedtuple('ReadVsUnreadStat', 'key, percentage_read, read_count, unread_count')
def compare_rvustat(a, b):
    if a.percentage_read == b.percentage_read:
        a_difference = a.read_count - a.unread_count
        b_difference = b.read_count - b.unread_count
        diff_difference = abs(b_difference) - abs(a_difference)
        if diff_difference == 0:
            return 1 if a.key > b.key else -1 # Use the key as a last resort
        else:
            return diff_difference
    else:
        return a.percentage_read - b.percentage_read


class ReadVsUnreadReport(object):
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
                stat = ReadVsUnreadStat(key, int(100 * (rd / (rd+ur))) , rd, ur)
                self.stats.append(stat)
            except ZeroDivisionError as err:
                # Q: Can this actually happen, or am I just being over-paranoid?
                logging.warning('%s has %d read, %d unread' % (key, rd, ur))
        return self # For method chaining

    def render(self, output_function=print):
        for stat in sorted(self.stats, key=cmp_to_key(compare_rvustat)):
            diff = stat.read_count - stat.unread_count
            output_function('%-30s : %5d%% %+4d %4d' %
                            (str(stat.key)[:30],
                             stat.percentage_read,
                             diff,
                             self.grouping_count[stat.key]))



BestRankedStat = namedtuple('BestRankedStat',
                            'key, average_rating, number_of_books_rated, number_of_pages')
def compare_brstat(a, b):
    # TODO (maybe?): number of pages as a further tie-breaker
    if a.average_rating == b.average_rating:
        return b.number_of_books_rated - a.number_of_books_rated
    else:
        return int(1000 * (b.average_rating - a.average_rating)) # Has to be an int for some reason

class BestRankedReport(object):

    def __init__(self, books, key_attribute,
                       ignore_single_book_groups=False,
                       ignore_undefined_book_groups=True):
        self.ignore_single_book_groups = ignore_single_book_groups

        self.rated_count = defaultdict(int)
        self.cumulative_rating = defaultdict(int)
        self.page_count = defaultdict(int)
        # TODO (maybe): could/should this be a namedtuple or class?
        self.rating_groupings = defaultdict(lambda: [None, 0,0,0,0,0])

        for book in books:
            br = book.rating
            if br:
                for key in book.property_as_sequence(key_attribute):
                    if key or not ignore_undefined_book_groups:
                        self.rated_count[key] += 1
                        self.cumulative_rating[key] += br
                        self.rating_groupings[key][br] += 1
                        try:
                            self.page_count[key] += book.pagination
                        except TypeError as err:
                            logging.error('No pagination defined for %s' %
                                            (book.title))

    def process(self):
        # TODO (maybe): Should ignore_single_book_groups be an argument here,
        #               rather than in the constructor?
        self.stats = []
        for k, rdr in self.rated_count.items():
            av = self.cumulative_rating[k] / rdr
            pg = self.page_count[k]
            if not self.ignore_single_book_groups or rdr > 1:
                self.stats.append(BestRankedStat(k, av, rdr, pg))
        return self # For method chaining

    def render(self, output_function=print, sort_metric='ranking',
               output_bars=True, enumerate_output=False):
        """
        Strictly speaking, "enumerate_output" is a misnomer, as this outputs
        a rank number rather than a simple increment.  However they are
        conceptually similar enough that I think it's simpler to use the same
        name across all reports, especially from the end user UX point-of-view.
        """
        biggest_first = False
        if sort_metric[0] in ('-', '~', '!'):
            biggest_first = True
            sort_metric = sort_metric[1:]

        if sort_metric == 'ranking':
            sorting_key = cmp_to_key(compare_brstat)
        else:
            # Sort by name order
            sorting_key = lambda z: getattr(z, sort_metric)

        prefix = ''
        rank_number = 1
        prev_rank_value = None
        prefix_format = generate_enumeration_prefix_format(self.stats)
        for i, stat in enumerate(sorted(self.stats, key=sorting_key, reverse=biggest_first)):
            # Standard deviation would be good too, to gauge (un)reliability
            if output_bars:
                bars = ' ' + render_ratings_as_bar(self.rating_groupings[stat.key])
            else:
                bars = ''
            if prev_rank_value is None or sorting_key(stat) != prev_rank_value:
                rank_number = i + 1
                prev_rank_value = sorting_key(stat)
            if enumerate_output:
                prefix = prefix_format % (rank_number)
            if 'number_of_pages' in sort_metric:
                count_val = stat.number_of_pages
            else:
                count_val = stat.number_of_books_rated
            output_function('%s%-30s : %.2f %4d%s' % (prefix,
                                                      stat.key, stat.average_rating,
                                                      count_val, bars))


def best_ranked_report(books, key_attribute, output_function=print,
                       sort_metric='ranking',
                       ignore_single_book_groups=False,
                       ignore_undefined_book_groups=True,
                       enumerate_output=False):
    brr = BestRankedReport(books, key_attribute, ignore_single_book_groups,
                           ignore_undefined_book_groups)
    brr.process()
    brr.render(output_function, sort_metric, enumerate_output=enumerate_output)



def get_keys_to_books_dict(books, key_attribute,
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



LastReadDetail = namedtuple('LastReadDetails', 'key, days_ago, title, num_unread')

def last_read_detail_comparator(a, b):
    if a.days_ago == b.days_ago:
        if a.num_unread == b.num_unread:
            # return a.key - b.key # blows up on strings
            return 1 if a.key > b.key else -1
        else:
            return b.num_unread - a.num_unread
    else:
        return b.days_ago - a.days_ago

class LastReadReport(object):

    def __init__(self, books, key):
        self.key2books = get_keys_to_books_dict(books, key)

    def process(self, as_of_date=None):
        if as_of_date is None:
            as_of_date = date.today()

        self.data = []

        for key, books in self.key2books.items():
            read_books = [z for z in books if z.is_read and z.date_read is not None]
            try:
                most_recently_read_book = max(read_books, key=lambda z: z.date_read)
                most_recent_title = most_recently_read_book.title
                if len(most_recent_title) > 35:
                    most_recent_title = most_recent_title[:32] + '...'
                days_ago = (as_of_date - most_recently_read_book.date_read).days
            except ValueError:
                # Presumably no books read
                most_recent_title = 'N/A'
                days_ago = 0 # Ugly, but avoids breaking the print formatting below

            unread_books = [z for z in books if z.is_unread]
            self.data.append(LastReadDetail(key, days_ago, most_recent_title, len(unread_books)))
        return self

    def render(self, output_function=print):
        prev_title = prev_days = None
        for details in sorted(self.data, key=cmp_to_key(last_read_detail_comparator)):
            prefix = '%s (%d unread)' % (details.key, details.num_unread)
            if prev_title == details.title and prev_days == details.days_ago:
                output_function('%-40s:     "' % (prefix))
            else:
                if details.days_ago == 0:
                    suffix = 'No books read'
                else:
                    suffix = '%3d days ago (%s)' % (details.days_ago, details.title)
                output_function('%-40s: %s' % (prefix, suffix))

            prev_title = details.title
            prev_days = details.days_ago

def percentages_report(books, key_attribute, output_function=print):
    data = get_keys_to_books_dict(books, key_attribute)
    all_books = set()
    stats = []
    max_qty = 0
    for key, books in data.items():
        num_books = len(books)
        stats.append((key, num_books))
        all_books.update(books)
        if num_books > max_qty:
            max_qty = num_books
    total_books = len(all_books)
    max_key_length = max([len(str(z)) for z in data.keys()])
    max_qty_length = math.ceil(math.log(max_qty, 10)) + 1

    fmt = '%%-%ds : %%%dd (%%d%%%%)' % (max_key_length, max_qty_length)
    for key, qty in sorted(stats, key=lambda z: -z[1]):
        output_function(fmt % (key, qty, 100 * (qty/total_books)))
