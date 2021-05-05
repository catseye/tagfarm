# encoding: UTF-8

import errno
import os


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def find_media_root(path):
    while path != '/':
        if os.path.isdir(os.path.join(path, 'by-tag')):
            return path
        path = os.path.abspath(os.path.join(path, os.pardir))
    raise ValueError("could not locate `by-tag` directory in curent directory or any parent directory thereof")


def index_files(media_root):
    index = {}
    for root, dirs, files in os.walk(media_root):
        if os.path.normpath(root) == os.path.normpath(os.path.join(media_root, 'by-tag')):
            dirs[:] = []
            continue

        for basename in files:
            filename = os.path.normpath(os.path.join(root, basename))
            if os.path.islink(filename):
                continue

            index.setdefault(basename, set()).add(filename)
    return index


def is_broken_link(path):
    return os.path.lexists(path) and not os.path.exists(path)


def is_absolute_link(path):
    return os.path.lexists(path) and os.readlink(path).startswith('/')


def readlink_or_broken(path):
    return '*BROKEN*' if is_broken_link(path) else os.readlink(path)


def relativize_target(media_root, path):
    # Prepends `../..` because the link always resides in `by-tag/<tagname>`
    return os.path.join('..', '..', os.path.relpath(path, media_root))


def tag_file(media_root, filename, tag):
    mkdir_p(os.path.join(media_root, 'by-tag', tag))
    linkname = os.path.join(media_root, 'by-tag', tag, os.path.basename(filename))
    if not os.path.lexists(linkname):
        srcname = relativize_target(media_root, filename)
        os.symlink(srcname, linkname)


def perform_repair(media_root, verbose=False, force_relink=False, restrict_to_tag=None, prune=False):
    index = index_files(media_root)

    by_tags_dir = os.path.join(media_root, 'by-tag')
    tags = [restrict_to_tag] if restrict_to_tag else sorted(os.listdir(by_tags_dir))
    for tag in tags:
        tagdir = os.path.join(by_tags_dir, tag)
        if not os.path.isdir(tagdir):
            continue
        repairs_made = []
        for basename in sorted(os.listdir(tagdir)):
            linkname = os.path.join(tagdir, basename)

            if basename.startswith('Link to '):
                new_basename = basename[8:]
                new_linkname = os.path.join(tagdir, new_basename)
                if os.path.lexists(new_linkname):
                    repairs_made.append(
                        "WARNING: not renaming '{}' (-> '{}') because '{}' (-> '{}') already exists".format(
                            linkname, readlink_or_broken(linkname), new_linkname, readlink_or_broken(new_linkname)
                        )
                    )
                else:
                    repairs_made.append("RENAMING {} -> {}".format(linkname, new_linkname))
                    os.rename(linkname, new_linkname)
                    linkname = new_linkname

            if not force_relink:
                if not os.path.islink(linkname):
                    repairs_made.append("WARNING: skipping {} (is regular file, but --force-relink not given)".format(linkname))
                    continue
                if not (is_broken_link(linkname) or is_absolute_link(linkname)):
                    if verbose:
                        repairs_made.append('kept {} -> {}'.format(linkname, os.readlink(linkname)))
                    continue

            candidates = index.get(basename, set())
            if len(candidates) == 0:
                if prune:
                    repairs_made.append("NOTICE: no candidates for {}, DELETING".format(basename))
                    os.remove(linkname)
                else:
                    repairs_made.append("WARNING: no candidates for {}".format(basename))
            elif len(candidates) > 1:
                repairs_made.append("WARNING: multiple candidates for {}:  {}".format(basename, candidates))
            else:
                os.remove(linkname)
                filename = list(candidates)[0]
                srcname = relativize_target(media_root, filename)
                os.symlink(srcname, linkname)
                repairs_made.append('FIXED {} -> {}'.format(linkname, srcname))

        if repairs_made:
            print('*** {}'.format(tag))
            for repair_made in repairs_made:
                print(repair_made)
