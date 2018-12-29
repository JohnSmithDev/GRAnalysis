#!/usr/bin/env python3

import unittest

from ..book import Book
from ..transformers import ReadVsUnreadStat, compare_rvustat, ReadVsUnreadReport



class TestCompareRVUStat(unittest.TestCase):

    # Since the reworking of the ReadVsUnreadStat class/namedtuple, the following
    # mock stats are slightly unrealistic.  TODO: redo them to be sensible
    PRIMARY_STAT = ReadVsUnreadStat('Foo', 33, 4, 1)
    SECONDARY_STAT = ReadVsUnreadStat('Bar', 55, 5, 3)

    STAT_WITH_SAME_PERCENTAGE = ReadVsUnreadStat('Baz', 33, 3, 0)
    STAT_WITH_SAME_PERCENTAGE_AND_DIFFERENCE = ReadVsUnreadStat('Boo', 33, 4, 1)

    def test_compare_unalike_stats(self):
        # smaller percentage comes first
        self.assertTrue(compare_rvustat(self.PRIMARY_STAT, self.SECONDARY_STAT) < 0)
        self.assertTrue(compare_rvustat(self.SECONDARY_STAT, self.PRIMARY_STAT) > 0)

    def test_compare_same_percentage_stats(self):
        # larger absolute difference comes first
        self.assertTrue(compare_rvustat(self.PRIMARY_STAT, self.STAT_WITH_SAME_PERCENTAGE) > 0)
        self.assertTrue(compare_rvustat(self.STAT_WITH_SAME_PERCENTAGE, self.PRIMARY_STAT) < 0)

    def test_compare_same_percentage_and_difference_stats(self):
        # alphabetically/numerically first key name comes first
        self.assertTrue(compare_rvustat(self.PRIMARY_STAT,
                                        self.STAT_WITH_SAME_PERCENTAGE_AND_DIFFERENCE) > 0)
        self.assertTrue(compare_rvustat(self.STAT_WITH_SAME_PERCENTAGE_AND_DIFFERENCE,
                                        self.PRIMARY_STAT) < 0)


class MockBookForReadVsUnreadReport(object):
    def __init__(self, keys, is_read):
        self.keys = keys
        self.is_read = is_read
        self.is_unread = not is_read

    def property_as_sequence(self, whatever):
        for k in self.keys:
            yield k

MOCK_BOOKS = [
    MockBookForReadVsUnreadReport(['foo'], True),
    MockBookForReadVsUnreadReport(['bar'], True),
    MockBookForReadVsUnreadReport(['baz'], True),

    MockBookForReadVsUnreadReport(['foo'], True),
    MockBookForReadVsUnreadReport(['bar'], True),
    MockBookForReadVsUnreadReport(['baz'], False),

    MockBookForReadVsUnreadReport(['foo'], False),
    MockBookForReadVsUnreadReport(['bar'], True),
    MockBookForReadVsUnreadReport(['baz'], False)
]

class TestReadVsUnreadReport(unittest.TestCase):
    def test_init(self):
        obj = ReadVsUnreadReport(MOCK_BOOKS, 'whatever')
        self.assertEqual({'foo': 2, 'bar': 3, 'baz': 1}, obj.read_count)
        self.assertEqual({'foo': 1, 'baz': 2}, obj.unread_count)
        self.assertEqual({'foo': 3, 'bar': 3, 'baz': 3}, obj.grouping_count)

    def test_process(self):
        obj = ReadVsUnreadReport(MOCK_BOOKS, 'whatever').process()
        # We sort both values here, because the order of the elements returned
        # from .process() is arbitrary
        self.assertEqual(sorted([ReadVsUnreadStat('baz', 33, -1),
                          ReadVsUnreadStat('foo', 66, 1),
                          ReadVsUnreadStat('bar', 100, 3)]),
                          sorted(obj.stats))

    def test_process(self):
        obj = ReadVsUnreadReport(MOCK_BOOKS, 'whatever').process()

        ret = []
        def collate_strings(txt):
            ret.append(txt)

        obj.render(output_function=collate_strings)
        self.assertEqual(['baz                            :    33%   -1    3',
                          'foo                            :    66%   +1    3',
                          'bar                            :   100%   +3    3'],
                          ret)


