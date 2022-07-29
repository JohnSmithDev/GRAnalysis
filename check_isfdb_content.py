#!/usr/bin/env python3
"""

Go through a Goodreads CSV export, and report on the contents of the titles.

This is intended for use with anthology/collections


Reguirements:
* isfdb_tools : https://github.com/JohnSmithDev/ISFDB-Tools
* A locally running/accessible MySQL/MariaDB instance of the ISFDB database

TODO:
* normalize authors: e.g. Allen M. Steele vs Allen Steele
* normalize titles: e.g. SMcG's Hello, Hello (2015)
* show where stuff was published


"""

from collections import defaultdict, namedtuple
import logging
import pdb
import sys

from utils.arguments import create_parser, validate_args
from utils.basic_report import process_books, output_grouped_lists
from utils.export_reader import read_file
from utils.colorama_canvas import (ColoramaCanvas, Fore, Back, Style)

# isfdb_tools
from common import get_connection
from find_book import (find_book_for_author_and_title, BookNotFoundError)
from identifier_related import get_authors_and_title_for_isbn
from title_related import get_all_related_title_ids
# This isn't importable, and doesn't seem to be used anyway?!?!  TODO: remove
# from title_related import STANDALONE_TITLE_TYPES
from normalize_author_name import normalize_name
from title_contents import (get_title_contents, render_pub, analyse_pub_contents)
from goodreads_related import (get_ids_from_goodreads_id,)


# STANDALONE_TITLE_TYPES is too inclusive
# e.g.
# a COLLECTION of Fahrenheit and other novels?
# a CHAPBOOK of The Midwich Cuckoos?!? http://www.isfdb.org/cgi-bin/title.cgi?172997
TITLE_TYPES_OF_INTEREST = ['NOVEL']

HashableStory = namedtuple('HashableStory',
                           'title_id, title, year, ttype')


def do_nothing(*args, **kwargs):
    """Stub for functions that take an output_function argument"""
    pass

def isfdb_title_url(tid):
    return 'http://www.isfdb.org/cgi-bin/title.cgi?%d' % (tid)



def work_out_title_stuff(conn, book):
    """
    Given a GR-sourced book object, return a list of **SOMETHING** or raise
    BookNotFoundError

    If no ISBN, try to work out what the book is based on author and title
    """
    author_guesses = [book.author]
    normalized_author = normalize_name(book.author)
    if normalized_author:
        author_guesses.append(normalized_author)
        # print(author_guesses)

    for i, author in enumerate(author_guesses):
        # print('%d. Trying author %s and title %s' % (i, author, book.clean_title))
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
            return isfdb_id_list

        except UnicodeEncodeError:
            logging.error('Unicode error with "%s" or "%s" - skipping' % (author,
                                                                          book.clean_title))
        except BookNotFoundError:
            pass # We might have another author name to try

    raise BookNotFoundError(f"Couldn't find {book} in ISFDB")


def check_book_content(conn, book, output_function=print):
    if book.isbn13 or book.isbn:
        title_details = get_authors_and_title_for_isbn(conn, book.isbn13 or book.isbn)
        # output_function(title_details)
        return title_details
    else:
        try:
            title_details = work_out_title_stuff(conn, book)
            # output_function(title_details)
            return title_details[0]
        except BookNotFoundError as err:
            # TODO: make this a warning, and increase verbosity level
            logging.warning(f"No ISBNs for {book}, and couldn't work out ISFDB record")

    return None

def process_books(conn, books, output_function=print):
    by_author = defaultdict(set)

    # not_found_count = 0 # TODO: deprecate/remove
    not_found = []

    total = 0 # books is a generator, so can't do len() on it
    for book_num, book in enumerate(books):
        total += 1
        try:
            pub_title_stuff = get_ids_from_goodreads_id(conn, book.book_id)
            first_entry = pub_title_stuff[0]
            title_id = first_entry['title_id']
            title = first_entry['title_title']
        except BookNotFoundError:
            title_details = check_book_content(conn, book)
            if not title_details:
                # not_found_count += 1
                not_found.append(book)
                continue
            title_id = title_details.title_id
            try:
                title = title_details.title
            except AttributeError:
                title = book.title

        output_function(title_id, title)
        title_ids = get_all_related_title_ids(conn, title_id,
                                              only_same_languages=True)
        contents = get_title_contents(conn, title_ids)
        best_pub_id, best_contents = analyse_pub_contents(contents,
                                                          output_function=do_nothing)
        # render_pub(best_pub_id, best_contents)
        if best_contents:
            for story in best_contents:
                for author in story['authors']:
                    author_key = author.name
                    h_s = HashableStory(story['title_id'],
                                        story['title_title'],
                                        story['title_date'][:4],
                                        story['title_storylen'] or story['title_ttype'].lower())
                    by_author[author_key].add(h_s)
        else:
            logging.error(f'No contents found for {title}')

        output_function()

    output_function('%d of %d/%d books not found' % (len(not_found),
                                                     total, book_num))
    for i, book in enumerate(sorted(not_found, key=lambda z: z.title), 1):
        print('%2d. %s (GR ID= %d / %s)' % (i, book,
                                           book.book_id, book.goodreads_url))

    # sys.exit(1)

    return by_author

# novel is in theory irrelevant here, but if we have a novel included within
# an anthology or collection, it'll be useful to know about it
STORY_TYPES = ('shortfiction', 'novel',
               'novella', 'novelette', 'short story')


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

    conn = get_connection()

    by_author = process_books(conn, books)

    for author, works in sorted(by_author.items()):
        stories = [z for z in works if z.ttype in STORY_TYPES]

        if stories:
            print('\n= %s - %d stories =\n' % (author, len(stories)))
            chronological = sorted(stories, key=lambda z: z.year)
            for i, story in enumerate(chronological, 1):
                print('%3d. %s [%s, %s]' % (i, story.title,
                                               story.year,
                                               story.ttype))
            print()
