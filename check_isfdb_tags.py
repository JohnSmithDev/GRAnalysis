#!/usr/bin/env python3
"""
I DON'T THINK THIS EVER FULLY WORKED PROPERLY?

Go through a Goodreads CSV export, and report on what tags ISFDB has - or perhaps,
more pertinently, doesn't have - for that title.

Reguirements:
* isfdb_tools : https://github.com/JohnSmithDev/ISFDB-Tools
* A locally running/accessible MySQL/MariaDB instance of the ISFDB database
"""

import logging
import pdb
# import sys

from utils.arguments import create_parser, validate_args
# from utils.basic_report import process_books, output_grouped_lists
from utils.export_reader import read_file
from utils.colorama_canvas import Fore

# isfdb_tools
from common import get_connection
from find_book import (find_book_for_author_and_title, BookNotFoundError)
from tag_related import get_title_tags
from identifier_related import get_authors_and_title_for_isbn
# This isn't importable, and doesn't seem to be used anyway?!?!  TODO: remove
# from title_related import STANDALONE_TITLE_TYPES
from normalize_author_name import normalize_name

CORE_TAGS = set(['science fiction', 'fantasy', 'horror', 'alternate history',
                 'time travel', 'urban fantasy'])

# STANDALONE_TITLE_TYPES is too inclusive
# e.g.
# a COLLECTION of Fahrenheit and other novels?
# a CHAPBOOK of The Midwich Cuckoos?!? http://www.isfdb.org/cgi-bin/title.cgi?172997
TITLE_TYPES_OF_INTEREST = ['NOVEL']

LOW_TAG_COUNT_WARNING = 3

def isfdb_title_url(tid):
    return 'http://www.isfdb.org/cgi-bin/title.cgi?%d' % (tid)


def output_found_details(book, title_id_tags_map, output_function=print):
    for title_id, tag_details_generator in title_id_tags_map.items():

        # tag_details_generator = get_title_tags(conn, title_id)
        tag_details = [z for z in tag_details_generator]
        if len(tag_details) == 0:
            colour = Fore.LIGHTRED_EX
        elif len(tag_details) < LOW_TAG_COUNT_WARNING:
            colour = Fore.LIGHTBLUE_EX
        else:
            colour = ''
        output_function('%s%s by %s has %d tags in ISFDB %s %s' %
                        (colour,
                         book.clean_title,
                         book.author,
                         len(tag_details),
                         isfdb_title_url(title_id),
                         Fore.RESET
                        ))
        if len(tag_details) > 0:
            tag_names = {z.tag_name for z in tag_details}
            if tag_names.isdisjoint(CORE_TAGS):
                output_function('%s%s lacks a core tag: %s%s %s%s %s' %
                                (Fore.LIGHTYELLOW_EX,
                                 book.clean_title,
                                 Fore.LIGHTGREEN_EX,
                                 ','.join(tag_names),
                                 Fore.LIGHTYELLOW_EX,
                                 isfdb_title_url(title_id),
                                 Fore.RESET
                                ))


def check_tags_for_book(conn, book, output_function=print):
    """
    For a given book, output the ISFDB tags if it was found in that database.

    Returns True if book was found, else false
    """
    if book.isbn13:
        ret = get_authors_and_title_for_isbn(conn, book.isbn13 or book.isbn)
        output_function(ret)

    author_guesses = [book.author]
    normalized_author = normalize_name(book.author)
    if normalized_author:
        author_guesses.append(normalized_author)
        # output_function(author_guesses)

    for i, author in enumerate(author_guesses):
        # output_function('%d. Trying author %s and title %s' % (i, author, book.clean_title))
        try:
            # TODO: better handling of multiple authors, although possibly we
            # won't need it as the ISFDB code should be able to work with just one
            # author
            isfdb_id_list = find_book_for_author_and_title(conn, author,
                                                           book.clean_title
                                                           # title_types is not supported!?!
                                                           # ,
                                                           # title_types=TITLE_TYPES_OF_INTEREST
            )
            title_id_and_tags = {z.title_id: get_title_tags(conn, z.title_id)
                                                    for z in isfdb_id_list}
            output_found_details(book, title_id_and_tags, output_function=output_function)
            return True

        except UnicodeEncodeError:
            logging.error('Unicode error with "%s" or "%s" - skipping' % (author,
                                                                          book.clean_title))
        except BookNotFoundError:
            pass # We might have another author name to try
    else:
        logging.error('Could not find %s/%s in ISFDB - skipping' % (author_guesses,
                                                                    book.clean_title))
        return False

if __name__ == '__main__':
    # Something else seems to be messing with logging levels - without setting
    # this explicitly here, we don't get WARNINGs?!?
    # logging.getLogger().setLevel(logging.WARNING)
    parser = create_parser('List all books matching filters, optionally ordered ' +
                           'and/or grouped.~',
                           supported_args='efs', report_on='book')
    args = parser.parse_args()
    validate_args(args)

    books = read_file(args=args)

    mconn = get_connection()

    not_found_count = 0
    total = 0 # books is a generator, so can't do len() on it
    for bk in books:
        total += 1
        if check_tags_for_book(mconn, bk):
            pass
        else:
            not_found_count += 1

    print('%d of %d books not found' % (not_found_count, total))
