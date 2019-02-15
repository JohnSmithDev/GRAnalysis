You may notice that some data in your reports is wrong and/or inconsistent with
what you see in the GoodReads website or app.  Whilst no guarantees are made
about the correctness of the output of this project, there are some issues
with the data in the GoodReads CSV export that may explain this.

Many issues with the exported data can be semi-manually addressed via the use
of patch files - see the details at the bottom of this page.


# Issues with the export

## Incorrect or missing read date

I believe this can happen when a book has been marked as read, and then unread.
Even if the book is subsequently marked as read, the "original" deleted read
date can cause the "new" one not to be used.

## Works with multiple authors

Books that have been written by 2 - or more? - authors only get attributed to
a single author in the Author column export.  (I suspect this is the
alphabetically first author, but I haven't checked.)  Use the 'all authors'
property to pick up any additional authors.

Anthologies are credited to the editor.  There is an "Additional Authors"
column in the CSV which isn't (currently) used by this project, although it
doesn't seem to be always populated or complete - this is presumably an issue
with the data in GoodReads itself, rather than the export.

Some scripts take a `-a` argument to indicate that all authors, rather than
just the "primary" author, should be used.

# Issues with the data in GoodReads

## Incorrect or missing pagination

...

## Incorrect or missing publication date

...

## Inconsistent or missing series names

...


# Patch files

It is possible to address many data issues by manually creating textual patch
files.  These contain a list of properties and values to match books against,
and a list of properties and values to change on books that match.  Here is a
simple example:


    title=I, Partridge: We Need to Talk about Alan
    ---
    date_read=2017-04-18
    state=read

Any book with a matching title with have the read date and state updated
accordingly.

## Setting up for use of patch files

You can store patch files in one or more directories.  These are defined in
the environment variable `GR_PATCH_PATH`; if you need to store them in more
than one location (not sure why you would need to do this though), separate
the directories using a colom in standard Unixlike manner.

Any files - except for 'temp' files such as emacs tilde-suffixed files - in the
patch directories will be processed, in arbitrary order.  Currently only files
in the top level of those directories will be processed, but future releases of
this code may iterate through subdirectories, should the need for such
functionality arise.

Any filename format or suffix can be used, `.txt` is probably as good a suffix
as any.

## Creating patch files

A patch file can contain one or more sets of rules - it is up to you to
organize them in whatever way is most convenient or sensible for you.  The
format is:

  # An optional comment line that is ignored
  matchprop1=foo
  matchprop2=bar
  matchpropN=zzz
  ---
  changeprop1=alpha
  changeprop2=beta
  changepropN=omega

  # Blank lines indicate the end of one ruleset and the start of another
  matchprop1a=qwerty
  -
  changeprop1a=zxcvb

  # etc

The names of the properties that can be matched against or changed can be
obtained by running `shelf_intersection.py -P`.  Valid values are dependent
on the particular property, and could be dates in `yyyy-mm-dd` format, numbers
or just regular strings.  Any whitespace before or after the property name,
equals sign or value is stripped.

The switch freom matching properties to properties to be changed is indicated
by a line beginning with a minus sign/hyphen.  To aid readability, I use
three hyphens, but a single one, or a hundred are equally valid.

It is perfectly OK to have the same property in both match and change sections,
for example:

    author=Robert Galbraith
    ---
    author=J. K. Rowling





