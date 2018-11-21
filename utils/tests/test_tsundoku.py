#!/usr/bin/env python3

from collections import namedtuple

import unittest
from .. import tsundoku


class TestTsundokuCalculateXPositions(unittest.TestCase):

    def test_calculate_x_positions_basic(self):
        counts = [tsundoku.Count('a', 10), tsundoku.Count('b', 8), tsundoku.Count('c', 6)]
        self.assertEquals([1, 0, 2], tsundoku.calculate_x_positions(counts))

    def test_calculate_x_positions_with_offset(self):
        counts = [tsundoku.Count('a', 10), tsundoku.Count('b', 8), tsundoku.Count('c', 6)]
        self.assertEquals([1, 0, 2], tsundoku.calculate_x_positions(counts, 0))

        counts = [tsundoku.Count('a', 10), tsundoku.Count('b', 8), tsundoku.Count('c', 6)]
        self.assertEquals([3, 2, 4], tsundoku.calculate_x_positions(counts, 2))

        counts = [tsundoku.Count('a', 10), tsundoku.Count('b', 8), tsundoku.Count('c', 6)]
        self.assertEquals([6, 5, 7], tsundoku.calculate_x_positions(counts, 5))

    def test_calculate_x_positions_with_duplicates(self):
        counts = [tsundoku.Count('a', 10), tsundoku.Count('a', 9),
                  tsundoku.Count('b', 5), tsundoku.Count('b', 5), tsundoku.Count('b', 5),
                  tsundoku.Count('c', 6)]
        self.assertEquals([2, 1, # a columns
                           3, 4, 5, # b columns
                           0 # c columns
        ], tsundoku.calculate_x_positions(counts))

    def test_calculate_x_positions_with_duplicates_and_offset(self):
        counts = [tsundoku.Count('a', 10), tsundoku.Count('a', 9),
                  tsundoku.Count('b', 5), tsundoku.Count('b', 5), tsundoku.Count('b', 5),
                  tsundoku.Count('c', 6)]
        self.assertEquals([5, 4, # a columns
                           6, 7, 8, # b columns
                           3 # c columns
        ], tsundoku.calculate_x_positions(counts, 3))


class TestTsundokuSquashCalculation(unittest.TestCase):

    def test_squash_calculation_no_squashing_needed(self):
        self.assertEquals([9], tsundoku._squash_calculation(9, 9))
        self.assertEquals([9], tsundoku._squash_calculation(9, 10))

    def test_squash_calculation_squashing_needed(self):
        self.assertEquals([3, 3, 3], tsundoku._squash_calculation(9, 3))
        self.assertEquals([3, 3, 3], tsundoku._squash_calculation(9, 4))
        self.assertEquals([5, 4], tsundoku._squash_calculation(9, 5))


if __name__ == '__main__':
    unittest.main()

