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

from collections import defaultdict, namedtuple, Counter
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
from isfdb_lib.identifier_related import get_authors_and_title_for_isbn
from title_related import get_all_related_title_ids
from normalize_author_name import normalize_name
from title_contents import (get_title_contents, render_pub, analyse_pub_contents)
from goodreads_related import (get_ids_from_goodreads_id,)




# novel is in theory irrelevant here, but if we have a novel included within
# an anthology or collection, it'll be useful to know about it
STORY_TYPES = ('shortfiction', 'novel',
               'novella', 'novelette', 'short story')

# Hashable* are for use in sets and as dict keys
HashableStory = namedtuple('HashableStory',
                           'title_id, title, year, ttype')
HashableAuthor = namedtuple('HashableAuthor',
                            'author_id, author') # TODO: aliases

# HashableTitles are intended for use on the published titles (anthologies or
# collections), not the individual short fiction stories
HashableTitle = namedtuple('HashableTitle',
                           'title_id, title')

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
    """
    Return two defaultdicts:
    * Mapping of author to set of stories
    * Mapping of HashableStory to titles they appear in
    """
    by_author = defaultdict(set) # maps author to stories

    story_to_pubs = defaultdict(set) # maps HashableStory to ...something...

    # not_found_count = 0 # TODO: deprecate/remove
    not_found = []

    total = 0 # books is a generator, so can't do len() on it
    find_method_counts = Counter()
    for book_num, book in enumerate(books):
        total += 1
        preferred_pub_ids = None
        try:
            pub_title_stuff = get_ids_from_goodreads_id(conn, book.book_id)
            first_entry = pub_title_stuff[0]
            title_id = first_entry['title_id']
            title = first_entry['title_title']
            preferred_pub_ids = {z['pub_id'] for z in pub_title_stuff}
            find_method_counts['goodreads_id'] += 1
        except BookNotFoundError:
            title_details = check_book_content(conn, book)
            if not title_details:
                # not_found_count += 1
                not_found.append(book)
                find_method_counts['not_found'] += 1
                continue
            title_id = title_details.title_id
            try:
                title = title_details.title
            except AttributeError:
                title = book.title
            find_method_counts['via_title'] += 1

        h_t = HashableTitle(title_id, title)
        # output_function(h_t)
        title_ids = get_all_related_title_ids(conn, title_id,
                                              only_same_languages=True)
        contents = get_title_contents(conn, title_ids)
        best_pub_id, best_contents = analyse_pub_contents(contents,
                                                          output_function=do_nothing)
        # render_pub(best_pub_id, best_contents)
        if best_contents:
            for story in best_contents:
                for author_key in story['authors']:
                    # TODO: support for pseudonyms
                    h_s = HashableStory(story['title_id'],
                                        story['title_title'],
                                        story['title_date'][:4],
                                        story['title_storylen'] or story['title_ttype'].lower())
                    by_author[author_key].add(h_s)
                    story_to_pubs[h_s].add(h_t)
                    # if h_s.title == 'Betrayals':
                    #    print(f'XXX {book_num}, {book} : {h_s}, {h_t} XXXX')
        else:
            logging.error(f'No contents found for {title}')

        #output_function()

    output_function('%d of %d/%d books not found' % (len(not_found),
                                                     total, book_num))
    output_function(find_method_counts.most_common())
    for i, book in enumerate(sorted(not_found, key=lambda z: z.title), 1):
        output_function('%2d. %s (GR ID= %d / %s)' % (i, book,
                                           book.book_id, book.goodreads_url))

    return by_author, story_to_pubs


def compare_title_contents_to_owned_stories(conn, title_id, story_to_pubs,
                                            output_function=print):
    """
    Work out which stories in anthology/collection title_id are or are not in story_to_pubs

    TODO: handle title variants (this needs work elsewhere in this script)
    """
    known_story_title_ids = {z.title_id for z in story_to_pubs.keys()}

    contents = get_title_contents(conn, [title_id])
    best_pub_id, best_contents = analyse_pub_contents(contents,
                                                      output_function=do_nothing)
    owned_stories = []
    unowned_stories = []
    if best_contents:
        for story in best_contents: # Note we don't iterate through authors, as this can cause dupes
            s_type = story['title_storylen'] or story['title_ttype'].lower()
            if s_type not in STORY_TYPES:
                continue # Ignore essays, coverart, etc
            if story['title_id'] in known_story_title_ids:
                owned_stories.append(story)
            else:
                unowned_stories.append(story)
    else:
        logging.error(f'No contents found for {title}')


    def output_story_list(stories):
        for i, story in enumerate(stories, 1):
            author_names = [z.name for z in story['authors']]
            authors_text = ', '.join(author_names)
            output_function('%2d. "%s" [%s] by %s' % (i, story['title_title'],
                                                      story['title_date'][:4],
                                                      authors_text))

    output_function('= Owned stories =\n')
    output_story_list(owned_stories)
    output_function('\n= Unowned stories =\n')
    output_story_list(unowned_stories)


if __name__ == '__main__':
    # Something else seems to be messing with logging levels - without setting
    # this explicitly here, we don't get WARNINGs?!?
    # logging.getLogger().setLevel(logging.WARNING)
    parser = create_parser('List all books matching filters, optionally ordered ' +
                           'and/or grouped.~',
                           supported_args='efs', report_on='book')
    parser.add_argument('-t', dest='title_id', nargs='?', type=int, default=None,
                        help='Compare stories in collection with anthology/collection of given '
                        'ISFDB title_id')
    args = parser.parse_args()
    validate_args(args)

    books = read_file(args=args)

    conn = get_connection()

    by_author, story_to_pubs = process_books(conn, books)

    if args.title_id is not None:
        # 36607
        compare_title_contents_to_owned_stories(conn, args.title_id, story_to_pubs)
        sys.exit(0)

    # compare_title_contents_to_owned_stories(conn, 2373543, story_to_pubs)
    # compare_title_contents_to_owned_stories(conn, 157779, story_to_pubs)

    sorted_authors = sorted(by_author.keys(), key=lambda z:z.name)


    #for author, works in sorted(by_author.items()):
    for author in sorted_authors:
        works = by_author[author]
        stories = [z for z in works if z.ttype in STORY_TYPES]

        if stories:
            print('\n= %s (%d) - %d stories =\n' % (author.name, author.id,
                                                   len(stories)))
            chronological = sorted(stories, key=lambda z: z.year)
            for i, story in enumerate(chronological, 1):
                pubs = ', '.join([z.title for z in story_to_pubs[story]])
                ac = len(story_to_pubs[story])
                appearance_count = f'{ac} times'
                if ac == 1:
                    appearance_count = 'once'
                elif ac == 2:
                    appearance_count = 'twice'

                print('%3d. %s [%s, %s] - appears %s in %s' %
                      (i, story.title,
                       story.year,
                       story.ttype,
                       appearance_count, pubs))
            print()
