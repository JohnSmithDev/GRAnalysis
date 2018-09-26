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

from utils.arguments import parse_args
from utils.colour_coding import rating_to_colours
from utils.export_reader import read_file, only_read_books
from utils.read_scatter_plot import ScatterPlot

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
