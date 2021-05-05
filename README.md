`tagfarm`
=========

_Version 0.3_
| _Entry_ [@ catseye.tc](https://catseye.tc/node/tagfarm)
| _See also:_ [shelf](https://github.com/catseye/shelf#readme)
∘ [ellsync](https://github.com/catseye/ellsync#readme)
∘ [yastasoti](https://github.com/catseye/yastasoti#readme)

- - - -

<img align="right" src="images/tagfarm-logo.png?raw=true" />

**tagfarm** is an ultra-lightweight filesystem-based categorization system for arbitrary files.

Motivation
----------

The limitation of a hierarchical filesystem is that any one file can only reside in one
directory.  But most files are best described by classifying them in more than one
category.  So directories don't map very well to categories -- if you have a picture of
the Mona Lisa, should you put it in `Portraits` or `Works by Leonardo da Vinci` or
`Enigmatic Smiles`?

The solution on blogs and wikis is to use "tags" or "categories", to allow every page
to be tagged with zero or more tags, and to allow all pages with a given tag to be listed
in a "tag index" or "category page".

tagfarm implements the same idea on a local filesystem.  Each tag is implemented as a
directory containing symbolic links to the files that have that tag.  And this is *all*
it consists of.

There are several advantages to this.  There's no metadata to go out of sync, no database
engine to install and maintain.  When you move files around, you can just run
`tagfarm repair` to rewrite the tag links.  You can treat the tag links as you would any
other file — for example, you can remove a tag from a file just by deleting the tag link.

There are also some disadvantages, of course.  Primarily, any limitations that your
filesystem has are also going to be imposed on the categorization system.  So, for
example, if your OS has performance problems listing 10,000 files in a single directory,
the same would hold for a set of 10,000 files that are tagged with the same tag.

Quick start
-----------

Make sure you have Python installed, clone this repository, and put its `bin` directory on
your executable search path.  You can then run `tagfarm` from your terminal.

Overview
--------

### Media tree

`tagfarm` operates on a part of your filesystem it calls the *media tree*.  There may be
multiple media trees in your filesystem.  The topmost directory of a media tree is called
the *media root* and it is identified by having a directory
called `by-tag` in it.  When `tagfarm` is started, it finds the media root it will operate
on, by looking for the `by-tag` directory, first in the current directory, then in every
successive parent directory thereof.  If it reaches `/` without having found a `by-tag`
directory, it exits immediately with an error code.

One constraint that applies to the media tree is that every file in it should have a
unique name.  This allows `tagfarm repair` to recreate fix broken tag links when a file is
moved around inside the media tree.

### `tag` and `untag`

You can add a tag to one or more files with the command

    tagfarm tag <tagname> <filename> [<filename2>...]

You can then list the contents of `by-tag/<tagname>` and see there are symlinks there.

You can remove a tag to one or more files with the command

    tagfarm untag <tagname> <filename> [<filename2>...]

### `showtags`

You can list the tags that have been applied to one or more files with

    tagfarm showtags <filename> [<filename2>...]

### `repair`

If the source files are moved around, the symbolic links will break.  Assuming the
files, after having moved, have not changed names and are still found somewhere in
the media tree, tagfarm can repair the broken links with the command

    tagfarm repair

By default, tagfarm will only attempt to repair broken links if they are actually
symlinks (not, for example, regular files) and not broken.  To have it replace all files
it happens to find in the tag link directory, pass `--force-relink`.  This is occasionally
handy for converting a directory full of copies of elsewhere-existing media files,
into links.  In conjunction with this, `--restrict-to-tag` may be used to name a single tag,
and this operation will be applied only to that tag.

`tagfarm repair` will also replace any links it finds that have absolute target paths,
with ones with relative target paths, even when the link is not broken.

`tagfarm repair` will also, when processing a link whose name is like `Link to xyz`,
rename it to simply `xyz`.  This is to handle the case where links are manually
created in a tag directory using a tools such as Nautilus (Gnome Desktop).

### `rename`

    tagfarm rename <oldfilename> <newfilename>

Renames the file, like `mv`, but also updates any tags that might be on it.

### `collect`

    tagfarm collect <tagname> <destdir>

Convenience command to move all the files with a given tag into a destination directory.
If the destination directory does not yet exist, will be created.  The tags of the files
are not changed.  At the end, `tagfarm repair` is called to update the tag links.

Other operations
----------------

The advantage of tagfarm being ultra-lightweight is that if there is something that
it does not directly support, it's often easy to accomplish it by simply issuing
some conventional commands to alter the filesystem.  For this reason, some
functionalities you might expect to exist, don't have specific `tagfarm` commands
implemented for them.

For example, to rename a tag, one needs only to rename the directory that contains
the tag links.  For example:

    mv by-tag/airplane by-tag/aeroplane

TODO
----

Better handling of cases where the target being linked is itself a link.

Set-theoretic queries on tags (e.g. tag all files with X or Y and not Z with a new tag T).
