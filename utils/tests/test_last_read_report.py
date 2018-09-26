#!/usr/bin/env python

from datetime import date
import unittest

from ..transformers import LastReadDetail, LastReadReport, last_read_detail_comparator



class TestLastReadDetailComparator(unittest.TestCase):
    FIRST_ITEM = LastReadDetail('foo', 33, 'Foo', 23)
    SECOND_ITEM = LastReadDetail('bar', 44, 'Bar', 11)

    ITEM_WITH_SAME_DAYS_AGO = LastReadDetail('baz', 33, 'Baz', 66)
    ITEM_WITH_SAME_DAYS_AGO_AND_COUNT = LastReadDetail('boo', 33, 'Boo', 23)

    def test_compare_unalike_items(self):
        # higher days ago comes first
        self.assertTrue(last_read_detail_comparator(self.FIRST_ITEM, self.SECOND_ITEM) > 0)
        self.assertTrue(last_read_detail_comparator(self.SECOND_ITEM, self.FIRST_ITEM) < 0)

    def test_compare_items_with_same_days_ago(self):
        # higher count comes first
        self.assertTrue(last_read_detail_comparator(self.FIRST_ITEM,
                                                    self.ITEM_WITH_SAME_DAYS_AGO) > 0)
        self.assertTrue(last_read_detail_comparator(self.ITEM_WITH_SAME_DAYS_AGO,
                                                    self.FIRST_ITEM) < 0)

    def test_compare_items_with_same_days_ago_and_count(self):
        # Order alphabetically/numerically on key
        self.assertTrue(last_read_detail_comparator(self.FIRST_ITEM, self.SECOND_ITEM) > 0)
        self.assertTrue(last_read_detail_comparator(self.SECOND_ITEM, self.FIRST_ITEM) < 0)

class MockBookForTestLastReadReport(object):
    def __init__(self, is_read, date_read, title):
        self.is_read = is_read
        self.is_unread = not is_read
        self.date_read = date_read
        self.title = title


class TestLastReadReport(unittest.TestCase):
    def test_last_read_report_process(self):
        lrr = LastReadReport([], 'whatever')
        lrr.key2books = {
            'foo': [MockBookForTestLastReadReport(True, date(2010,1,1), 'Foo1'),
                    MockBookForTestLastReadReport(False, None, 'Foo2'),
                    MockBookForTestLastReadReport(True, date(2010,4,1), 'Foo3')],
            'bar': [MockBookForTestLastReadReport(True, date(2011,1,1), 'Bar1'),
                    MockBookForTestLastReadReport(False, None, 'Bar2')],
            'baz': [MockBookForTestLastReadReport(True, date(2012,1,1), 'Baz1'),
                    MockBookForTestLastReadReport(True, None, 'Baz2'), # Note missing read date
                    MockBookForTestLastReadReport(False, None, 'Baz3'),
                    MockBookForTestLastReadReport(True, date(2012,4,1), 'Baz4')]
            }
        lrr.process(as_of_date=date(2013,1,1))
        self.assertEqual([LastReadDetail('bar', 731, 'Bar1', 1),
                          LastReadDetail('baz', 275, 'Baz4', 1),
                          LastReadDetail('foo', 1006, 'Foo3', 1)],
                         sorted(lrr.data))





