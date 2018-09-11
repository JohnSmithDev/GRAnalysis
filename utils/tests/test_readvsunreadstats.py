#!/usr/bin/env python3

import unittest

from ..transformers import ReadVsUnreadStat, compare_rvustat, ReadVsUnreadStats



class TestCompareRVUStat(unittest.TestCase):

    PRIMARY_STAT = ReadVsUnreadStat('Foo', 33, 1)
    SECONDARY_STAT = ReadVsUnreadStat('Bar', 55, 2)

    STAT_WITH_SAME_PERCENTAGE = ReadVsUnreadStat('Baz', 33, 3)
    STAT_WITH_SAME_PERCENTAGE_AND_DIFFERENCE = ReadVsUnreadStat('Boo', 33, 1)

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



