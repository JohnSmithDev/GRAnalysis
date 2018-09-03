# GoodReads Analysis - Python tools for analysing CSV exports from GoodReads

A set of Python scripts and library code to process GoodReads data and
analyse it for personal preferences, to-be-read suggestions, and general
data interrogation.

## Dependencies

* Python 3
* Unixlike-terminal that can display Unicode characters
* A CSV export file from GoodReads

### Optional dependencies

* colorama - for colour output
* Terminal that supports colour output

## Licence

GPL v3 - see LICENCE.txt for full text

## Setup

First off, you need to get your data exported from GoodReads.  By default
this will be as a file named goodreads_library_export.csv

As of September 2018, this can be generated as follows:

* Log into GoodReads in a browser
* Go to https://www.goodreads.com/review/import
* Click "Export Library" button in the top right corner
* Wait for a link to appear, it should be titled something like
  "Your export from mm/dd/yyyy - hh:mm"
* Right-click/Save as on the link

## Running the scripts

All the scripts need to know where to get the data from.  You can pass the
name of the CSV file as the first argument to all the scripts e.g.

```
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
```

This gets pretty tiresome, so you can alternatively set the environment
variable GR_CSV_FILE to be the location of the file, avoiding the need to
specify it on the command line.

A breakdown of the functionality of all the reports is in REPORTS.md

## Alternatives

There are a few other projects on GitHub or discoverable through Google which
do similar to this one - at the time I wrote the initial version of this, I
wasn't aware of their existence, so I don't know how comparable they are.


* https://github.com/philippbayer/Goodreads_visualization
* https://almoturg.com/bookstats/ / https://github.com/PaulKlinger/Bookstats
* http://www.hoboes.com/Mimsy/hacks/goodreads-what-books-did-i-read-last-week-and-last-month/