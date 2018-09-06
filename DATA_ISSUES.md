You may notice that some data in your reports is wrong and/or inconsistent with
what you see in the GoodReads website or app.  Whilst no guarantees are made
about the correctness of the output of this project, there are some issues
with the data in the GoodReads CSV export that may explain this.

# Issues with the export

## Incorrect or missing read date

I believe this can happen when a book has been marked as read, and then unread.
Even if the book is subsequently marked as read, the "original" deleted read
date can cause the "new" one not to be used.

## Works with multiple authors

Books that have been written by 2 - or more? - authors only get attributed to
a single author in the export.  (I suspect this is the alphabetically first
author, but I haven't checked.)

Anthologies are credited to the editor.  There is an "Additional Authors"
column in the CSV which isn't (currently) used by this project, although it
doesn't seem to be always populated - this is presumably an issue with the
data in GoodReads itself, rather than the export.

# Issues with the data in GoodReads

## Incorrect or missing pagination

...

## Incorrect or missing publication date

...

## Inconsistent or missing series names

...