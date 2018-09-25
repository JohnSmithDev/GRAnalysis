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
from shutil import get_terminal_size

from utils.arguments import parse_args
from utils.colorama_canvas import (ColoramaCanvas, Fore, Back, Style,
                                   ColourTextObject)
from utils.colour_coding import rating_to_colours
from utils.date_related import MONTH_LETTERS, MONTH_ABBREVIATIONS
from utils.export_reader import read_file, only_read_books

SPACE_FOR_PUBLICATION_YEAR_LABELS = 5 # yyyy plus a space
SPACE_FOR_READ_DATE_LABELS = 2 # lines for year and month
BAND_HEIGHT = 5 # in characters
YEAR_WIDTHS = (4,6,12,24,36,48,60,72) # in characters

# There is no point having a grouping value smaller than BAND_HEIGHT, as
# the export only has publication year, not publication date
PUBLICATION_YEAR_GROUPINGS = (5, 10, 50, 100)


def year_to_grouping_start(y, g):
    return (y // g) * g

def year_to_group_of_years(y, g):
    start = year_to_grouping_start(y, g)
    return range(start, start + g)

def merge_years(year_counts, max_in_group, year_groupings=None):
    """
    Given a dict mapping years to quantities, return a tuple containing:
    * list of (start_year, end_year) tuples, where the specified inclusive
      range has no more than max_in_group elements
    * dict mapping years to data related to the previous element
    (The dict is a convenience to save the caller re-deriving the info from
     the list)

    year_groupings defines the granularity of ranges that can be merged to
    e.g. 5 years, 10 years, etc

    This is a crude implementation that destroys year_counts; I'm sure it
    could be done much better with a bit of extra thinking.
    """

    if year_groupings is None:
        year_groupings = PUBLICATION_YEAR_GROUPINGS
    ranges = []
    year_to_ranges = {}
    years_and_counts = sorted(year_counts.items())
    dont_go_earlier_than = None
    for year, count in years_and_counts:
        if year not in year_counts:
            # Assume it has already been merged
            # print('Skipping %d' % (year))
            continue
        # best_so_far = [year]
        best_so_far = year_to_group_of_years(year, year_groupings[0])
        for grouping in year_groupings[1:]:
            years = year_to_group_of_years(year, grouping)
            total = sum(year_counts[z] for z in years)
            if total > max_in_group or dont_go_earlier_than in years:
                break
            best_so_far = years
        r = (min(best_so_far), max(best_so_far))
        ranges.append(r)
        for y in best_so_far:
            year_to_ranges[y] = (len(ranges)-1, r[0], r[1]-r[0]+1 )
            del year_counts[y]
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

    def process(self, max_items_in_year_banding=None):
        if max_items_in_year_banding is None:
            # This seems to produce reasonable results
            max_items_in_year_banding = len(self.books) // 6

        time_groups = defaultdict(int) # Could we do this more simply with Counter?
        for bk in self.books:
            time_groups[bk.year] += 1

        self.ranges, self.year_factors = merge_years(time_groups, max_items_in_year_banding)
        return self

    def _calculate_chart_x_scale(self, max_width=200):
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
                # 48 chars => 4 chars per month has enough space for 3
                # letter abbreviations, but it looks a bit too busy
                if self.chars_per_year > 48:
                    month_list = MONTH_ABBREVIATIONS
                else:
                    month_list = MONTH_LETTERS
                for j, month in enumerate(month_list[1:]):
                    canvas.print_at(x_origin + (i * self.chars_per_year) +
                                    (j * (self.chars_per_year // 12)),
                                    y_origin + 1, month)

    def _render_publication_date_labels(self, canvas, width, height):
        for band_number, band in enumerate(self.ranges):
            canvas.current_fg = Fore.BLUE
            y_pos = height - \
                    (band_number * BAND_HEIGHT) - 1
            canvas.print_at(SPACE_FOR_PUBLICATION_YEAR_LABELS, y_pos,
                        u'\u2581 ' * (width//2)) # Lower one eighth block
            canvas.current_fg = Fore.RESET

            if band[0] != band[1]: # a range of years
                canvas.print_at(0, y_pos - 3, '%s' % (band[0]))
                canvas.print_at(1, y_pos - 2, 'to')
                canvas.print_at(0, y_pos - 1, '%s' % (band[1]))
            else: # a single year (probably won't happen, but cater for it anyway)
                canvas.print_at(0, y_pos - 2, band[0])


    def render(self, colour_function, render_width=None, render_height=None):
        if render_width is None or render_height is None:
            x, y = get_terminal_size((80, 40))
            if render_width is None:
                render_width = x - SPACE_FOR_PUBLICATION_YEAR_LABELS
            # For now, keep the band height hard coded as 5 chars

        self.chars_per_year = self._calculate_chart_x_scale(render_width)
        self.day_scale = self.chars_per_year / 365 # TODO: Account for leap years
        # print("chars per year: %s / day_scale: %s" % (self.chars_per_year,
        #                                               self.day_scale))

        #print("Publication years: %s to %s" % (self.min_year, self.max_year))
        #print("Read dates: %s to %s" % (self.min_read_date, self.max_read_date))
        #print("Read dates: %s to %s" % (self.min_chart_date, self.max_chart_date))

        CHART_WIDTH = (self.max_chart_date.year - self.min_chart_date.year + 1) * \
                      self.chars_per_year

        width = CHART_WIDTH + 2 + SPACE_FOR_PUBLICATION_YEAR_LABELS
        height = (len(self.ranges) * BAND_HEIGHT) + SPACE_FOR_READ_DATE_LABELS

        cc = ColoramaCanvas(width, height)
        self._render_read_date_labels(cc, SPACE_FOR_PUBLICATION_YEAR_LABELS, 0)
        self._render_publication_date_labels(cc, CHART_WIDTH, height)

        for bk in self.books:
            x_pos = int((bk.date_read - self.min_chart_date).days * self.day_scale)
            # y_pos = (self.max_chart_year - bk.year) // 2
            band_number, starting_year, year_range = self.year_factors[bk.year]
            offset_within_band = (bk.year - starting_year) / year_range
            y_pos = height - int((band_number + offset_within_band)* BAND_HEIGHT) -1

            cc.current_fg, cc.current_bg, cc.current_style, txt = colour_function(bk)

            cc.print_at(SPACE_FOR_PUBLICATION_YEAR_LABELS + x_pos, y_pos, txt)
        cc.render()

def only_books_with_publication_year(bk):
    return bk.year is not None

def only_books_with_read_date(bk):
    return bk.date_read is not None

if __name__ == '__main__':
    args = parse_args('Draw a scatter plot of all books read',
                      'f')

    books = read_file(args=args, filter_funcs=[only_read_books,
                                               only_books_with_read_date,
                                               only_books_with_publication_year])
    sp = ScatterPlot(books)
    sp.process()

    sp.render(colour_function=rating_to_colours)
