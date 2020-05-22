# encoding: UTF-8

from argparse import ArgumentParser
import os
import sys

from tagfarm.utils import (
    mkdir_p, find_media_root, tag_file, perform_repair
)


def tag(media_root, options):
    for filename in options.filenames:
        tag_file(media_root, filename, options.tag)


def untag(media_root, options):
    for filename in options.filenames:
        linkname = os.path.join(media_root, 'by-tag', options.tag, os.path.basename(filename))
        if os.path.lexists(linkname):
            os.remove(linkname)


def showtags(media_root, options):
    by_tags_dir = os.path.join(media_root, 'by-tag')
    for filename in options.filenames:
        tags = []
        basename = os.path.basename(os.path.normpath(filename))
        for tag in sorted(os.listdir(by_tags_dir)):
            linkname = os.path.join(by_tags_dir, tag, basename)
            if os.path.lexists(linkname):
                tags.append(tag)
        if options.show_only_fewer_than is None or len(tags) < options.show_only_fewer_than:
            print('{}: {}'.format(filename, ', '.join(tags)))


def repair(media_root, options):
    perform_repair(media_root, verbose=options.verbose, force_relink=options.force_relink, prune=options.prune)


def rename(media_root, options):
    src = os.path.normpath(options.src)
    dest = os.path.normpath(options.dest)

    os.rename(src, dest)

    src_basename = os.path.basename(src)
    dest_basename = os.path.basename(dest)

    by_tags_dir = os.path.join(media_root, 'by-tag')
    for tag in os.listdir(by_tags_dir):
        old_linkname = os.path.join(by_tags_dir, tag, src_basename)
        if os.path.lexists(old_linkname):
            os.remove(old_linkname)
            target = os.path.join('..', '..', os.path.relpath(dest, media_root))
            new_linkname = os.path.join(by_tags_dir, tag, dest_basename)
            os.symlink(target, new_linkname)
            print('UPDATED {} -> {}'.format(new_linkname, target))


def collect(media_root, options):
    tagdir = os.path.join(media_root, 'by-tag', options.tag)
    if not os.path.isdir(tagdir):
        print("WARNING: no files tagged '{}'".format(options.tag))
        return

    dest = os.path.normpath(options.dest)
    mkdir_p(dest)

    for basename in os.listdir(tagdir):
        linkname = os.path.join(tagdir, basename)

        filename = os.path.join(tagdir, os.readlink(linkname))
        new_filename = os.path.join(dest, basename)

        if verbose:
            print(filename, new_filename)

        if not os.path.exists(new_filename):
            os.rename(filename, new_filename)
        else:
            print("WARNING: {} already exists, not moving".format(new_filename))

    perform_repair(media_root, verbose=verbose)


# - - - - driver - - - -


def main(args):
    parser = ArgumentParser()

    parser.add_argument('--verbose', action='store_true',
        help='Produce more reporting output'
    )

    subparsers = parser.add_subparsers()

    # - - - - tag - - - -
    parser_tag = subparsers.add_parser('tag', help='Add a given tag to one or more files')
    parser_tag.add_argument('tag', metavar='TAG', type=str,
        help='Name of tag to apply'
    )
    parser_tag.add_argument('filenames', metavar='FILENAME', type=str, nargs='+',
        help='Names of files to tag'
    )
    parser_tag.set_defaults(func=tag)

    # - - - - untag - - - -
    parser_untag = subparsers.add_parser('untag', help='Remove a given tag from one or more files')
    parser_untag.add_argument('tag', metavar='TAG', type=str,
        help='Name of tag to remove'
    )
    parser_untag.add_argument('filenames', metavar='FILENAME', type=str, nargs='+',
        help='Names of files to untag'
    )
    parser_untag.set_defaults(func=untag)

    # - - - - showtags - - - -
    parser_showtags = subparsers.add_parser('showtags', help='Report the tags currently on one or more files')
    parser_showtags.add_argument('filenames', metavar='FILENAME', type=str, nargs='+',
        help='Names of files to show tags of',
    )
    parser_showtags.add_argument('--show-only-fewer-than', type=int, default=None,
        help='If given, report only those files that have fewer than this number of tags',
    )
    parser_showtags.set_defaults(func=showtags)

    # - - - - repair - - - -
    parser_repair = subparsers.add_parser('repair', help='Re-assign broken tag links to relocated files')
    parser_repair.add_argument('--force-relink', action='store_true',
        help='Replace files found in taglinks directory even when they are not symlinks or not broken'
    )
    parser_repair.add_argument('--prune', action='store_true',
        help='Remove broken symlinks for which no candidate files can be found'
    )
    parser_repair.set_defaults(func=repair)

    # - - - - rename - - - -
    parser_rename = subparsers.add_parser('rename', help='Rename file whille updating all its tag links')
    parser_rename.add_argument('src', metavar='FILENAME', type=str,
        help='Current name of file that is to be renamed'
    )
    parser_rename.add_argument('dest', metavar='FILENAME', type=str,
        help='New name of file'
    )
    parser_rename.set_defaults(func=rename)

    # - - - - collect - - - -
    parser_collect = subparsers.add_parser('collect', help='Move all files with a given tag into a given directory')
    parser_collect.add_argument('tag', metavar='TAG', type=str,
        help='Tag to select files by'
    )
    parser_collect.add_argument('dest', metavar='DIRNAME', type=str,
        help='Directory to move files into'
    )
    parser_collect.set_defaults(func=collect)

    options = parser.parse_args(args)
    media_root = find_media_root(os.path.realpath('.'))
    options.func(media_root, options)
