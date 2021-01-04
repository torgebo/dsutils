#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""`catp` unwraps one or more pickle streams
("append files") into a collection object and
pickles that object to standard output.
"""
from io import (
    IOBase as _IOBase,
)
from os import (
    PathLike as _PathLike,
)
from typing import (
    Any,
    Generator,
    Iterable,
    List,
)

import logging as _logging
import pickle as _pickle


__version__ = "0.1.1"
_log = _logging.getLogger(__name__)


def pickle_iter_files(
        ref_files: Iterable[_PathLike]) -> Generator[Any, None, None]:
    for rfile in ref_files:
        yield from pickle_iter(rfile)


def _pickle_iter_buf(buf: _IOBase) -> List[Any]:
    while True:
        try:
            el = _pickle.load(buf)
        except EOFError:
            return
        else:
            yield el


def pickle_iter(ref_file: _PathLike) -> Generator[Any, None, None]:
    """Yield objects in pickle file."""
    _log.info("read from pickle file %s", ref_file)
    if isinstance(ref_file, _IOBase):
        yield from _pickle_iter_buf(ref_file)
    else:
        with open(ref_file, "rb") as f:
            yield from _pickle_iter_buf(f)


def catp(files: Iterable[_PathLike], out_stream) -> List[Any]:
    """For each pickle file in `files`, gather objects and
    write them as a single List to `out_stream`. Returns collection.
    """
    collection = []
    num = 0
    for item in pickle_iter_files(files):
        collection.append(item)
        num += 1
    _pickle.dump(collection, out_stream)
    _log.info("wrote a total of %s objects to %s", num, out_stream)
    return collection


if __name__ == "__main__":
    import argparse
    import sys
    _logging.basicConfig(level=_logging.INFO)
    parser = argparse.ArgumentParser(
        description=(
            """`catp` unwraps one or more pickle streams
            ("append files") into a collection object and
            pickles that object to standard output.
            """.lstrip().replace("\n", " ")
        ),
    )
    parser.add_argument('input_pickles', metavar='input-pickles', nargs='+',
                        help='one or more files containing pickled objects')
    args = parser.parse_args()
    catp(args.input_pickles, sys.stdout.buffer)
