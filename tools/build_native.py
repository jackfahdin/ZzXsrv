"""Small byte-stream filters used by the native Windows build recipes."""

import argparse
import gzip
import re
import shutil
import sys


def gzip_stream(source, destination):
    """Write gzip -9 data without a timestamp or source filename."""
    with gzip.GzipFile(
        filename="", mode="wb", compresslevel=9, fileobj=destination, mtime=0
    ) as compressed:
        shutil.copyfileobj(source, compressed)


def locale_aliases(source, destination):
    """Apply libX11/nls/makefile's two sed rules, retaining byte line endings."""
    remove_colon = re.compile(br"^[^#][^\t ]*:")
    delete_line = re.compile(br"^[^#].*[\t ].*:")
    for line in source:
        if remove_colon.search(line):
            line = line.replace(b":", b"", 1)
        if not delete_line.search(line):
            destination.write(line)


def cut_out(source, destination):
    """Apply fontconfig's awk filter; retain CRLF and terminate a final record."""
    no_write = False
    for line in source:
        if b"CUT_OUT_BEGIN" in line:
            no_write = True
            continue
        if b"CUT_OUT_END" in line:
            no_write = False
            continue
        if not no_write:
            destination.write(line)
            if not line.endswith(b"\n"):
                destination.write(b"\n")


def main():
    commands = {
        "gzip": gzip_stream,
        "locale-aliases": locale_aliases,
        "cut-out": cut_out,
    }
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=commands)
    arguments = parser.parse_args()
    # Buffer access avoids text encoding, newline translation and Ctrl-Z EOF.
    commands[arguments.command](sys.stdin.buffer, sys.stdout.buffer)


if __name__ == "__main__":
    main()
