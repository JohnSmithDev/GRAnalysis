#!/usr/bin/env python3
"""
Output list of sorted books that have been read ordered by how long they were
TBR, as measured by date added vs date read.

Obviously this is highly dependent on how accurately you record your reading
activity, and - maybe more importantly - doesn't include any books you haven't
yet read (or are currently reading), which may well be many more than are listed
here.
"""

from functools import cmp_to_key

from utils.export_reader import TEST_FILE, read_file, only_read_books, \
    only_unread_books
from utils.display import render_ratings_as_bar

def output_report(books, min_period=None, max_books=None):
    for i, bk in enumerate(books):
        if (min_period and bk.days_on_tbr_pile < min_period) or \
           (max_books and i >= max_books):
            break
        print('%4d. %-60s : Days on TBR pile: %4d' %
              (i+1, bk.title[:58], bk.days_on_tbr_pile))


if __name__ == '__main__':
    MIN_PERIOD = 31
    MAX_BOOKS = 50
    def comparator(book_a, book_b):
        return book_b.days_on_tbr_pile - book_a.days_on_tbr_pile


    def only_valid_dates(bk):
        return bk.date_added and bk.date_read and (bk.date_read > bk.date_added)

    print('== Read books ==')
    read_books = sorted(read_file(TEST_FILE,
                                  filter_funcs=[only_read_books, only_valid_dates]),
                        key=cmp_to_key(comparator))
    output_report(read_books, MIN_PERIOD, MAX_BOOKS)


    print()

    print('== Unread books ==')
    unread_books = sorted(read_file(TEST_FILE,
                                    filter_funcs=[only_unread_books]),
                          key=cmp_to_key(comparator))
    output_report(unread_books, MIN_PERIOD, MAX_BOOKS)

