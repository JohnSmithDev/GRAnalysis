#!/usr/bin/env python3
"""
Aggregates multiple "Year in Books" pages to report on top (e.g. most read)
books/authors
"""

from collections import Counter, defaultdict, namedtuple
import json
import os
import pdb
from random import randrange
import requests
import sys
import time

AuthorAndTitle = namedtuple('AuthorAndTitle', 'author, title, book_id')

from bs4 import BeautifulSoup

id_to_author_title = {}
authors_to_books = {}

GR_DATA_FILE = os.path.join('/', 'proj', 'goodreads_analysis', 'personal', 'goodreads_data.json')
GR_BASE_URL = 'https://www.goodreads.com/'

def load_gr_data(filename=GR_DATA_FILE):
    try:
        with open(filename) as filestream:
            data = json.load(filestream)
    except FileNotFoundError as err:
        data = {'book_id_to_work_id': {}}
    return data

def save_gr_data(data, filename=GR_DATA_FILE):
    with open(filename, 'w') as filestream:
        json.dump(data, filestream)

def call_goodreads_api(url, http_method='GET', key=None, format='json'):
    if not url.startswith('http'):
        url = GR_BASE_URL + url
    if key:
        url = url + '?key=' + key

    if format:
        url += '&format=%s' % (format)

    req = requests.get(url)
    if req.status_code >= 400:
        raise Exception('Error getting %s from Goodreads - HTTP status %d' %
                        (url, req.status_code))
    if format == 'json':
        try:
            return req.json()
        except Exception as err:
            pdb.set_trace()
    else:
        return req.content # TODO: or is it content()?



def output_stats(count_data, subhead,
                 key_format_function,
                 heading=None, footer=None,
                 max_items=10, min_count=2):
    prev_count = None
    if heading is not None:
        print(heading)
    for i, (key, count) in enumerate(count_data.most_common(20)):
        if count < min_count:
            break
        if count != prev_count:
            if i > max_items:
                break
            print(subhead % (count))
            prev_count = count
        print(key_format_function(key))
    if footer is not None:
        print(footer)
    # print('%d books read by %d people' % (len(id_to_author_title), len(filenames)))


def chunkify(lst, size=10):
    # https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
    for i in range(0, len(lst), size):
        yield lst[i:i+size]

class YearInBooksReport(object):
    def __init__(self, gr_api_key=None):
        self.gr_api_key = gr_api_key

        self.book_stats = Counter()
        self.author_per_reader_stats = Counter()
        self.author_books = defaultdict(set)
        self.author_book_stats = Counter()

        self.gr_data = load_gr_data()


    def _get_work_ids(self, book_ids, max_items_per_api_request=10):
        id_map = self.gr_data['book_id_to_work_id'] # just to save typing
        unknown_book_ids = []
        for book_id in book_ids:
            if book_id not in id_map:
                unknown_book_ids.append(book_id)
        for chunk in chunkify(unknown_book_ids, 5):
            # print(chunk)
            ids_string = ','.join(chunk)
            data = call_goodreads_api('book/id_to_work_id/%s' % ids_string,
                                      key=self.gr_api_key)
            # Q: Could this be done more Pythonically with zip()?
            for i, work_id in enumerate(data['work_ids']):
                id_map[chunk[i]] = work_id
            time.sleep(randrange(5,20))


    def _process_page(self, filename):
        book_ids = set()
        author_to_book_ids = defaultdict(set)
        with open(filename) as html_data:
            soup = BeautifulSoup(html_data, 'lxml')
            book_divs = soup.findAll('div', {'data-resource-type': 'Book'})
            print('Found %d book_divs in %s' % (len(book_divs), filename))
            self._get_work_ids([bd['data-resource-id'] for bd in book_divs])
            save_gr_data(self.gr_data)

            for bd in book_divs:
                # Note that some books will appear twice - the shortest/longest/
                # most pop/least pop/highest rated headers

                # I thought data-resource-id would be a canonical ID for book, but
                # it seems not.  e.g. Consider Phlebas is 535073 and 8935689 - these
                # seem to be edition IDs.
                # img alt/title attributes can't be used because these are edition/
                # language dependent - would have to do a GR API lookup?
                book_id = bd['data-resource-id']
                work_id = self.gr_data['book_id_to_work_id'][book_id]

                img = bd.find('img')
                title_and_author = img['title']
                title, author = title_and_author.rsplit(' by ', 1)
                if work_id not in id_to_author_title:
                    id_to_author_title[work_id] = AuthorAndTitle(author, title, book_id)

                # print('%d,%s,%s' % (book_id, author, title))
                book_ids.add(work_id)
                canonical_author = id_to_author_title[work_id].author
                author_to_book_ids[canonical_author].add(work_id)
        # print(len(id_to_author_title))
        # pdb.set_trace()
        return book_ids, author_to_book_ids


    def generate_stats(self, filenames):
        for filename in filenames:
            book_ids, author_data = self._process_page(filename)
            self.book_stats.update(book_ids)
            self.author_per_reader_stats.update(author_data.keys())
            for author, book_ids in author_data.items():
                self.author_books[author].update(book_ids)

        for author, books in self.author_books.items():
            self.author_book_stats.update({author: len(books)})

        save_gr_data(self.gr_data)

    def output_report(self):
        def format_author_and_title_from_book_id(book_id):
            # The URLs are currently wrong because of the swtich from book IDs
            # work IDs
            """
            return '  (%s - %s)[https://www.goodreads.com/book/show/%d]' % \
                id_to_author_title[book_id]

            """
            return '  (%s - %s)[https://www.goodreads.com/book/show/%s]' % \
                id_to_author_title[book_id]
        output_stats(self.book_stats, '    *%d readers*', format_author_and_title_from_book_id,
                     heading='    **Most read books**', footer='')

        output_stats(self.author_per_reader_stats, '    *Authors read by %d readers*',
                     lambda z: '    %s' % (z),
                     heading='    **Most widely read authors**', footer='')

        output_stats(self.author_book_stats, '  *Authors with %d titles read*',
                     lambda z: '    %s' % (z),
                     max_items=40,
                     heading='    **Authors with most titles read**')

if __name__ == '__main__':
    # for filename in sys.argv[1:]:
    #    process_page(filename)
    gr_api_key = os.environ['GR_API_KEY']
    report = YearInBooksReport(gr_api_key)
    report.generate_stats(sys.argv[1:])
    report.output_report()
