# The reports

The reports broadly break down into 3 categories

* Reports to interrogate your data e.g. books which are on multiple shelves
* Reports on books you have read e.g. favourite authors/shelves/decades
* Reports on books you haven't read e.g. least read shelves/decades,
  visualization of to-be-read pile (aka TBR aka Mount Tsundoku)

## Command-line arguments

The reports take command-line arguments, many of which are shared between them.
Do `name_of_report.py -h' to see the help page documenting what any given
report script supports.

All reports take an argument to indicate where the CSV file from GoodReads is
located.  Because this is common, and annoying to retype, you can instead set
the `GR_CSV_FILE` environment variable to the file's location, which will remove
the need to specify it on each invocation.

### Filters

Scripts accepting `-f` filters can optionally filter only books that match
certain critera.  Multiple filters can be specified to indicate that only books
matching all the filter criteria should be displayed.  (This is a logical AND,
or intersection of the sets, if you prefer.)

There are two types of filters.

#### Shelf filters

These are just a single textual element, indicating that only books on a
particular named shelf should be included.  Alternatively, prefix the shelf name
with an exclamation-mark ! or tilde ~ to filter on books *not* on that shelf.

(Tip: The tilde variant may be preferable, as some Unix/Linux shells may try to
interpret strings prefixed with an exclamation mark as something else, causing
the filter to fail.)

#### Comparison filters

These are of the form `property comparator value`, and indicate that only books
where a property is equal/not equal/greater than/etc a particular value should
be included.

The supported properties are not yet documented outside of the code in
`utils/book.py`.

Supported comparators are:

* `=` or `==` - equals
* `!=` or `<>` - not equal to
* `~` or `~=` or `=~` - textual match (specifically, [regular expression](https://en.wikipedia.org/wiki/Regular_expression) match)
* `>` - greater than
* `>=` or `=>` greater or equal than
* `<` - less than
* `<=` or `=<` less or equal than

Values should be whatever makes sense in the context of any particular property.
Dates are supported in `yyyy-mm-dd` or `yyyy/mm/dd` formats.

#### Filter examples

* `-f non-fiction` - Show only books on the non-fiction shelf
* `-f ~non-fiction` - Exclude books on the non-fiction shelf
* `-f non-fiction -f british-author` - Show only books which are on both the non-fiction and british-author shelves
* `-f year > 2000` - Show only books published in the 21st century
* `-f author ~ john` - Show only books written by people with John in their name (note that search is case insensitive, and against the entire name, so authors with the surname Johnson would be included, for example

Note that certain scripts use some built-in filtering that cannot be
overridden, in order to produce sensible results.  e.g. Anything reporting
on your particular ratings will filter out books which you have not read.

## Limiting results

Scripts accepting a `-l <number>` argument will output no more than the
specified number of results.

## Colour configuration

Scripts accepting a `-c <colour-config-file>` argument will take a JSON
configuration file indicating how books on particular shelves or with particular
properties will be displayed.  (This JSON configuration format is not yet
documented, but an example file should give sufficient hints to the curious.)

## Data interrogation reports

### avg_page_count.py

Outputs the mean number of pages of particular groupings of books, additionally
indicating how many books are in that grouping.

![Average page count example output](images/avg_page_count.png "Average page count example")

Arguments accepted:

* `-f filters`

**Note**: this script currently reports for multiple groupings - shelves, decades,
rating, etc.  It is likely this single script will be split up into smaller
ones each reporting on a single grouping.

### publication_year.py

Outputs a list of books ordered by year.

![Publication year example output](images/publication_year.png "Publication year example")

Arguments accepted:

* `-f filters`
* -s - Output a blank line between years (this makes the output slightly more readable)

### shelf_intersection.py

Output a list of books (in arbitrary order) matching the supplied filters

![Shelf intersection example output](images/shelf_intersection.png "Shelf intersection example")

Arguments accepted:

* `-f filters`

**Note**: This is an older script that isn't radically different from
`publication_year.py` as it currently stands.

## Reports on books read

All of these reports automatically apply a filter to only include books which
have been read.

### best_ranked_*.py

For given groupsings of books, show what the average rating for the books in that
group is, along with the number of books in that group, and a graphical
representation of the rankings.

![Best ranked example output](images/best_ranked_decades.png "Best ranked example")

In the above example, 2 books from 1940s have been rated, one a 4-stars (blue)
and one at 5-starts (purple).

**Note**: Some of these scripts report by order of ranking, others by the
property value.  This may be configurable by a command-line argument in
future.

Arguments accepted:

* `-f filters`

## Reports on books to be read

### draw_tsundoku_by_*.py

Draw a graphical representation of all the books you are yet to read, and those
you have, colour coded by the type of book.

![Draw Tsundoku example output](images/draw_tsundoku.png "Draw Tsundoku example")

The upper "mountain" represents the books to be read, and the lower one
represents the books you have read, with the total books in each category
displayed at "ground level".

Arguments accepted:

* `-f filters`
* `-c colour-configuration-file`

The colour configuration is not yet documented, and requires a fair bit of
trial-and-error to get ideal results.  I have ideas for how a colour code might
be automagically generated that might produce OK renderings, but this is not
yet implemented.

### least_read_*.py

On the assumption that you might want to have read a diverse set of books, this
report shows which shelves/decades/etc in your collection are least read.

![Least read example output](images/least_read_decades.png "Least read example")

The percentage value is the number of books you have read, the second number
is the difference between the number read and the number to-read, and the final
number is the total number of books in this group.

### longest_on_tbr_pile.py

This report points out how shamefully long some books in your collection have
gone unread.

![Longest on TBR pile example output](images/longest_on_tbr_pile.png "Longest on TBR pile example")

Arguments accepted:

* `-f filters`
* `-l limit`
* `-p period` - do not show books that have been unread for less than a particular number of days (default 31)

**Note**: This report currently outputs both

* which books have been waiting to be read the longest
* which books have been read, but had to wait the longest before they eventually got read

As the latter is of less interest, this script is likely to be split up into
two separate reports, each only reporting on one of these groupings.

