#/usr/bin/env python3

from collections import namedtuple
from datetime import date

from utils.colorama_canvas import (ColoramaCanvas, Fore, Back, Style,
                                   ColourTextObject)
from utils.date_related import MONTH_LETTERS, monthstring, pad_month_list_as_tuples
from utils.transformers import get_keys_to_books_dict


TimelineStat = namedtuple('TimelineStat',
                          'number_of_books_added, number_of_books_read, percentage_read')


def generic_colour_function(bk):
    txt = u'\u2b24' if bk.is_read else u'\u00b7' # BLACK LARGE CIRCLE or MIDDLE DOT
    return ColourTextObject(Fore.RESET, Back.RESET, Style.RESET_ALL, txt)


class TimelineChart(object):

    def __init__(self, books, key_attribute='month_added'):
        self.month2books = get_keys_to_books_dict(books, key_attribute)

    def process(self):
        self.month_stats = {}
        for month, books in self.month2books.items():
            num_added = len(books)
            num_read = len([z for z in books if z.is_read])
            if num_added > 0:
                percentage = '%3d%%' % int(100 * num_read / len(books))
            else:
                percentage = 'N/A'
            self.month_stats[month] = TimelineStat(num_added, num_read,
                                                   percentage)
        return self

    def render(self, output_function=print, colour_function=generic_colour_function):
        # self._render_stats(output_function)
        self._render_canvas(output_function, colour_function)

    def _render_stats(self, output_function):
        """
        Not currently used, but may be helpful for debugging?
        """
        for month, books in sorted(self.month2books.items(),
                                   key=lambda z: z[0]):
            stat = self.month_stats[month]
            output_function('%s : %2d %2d %s' % (month,
                                                 stat.number_of_books_read,
                                                 stat.number_of_books_added,
                                                 stat.percentage_read))

    def _render_canvas(self, output_function, colour_function):
        # Note we skip first month - TODO: make this switchable
        # TODO2: do this more elegantly
        padded_months = list(pad_month_list_as_tuples(self.month2books.keys()))[1:]
        min_month = min(self.month2books.keys())
        del self.month2books[min_month]

        width = len(padded_months)
        height = max([len(z) for z in self.month2books.values()]) + 4
        cc = ColoramaCanvas(width + 5, # Extra bit added to account for year
                            height,
                            output_function=output_function)

        prev_y = None
        for i, (y, m) in enumerate(padded_months):
            cc.current_fg = Fore.WHITE
            cc.current_bg = Back.RESET
            cc.print_at(i, height -3, MONTH_LETTERS[m])
            if y != prev_y and m <= 8:
                cc.print_at(i, height -2, '|')
                cc.print_at(i, height -1, str(y))
            prev_y=y
            month = monthstring(y, m)

            cc.reset_style()

            try:
                # stat = self.month_stats[month] # Q: Do we need this?
                books = self.month2books[month]
            except KeyError:
                # This is a padded month with 0 books
                books = set()

            def sort_value(bk):
                if bk.is_read:
                    return bk.date_read or date(2999, 1, 1)
                else:
                    return date(3999, 1, 1)
            for j, bk in enumerate(sorted(books, key=sort_value)):
                cc.current_fg, cc.current_bg, cc.current_style, txt = colour_function(bk)
                cc.print_at(i, height-j -4, txt)
                cc.reset_style()

        cc.render()
