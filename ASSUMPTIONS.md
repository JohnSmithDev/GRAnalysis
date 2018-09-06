This project was originally put together to try to satisfy my own personal
wishes to analyse my book collection and reading habits beyond what the
GoodReads website and app provides.  Thus the functionality and logic is built
upon my usage patterns, which may or may not be shared by other people.

## Books are added as they are acquired

As far as I can see, GoodReads doesn't allow you to specify the date when you
acquire a book, which would be useful for any old books you've owned before you
joined GoodReads (or before GoodReads even existed).  This project assumes that
you add books to GoodReads as-and-when you acquire them.

If you don't do this - e.g. you only add books when you start or finish reading
them - then nothing should break, but any of the to-be-read aka Tsundoku
reports will probably be of minimal use.

## "Want to read" means you own a book, rather than you want to own it

It seems an omission to me that there isn't a way in GoodReads to show that
you want a book, similar to wish lists on Amazon, or holds on libraries or
OverDrive.  As such, I can imagine that many people will use the "Want to read"
(aka to-read) status for such books.

Again, doing that will - arguably - skew any to-be-read reports, as I don't
think it's reasonable to consider a book you don't (yet) own to be on your
to-be-read pile.

## Abandoned books

There is no functionality in this project for reporting on books which you
abandon part way through, but I can imagine that such a thing could be added
in the future.  Such hypothetical functionality would probably be based around
my usage patterns:

* Books are kept in "read" state
* Books I haven't finished are usually not rated
* Unfinished books are added to a "did-not-finish" shelf.  (Any functionality
  based on this shelving would also use clear synonyms such as "dnf",
  "abandoned", etc)
* If I did rate an unfinished book, this would be included in any statistics
  on average rating (unless a filter is applied based on the aforementioned
  shelving.)

