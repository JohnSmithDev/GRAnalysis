#!usr/bin/env python3

import unittest
from ..transformers import calculate_average_metric



class MockBookForCalculateAverageMetric(object):
    def __init__(self, shelves, decade, rating, pagination):
        self.shelves = shelves
        self.decade = decade
        self.rating = rating
        self.pagination = pagination

MOCK_BOOKS = [
    MockBookForCalculateAverageMetric(['alpha', 'beta', 'gamma'],
                                       '1980s', 4, 100),
    MockBookForCalculateAverageMetric(['alpha', 'gamma'],
                                       '1990s', 3, 200),
    MockBookForCalculateAverageMetric(['beta'],
                                       '2000s', None, 300),
    MockBookForCalculateAverageMetric(['gamma'],
                                       '2010s', 5, 400),
    MockBookForCalculateAverageMetric(['alpha'],
                                       '1980s', 1, 500),
    MockBookForCalculateAverageMetric(['beta', 'gamma'],
                                       '1980s', 3, 600),
    MockBookForCalculateAverageMetric(['alpha'],
                                       '2000s', 5, 700),
    MockBookForCalculateAverageMetric(['beta'],
                                       '2010s', 1, 800),
    MockBookForCalculateAverageMetric(['alpha', 'beta', 'gamma'],
                                       '2010s', None, 900),
    MockBookForCalculateAverageMetric(['alpha', 'gamma'],
                                       '2000s', 2, None)
    ]



class TestCalculateAverageMetric(unittest.TestCase):
    def test_by_shelf(self):
        data = sorted(calculate_average_metric(MOCK_BOOKS, 'shelves', 'pagination'))
        self.assertEqual([('*Bad/missing pagination*', 0.0, 1),
                          ('alpha', 480.0, 5), # 100+200+500+700+900=2400
                          ('beta', 540.0, 5), # 100+300+600+800+900=2700
                          ('gamma', 440.0, 5) # 100+200+400+600+900=2200
        ], data)

    def test_by_shelf_excluding_missing_pagination(self):
        data = sorted(calculate_average_metric(MOCK_BOOKS, 'shelves', 'pagination',
                                               include_missing_pagination=False))
        self.assertEqual([('alpha', 480.0, 5), # 100+200+500+700+900=2400
                          ('beta', 540.0, 5), # 100+300+600+800+900=2700
                          ('gamma', 440.0, 5) # 100+200+400+600+900=2200
        ], data)

    def test_by_decade(self):
        data = sorted(calculate_average_metric(MOCK_BOOKS, 'decade', 'pagination'))
        self.assertEqual([('*Bad/missing pagination*', 0.0, 1),
                          ('1980s', 400.0, 3), # 100+500+600
                          ('1990s', 200.0, 1), # 200
                          ('2000s', 500.0, 2), # 300+700 (+None)
                          ('2010s', 700.0, 3) # 400+800+900
        ], data)

    def test_by_rating(self):
        # Note the key argumetn to sorted - this is because the default will
        # try to sort using None, and blow up.  As the sort is just to ennsure
        # a consistent return that we can reliably test against, this is no
        # big deal.
        data = sorted(calculate_average_metric(MOCK_BOOKS, 'rating', 'pagination'),
                      key=lambda z: z[1])
        self.assertEqual([('*Bad/missing pagination*', 0.0, 1),
                          (4, 100.0, 1), # 100
                          (3, 400.0, 2), # 200+600
                          (5, 550.0, 2), # 400+700
                          (None, 600.0, 2), # 300+900 = 1200
                          (1, 650.0, 2), # 500+800
        ], data)
