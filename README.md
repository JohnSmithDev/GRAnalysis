# GoodReads Analysis - Python tools for analysing CSV exports from GoodReads

A set of Python scripts and library code to process
[GoodReads](https://www.goodreads.com) data and
analyse it for personal preferences, to-be-read suggestions, and general
data interrogation.

## Dependencies

* Python 3
* Unixlike-terminal that can display Unicode characters
* A CSV export file from GoodReads

### Optional dependencies

* [colorama](https://pypi.org/project/colorama/) - for colour output
* Terminal that supports colour output

## Licence

GPL v3 - see [LICENCE.txt](licence.txt) for full text,

## Disclaimers

This project is no affiliation with GoodReads or its associated companies.

This project uses the facility GoodReads provides to export a user's data in
CSV format.  To the best of my knowledge, GoodReads makes no guarantees about
the future availability of that functionality, nor any commitment regarding
changes to it, both of which would likely break the functionality of this
project.

To the best of my knowledge, GoodReads does not document the format of the
CSV export file, beyond the column names, so some - possibly erroneous -
assumptions about how to process the data have been made.

Some data may be incorrect (e.g. page counts) or inconsistent (names of a
series of books) in GoodReads, and this will be reflected in the CSV export.
Furthermore, some data that appears correct in the GoodReads website and app
may not export correctly into the CSV.  Attempts are made in this project to
deal with some of these issues where possible, but any and all data should not
be considered 100% perfect.  More detail about these issues is described in
DATA_ISSUES.md

The quality of analysis and reports by this project is somewhat dependent on
how you use GoodReads.  This is described in more detail in
[ASSUMPTIONS.md](ASSUMPTIONS.md).

## Setup

First off, you need to get your data exported from GoodReads.  By default
this will be as a file named `goodreads_library_export.csv`.

As of September 2018, this can be generated as follows:

* Log into GoodReads in a browser
* Go to [https://www.goodreads.com/review/import](https://www.goodreads.com/review/import)
* Click "Export Library" button in the top right corner
* Wait for a link to appear, it should be titled something like
  "Your export from mm/dd/yyyy - hh:mm"
* Right-click/Save as on the link

## Running the scripts

All the scripts need to know where to get the data from.  You can pass the
name of the CSV file as the first argument to all the scripts e.g.


    goodreads $ ./least_read_decades.py ~/Downloads/goodreads_library_export_latest.csv
    1810s                          :     0%  -1   1
    1890s                          :     0%  -1   1
    1920s                          :     0%  -1   1
    1930s                          :     0%  -1   1
    ...
    ...
    goodreads $ ./shelf_intersection.py -f non-fiction -f british-author ~/Downloads/goodreads_library_export_latest.csv
    'My Grammar And I (Or Should That Be 'Me'?) Old-School Ways to Sharpen your English' by Caroline Taggart [2008], read
    'Unleashing Demons: The Inside Story of Brexit' by Craig Oliver [2016], to-read
    ....
    ....
    etc


This gets pretty tiresome, so you can alternatively set the environment
variable `GR_CSV_FILE` to be the location of the file, avoiding the need to
specify it on the command line.

A breakdown of the functionality of all the reports is in [REPORTS.md](REPORTS.md).

## Alternatives

There are a few other projects on GitHub or discoverable through Google which
do similar to this one - at the time I wrote the initial version of this, I
wasn't aware of their existence, so I don't know how comparable they are.


* [https://github.com/philippbayer/Goodreads_visualization](https://github.com/philippbayer/Goodreads_visualization)
* [https://almoturg.com/bookstats/](https://almoturg.com/bookstats/)
* [https://github.com/PaulKlinger/Bookstats](https://github.com/PaulKlinger/Bookstats) (source for the previous)
* [http://www.hoboes.com/Mimsy/hacks/goodreads-what-books-did-i-read-last-week-and-last-month/](http://www.hoboes.com/Mimsy/hacks/goodreads-what-books-did-i-read-last-week-and-last-month/)

