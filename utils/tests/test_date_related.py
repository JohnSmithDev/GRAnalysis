#!/usr/bin/env python3

import unittest

from ..date_related import (monthstring, pad_month_list_as_tuples,
                             pad_month_list_as_strings)


class TestMonthString(unittest.TestCase):
    def test_vanilla(self):
        self.assertEqual('2018-09', monthstring(2018, 9))

    def test_custom_separator(self):
        self.assertEqual('2018X09', monthstring(2018, 9, separator='X'))


class TestMonthListTuples(unittest.TestCase):
    def test_same_year(self):
        self.assertEqual([(2018,4), (2018,5), (2018,6), (2018,7)],
                         list(pad_month_list_as_tuples(['2018-04', '2018-05', '2018-07'])))

    def test_adjacent_years(self):
        self.assertEqual([(2017, 10), (2017, 11), (2017, 12),
                          (2018, 1), (2018, 2), (2018, 3)],
                         list(pad_month_list_as_tuples(['2017-10', '2018-01', '2018-03'])))

    def test_several_years(self):
        self.assertEqual([(2016, 10), (2016, 11), (2016, 12),
                          (2017, 1), (2017, 2), (2017, 3),
                          (2017, 4), (2017, 5), (2017, 6),
                          (2017, 7), (2017, 8), (2017, 9),
                          (2017, 10), (2017, 11), (2017, 12),
                          (2018, 1), (2018, 2), (2018, 3)],
                         list(pad_month_list_as_tuples(['2016-10', '2017-01', '2018-03'])))

class TestMonthListStrings(unittest.TestCase):
    def test_same_year(self):
        self.assertEqual(['2018-04', '2018-05', '2018-06', '2018-07'],
                         list(pad_month_list_as_strings(['2018-04', '2018-05', '2018-07'])))

