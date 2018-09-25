#!/usr/bin/env python3
"""
Draw a scatter plot of books read, by publication year and read date.

This is similar to the one available on the GoodReads website, but has the
following notable differences:
* The publication years are flexible so that periods where you have read
  relatively few periods are compressed compared to those where you have read
  a lot.
* The "dots" for each book indicate the rating you gave it.
"""

from collections import defaultdict
from datetime import date
import pdb

from utils.arguments import parse_args
from utils.colorama_canvas import (ColoramaCanvas, Fore, Back, Style,
                                   FG_RAINBOW, ColourTextObject)
from utils.colour_coding import rating_to_colours
from utils.date_related import MONTH_LETTERS
from utils.export_reader import read_file, only_read_books


# GROUPINGS = (1, 5, 10, 50, 100)
GROUPINGS = (5, 10, 50, 100)

def year_to_decade(y):
    return (y // 10) * 10

def year_to_grouping_start(y, g):
    return (y // g) * g

def year_to_group_of_years(y, g):
    start = year_to_grouping_start(y, g)
    return range(start, start + g)

def merge_years(time_groups, max_in_group):
    ranges = []
    year_to_ranges = {}
    years_and_counts = sorted(time_groups.items())
    dont_go_earlier_than = None
    for year, count in years_and_counts:
        if year not in time_groups:
            # Assume it has already been merged
            # print('Skipping %d' % (year))
            continue
        # best_so_far = [year]
        best_so_far = year_to_group_of_years(year, GROUPINGS[0])
        for grouping in GROUPINGS[1:]:
            years = year_to_group_of_years(year, grouping)
            total = sum(time_groups[z] for z in years)
            if total > max_in_group or dont_go_earlier_than in years:
                break
            best_so_far = years
        r = (min(best_so_far), max(best_so_far))
        ranges.append(r)
        for y in best_so_far:
            year_to_ranges[y] = (len(ranges)-1, r[0], r[1]-r[0]+1 )
            del time_groups[y]
        dont_go_earlier_than = max(best_so_far)

    # print(year_to_ranges)
    return ranges, year_to_ranges

class ScatterPlot(object):

    def __init__(self, books):
        self.books = list(books)

        # TODO (maybe): do this as one big 'manual' loop
        self.min_year = min([z.year for z in self.books])
        self.max_year = max([z.year for z in self.books])
        self.min_read_date = min([z.date_read for z in self.books])
        self.max_read_date = max([z.date_read for z in self.books])

        self.min_chart_date = date(self.min_read_date.year, 1, 1)
        self.max_chart_date = date(self.max_read_date.year, 12, 31)

        self.min_chart_year = year_to_decade(self.min_year)
        self.max_chart_year = year_to_decade(self.max_year) + 10

    def process(self):
        time_groups = defaultdict(int)
        # TODO: this will omit "interval" decades where no books were read
        for bk in self.books:
            # dec = year_to_decade(bk.year)
            time_groups[bk.year] += 1

        # for k, v in sorted(time_groups.items()):
        #     print(k,v)
        # print("Total read books: %d" % (len(self.books)))

        target = len(self.books) // 6
        self.ranges, self.year_factors = merge_years(time_groups, target)
        # print(self.ranges)
        return self

    def _calculate_chart_x_scale(self, max_width=200):
        YEAR_WIDTHS = (4,6,12,24,48,72) # in characters
        num_years = self.max_read_date.year - self.min_read_date.year + 1
        best_year_width = YEAR_WIDTHS[0]
        for yw in YEAR_WIDTHS[1:]:
            if yw * num_years > max_width:
                break
            best_year_width = yw
        return best_year_width

    def _render_read_date_labels(self, canvas, x_origin, y_origin):
        min_year = self.min_chart_date.year
        max_year = self.max_chart_date.year
        for i, year in enumerate(range(min_year, max_year+1)):
            if self.chars_per_year <=4:
                year_label = str(year % 100)
            else:
                year_label = str(year)
            canvas.print_at(x_origin + (i * self.chars_per_year),
                            y_origin, year_label)
            if self.chars_per_year >= 12:
                for j, month in enumerate(MONTH_LETTERS[1:]):
                    canvas.print_at(x_origin + (i * self.chars_per_year) +
                                    (j * (self.chars_per_year // 12)),
                                    y_origin + 1, month)

    def render(self):
        self.chars_per_year = self._calculate_chart_x_scale()
        self.day_scale = self.chars_per_year / 365
        # print("chars per year: %s / day_scale: %s" % (self.chars_per_year,
        #                                               self.day_scale))

        #print("Publication years: %s to %s" % (self.min_year, self.max_year))
        #print("Read dates: %s to %s" % (self.min_read_date, self.max_read_date))
        #print("Publication years: %s to %s" % (self.min_chart_year, self.max_chart_year))
        #print("Read dates: %s to %s" % (self.min_chart_date, self.max_chart_date))

        # X_SCALE = 8
        SPACE_FOR_PUBLICATION_YEAR_LABELS = 5
        # CHART_WIDTH = (self.max_chart_date - self.min_chart_date).days // X_SCALE
        CHART_WIDTH = (self.max_chart_date.year - self.min_chart_date.year + 1) * \
                      self.chars_per_year

        width = CHART_WIDTH + 2 + SPACE_FOR_PUBLICATION_YEAR_LABELS
        # height = self.max_chart_year - self.min_chart_year + 2


        SPACE_FOR_READ_DATE_LABELS = 2

        BAND_HEIGHT = 5
        height = (len(self.ranges) * BAND_HEIGHT) + SPACE_FOR_READ_DATE_LABELS

        cc = ColoramaCanvas(width, height)
        self._render_read_date_labels(cc, SPACE_FOR_PUBLICATION_YEAR_LABELS, 0)


        for band_number, band in enumerate(self.ranges):
            #if band_number % 2 == 0:
            #    cc.current_bg = Back.BLUE
            # else:
            #    cc.current_bg = Back.RESET
            #for y in range(BAND_HEIGHT):
            #    y_pos = (band_number* BAND_HEIGHT) + y
            #    cc.print_at(SPACE_FOR_YEAR_LABELS, y_pos, ' ' * (CHART_WIDTH-5))
            # cc.current_bg = Back.RESET

            cc.current_fg = Fore.BLUE
            y_pos = height - \
                    (band_number * BAND_HEIGHT) - 1
            cc.print_at(SPACE_FOR_PUBLICATION_YEAR_LABELS, y_pos,
                        u'\u2581 ' * (CHART_WIDTH//2)) # Lower one eighth block
            cc.current_fg = Fore.RESET


            if band[0] != band[1]:
                cc.print_at(0, y_pos - 3, '%s' % (band[0]))
                cc.print_at(1, y_pos - 2, 'to')
                cc.print_at(0, y_pos - 1, '%s' % (band[1]))
            else:
                cc.print_at(0, y_pos - 2, band[0])

        for bk in self.books:
            # x_pos = ((bk.date_read - self.min_chart_date).days // X_SCALE)
            x_pos = int((bk.date_read - self.min_chart_date).days * self.day_scale)
            # y_pos = (self.max_chart_year - bk.year) // 2
            band_number, starting_year, year_range = self.year_factors[bk.year]
            offset_within_band = (bk.year - starting_year) / year_range
            y_pos = height - int((band_number + offset_within_band)* BAND_HEIGHT) -1

            cc.current_fg, cc.current_bg, cc.current_style, txt = rating_to_colours(bk)

            cc.print_at(SPACE_FOR_PUBLICATION_YEAR_LABELS + x_pos, y_pos, txt)
        cc.render()

def only_books_with_publication_year(bk):
    return bk.year is not None

def only_books_with_read_date(bk):
    return bk.date_read is not None

if __name__ == '__main__':
    args = parse_args('Draw a scatter plot of all books read')

    books = read_file(args=args, filter_funcs=[only_read_books,
                                               only_books_with_read_date,
                                               only_books_with_publication_year])
    sp = ScatterPlot(books)
    sp.process().render()
