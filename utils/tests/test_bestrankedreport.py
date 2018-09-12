#!/usr/bin/env python3

from decimal import Decimal
import unittest

from ..book import Book
from ..transformers import BestRankedStat, compare_brstat, BestRankedReport

class TestCompareBRStat(unittest.TestCase):

    PRIMARY_STAT = BestRankedStat('Foo', Decimal('3.1'), 22)
    SECONDARY_STAT = BestRankedStat('Bar', Decimal('4.2'), 11)

    STAT_WITH_SAME_AVERAGE = BestRankedStat('Baz', Decimal('3.1'), 15)
    IDENTICAL_STAT = BestRankedStat('Boo', Decimal('3.1'), 22)

    def test_compare_unalike_stats(self):
        # higher average comes first
        self.assertTrue(compare_brstat(self.PRIMARY_STAT, self.SECONDARY_STAT) > 0)
        self.assertTrue(compare_brstat(self.SECONDARY_STAT, self.PRIMARY_STAT) < 0)

    def test_compare_stats_with_same_average(self):
        # TODO (nice-to-have): We should fall back to sorting on the key name,
        # as in compare_rvustat()
        self.assertTrue(compare_brstat(self.PRIMARY_STAT, self.IDENTICAL_STAT) == 0)
        self.assertTrue(compare_brstat(self.IDENTICAL_STAT, self.PRIMARY_STAT) == 0)


class MockBookForReadVsUnreadReport(object):
    def __init__(self, keys, rating):
        self.keys = keys
        self.rating = rating

    def property_as_sequence(self, whatever):
        for k in self.keys:
            yield k

MOCK_BOOKS = [
    MockBookForReadVsUnreadReport(['foo'], 4),
    MockBookForReadVsUnreadReport(['bar'], 3),
    MockBookForReadVsUnreadReport(['baz'], 2),

    MockBookForReadVsUnreadReport(['foo'], 1),
    MockBookForReadVsUnreadReport(['bar'], 3),
    MockBookForReadVsUnreadReport(['baz'], 5),

    MockBookForReadVsUnreadReport(['foo'], None), # e.g. a book which was DNFed
    MockBookForReadVsUnreadReport(['bar'], 2),
    MockBookForReadVsUnreadReport(['baz'], 4)
]


class TestBestRankedReport(unittest.TestCase):
    def test_init(self):
        obj = BestRankedReport(MOCK_BOOKS, 'whatever')
        self.assertEqual({'foo': 2, 'bar': 3, 'baz': 3}, obj.rated_count)
        self.assertEqual({'foo': 5, 'bar': 8, 'baz': 11}, obj.cumulative_rating)
        self.assertEqual({'foo': [None, 1, 0, 0, 1, 0],
                          'bar': [None, 0, 1, 2, 0, 0],
                          'baz': [None, 0, 1, 0, 1, 1]},
                         obj.rating_groupings)

    def test_process(self):
        obj = BestRankedReport(MOCK_BOOKS, 'whatever')
        obj.process()
        # Sort both values tested as the ordering as arbitrary at this point
        self.assertEqual(sorted([
            BestRankedStat('foo', 2.5, 2),
            BestRankedStat('bar', 8 / 3, 3),
            BestRankedStat('baz', 11 / 3, 3),
            ]), sorted(obj.stats))

    def test_render(self):
        obj = BestRankedReport(MOCK_BOOKS, 'whatever')
        obj.process()

        ret = []
        def collate_strings(txt):
            ret.append(txt)

        # We could test the bar output, but it would be very messy due to use
        # of colour codes and Unicode.  If we do want to test it, it would
        # probably be better off testing the just the display module
        obj.render(output_function=collate_strings, output_bars=False)
        self.assertEqual([
            'baz                            : 3.67    3',
            'bar                            : 2.67    3',
            'foo                            : 2.50    2'
            ], ret)
