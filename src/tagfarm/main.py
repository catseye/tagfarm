# encoding: UTF-8

from argparse import ArgumentParser
import os
import sys

from tagfarm.utils import (
    mkdir_p, find_media_root, tag_file, perform_repair
)


def tag(media_root, args, verbose=False):
    argparser = ArgumentParser()
    argparser.add_argument('tag', metavar='TAG', type=str,
        help='Name of tag to apply'
    )
    argparser.add_argument('filenames', metavar='FILENAME', type=str, nargs='+',
        help='Names of files to tag'
    )
    options = argparser.parse_args(args)

    for filename in options.filenames:
        tag_file(media_root, filename, options.tag)


def untag(media_root, args, verbose=False):
    argparser = ArgumentParser()
    argparser.add_argument('tag', metavar='TAG', type=str,
        help='Name of tag to remove'
    )
    argparser.add_argument('filenames', metavar='FILENAME', type=str, nargs='+',
        help='Names of files to untag'
    )
    options = argparser.parse_args(args)

    for filename in options.filenames:
        linkname = os.path.join(media_root, 'by-tag', options.tag, os.path.basename(filename))
        if os.path.lexists(linkname):
            os.remove(linkname)


def showtags(media_root, args, verbose=False):
    argparser = ArgumentParser()
    argparser.add_argument('filenames', metavar='FILENAME', type=str, nargs='+',
        help='Names of files to show tags of',
    )
    argparser.add_argument('--show-only-fewer-than', type=int, default=None,
        help='If given, report only those files that have fewer than this number of tags',
    )
    options = argparser.parse_args(args)

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


def repair(media_root, args, verbose=False):
    argparser = ArgumentParser()
    argparser.add_argument('--force-relink', action='store_true',
        help='Replace files found in taglinks directory even when they are not symlinks or not broken'
    )
    argparser.add_argument('--prune', action='store_true',
        help='Remove broken symlinks for which no candidate files can be found'
    )
    options = argparser.parse_args(args)

    perform_repair(media_root, verbose=verbose, force_relink=options.force_relink, prune=options.prune)


def rename(media_root, args, verbose=False):
    argparser = ArgumentParser()
    argparser.add_argument('src', metavar='FILENAME', type=str,
        help='Current name of file that is to be renamed'
    )
    argparser.add_argument('dest', metavar='FILENAME', type=str,
        help='New name of file'
    )
    options = argparser.parse_args(args)

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


def collect(media_root, args, verbose=False):
    argparser = ArgumentParser()
    argparser.add_argument('tag', metavar='TAG', type=str,
        help='Tag to select files by'
    )
    argparser.add_argument('dest', metavar='DIRNAME', type=str,
        help='Directory to move files into'
    )
    options = argparser.parse_args(args)

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


COMMANDS = {
    'tag': tag,
    'untag': untag,
    'showtags': showtags,
    'repair': repair,
    'rename': rename,
    'collect': collect,
}

# - - - - driver - - - -


def main(args):
    argparser = ArgumentParser()

    argparser.add_argument('command', metavar='COMMAND', type=str,
        help='The action to take. One of: {}'.format(', '.join(COMMANDS.keys()))
    )
    argparser.add_argument('--verbose', action='store_true',
        help='Produce more reporting output'
    )

    options, remaining_args = argparser.parse_known_args(args)

    media_root = find_media_root(os.path.realpath('.'))

    command = COMMANDS.get(options.command, None)
    if command:
        command(media_root, remaining_args, verbose=options.verbose)
    else:
        argparser.print_help()
        sys.exit(1)
