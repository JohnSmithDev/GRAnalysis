#!/usr/bin/env python3
"""
Show year-by-year (read or added) stats over shelves (or other dimension derived
from symlinked filename)
"""

from collections import Counter

from utils.transformers import get_keys_to_books_dict

class YearOnYearReport(object):
    def __init__(self, key_attribute, year_key):
        self.key_attribute = key_attribute
        self.year_key = year_key

    def process(self, raw_books):
        books = list(raw_books) # We process it twice, so generator is no good

        self.number_of_books_by_year = {}
        for y, b in get_keys_to_books_dict(books, self.year_key).items():
            self.number_of_books_by_year[y] = len(b)

        data = get_keys_to_books_dict(books, self.key_attribute)
        self.min_year = 9999
        self.max_year = 0
        self.none_year_found = False

        self.max_key_length = 0
        self.key_to_year_counts = {}
        for key, book_subset in data.items():
            if len(key) > self.max_key_length:
                self.max_key_length = len(key)
            year_counts = Counter([getattr(bk, self.year_key) for bk in book_subset])
            self.key_to_year_counts[key] = year_counts
            if None in year_counts.keys():
                self.none_year_found = True
            actual_years = [z for z in year_counts.keys() if z]
            if actual_years: # Don't try to process empty lists, as min/max blow up
                miny = min(actual_years)
                if miny < self.min_year:
                    self.min_year = miny
                maxy = max(actual_years)
                if maxy > self.max_year:
                    self.max_year = maxy

    def render(self, do_percentages=False, do_totals=False,
               output_function=print):
        output_format = '%%-%ds %%s %%s' % (self.max_key_length)

        years = ' | '.join(str(y) for y in range(self.min_year, self.max_year+1))
        output_function(output_format % ('', ' ', years))
        for key, counts in sorted(self.key_to_year_counts.items()):
            year_vals = []
            for y in range(self.min_year, self.max_year+1):
                if y in counts:
                    if do_percentages:
                        if self.number_of_books_by_year.get(y, 0):
                            year_vals.append( '%3d%%' %
                                              (int(100 *
                                                   counts[y]/self.number_of_books_by_year[y])))
                        else:
                            year_vals.append( '    ')
                    else:
                        year_vals.append( '%4d' % (counts[y]) )
                else:
                    year_vals.append( '    ' )

            output_function(output_format % (key, ':', ' | '.join(year_vals)))

        if do_totals:
            output_function('-' * (self.max_key_length + 3 + (self.max_year-self.min_year + 1)*6))
            year_totals = ['%4d' % v for k, v in sorted(self.number_of_books_by_year.items())]
            output_function(output_format % ('Total', ':',
                                             ' | '.join(year_totals)))

