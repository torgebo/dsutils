#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""`grep.py` searches text streams using Python expressions.
"""
import logging as _logging
import os as _os
import re as _re
from fileinput import FileInput as _FileInput
from pathlib import Path as _Path
from pathlib import PosixPath as _PosixPath
from typing import Any, Callable, Generator, List, Union

__author__ = 'Torgeir Børresen'
_log = _logging.getLogger(__name__)


def load_expression(expr: str) -> Callable[[str], Any]:
    """Load search expression.

    Notes
    -----
    - Consider changing returncode Callable[[], Any]
    """
    loc = {"re": _re}
    eval_exp = eval(expr, loc, {})

    # Got function
    if callable(eval_exp):
        return eval_exp

    # Got regular expression
    regexp = _re.compile(expr)
    return lambda s: regexp.match(s)


def _generate_inputs(inputs: List[str], recursive: bool) -> Generator[
        Union[_Path, FileNotFoundError], None, None]:
    """Generate Path object for each member of `inputs`.

    If the object does not exists returns 
    """
    for input_exp in inputs:
        path = _Path(input_exp)
        if recursive and path.is_dir():
            for root, __, files in _os.walk(path):
                for fn in files:
                    yield _Path(root) / fn
        elif path.is_file():
            yield path
        else:
            return FileNotFoundError()
            


def pgrep(inputs: List[str], expr: str, recursive: bool):
    _out_fmt = '{fname:s}:{lineno:d}{line:s}'
    func = load_expression(expr)
    gen_inputs = _generate_inputs(inputs, recursive)
    finputs = _FileInput(files=gen_inputs)
    for line in finputs:
        if func(line):
            fname = finputs.filename()
            name: str
            if isinstance(fname, _PosixPath):
                name = str(fname.name)
            else:
                name = fname
            outs = _out_fmt.format(
                fname=name,
                lineno=finputs.filelineno(),
                line=line,
            )
            print(outs, end="")


if __name__ == "__main__":
    import argparse
    _logging.basicConfig(level=_logging.INFO)
    parser = argparse.ArgumentParser(
        description=__doc__,
    )
    parser.add_argument(
        'expression',
        help='Python search expression',
    )
    parser.add_argument(
        '--recursive',
        action='store_true',
        help='search files recursively',
    )
    parser.add_argument(
        'input_files',
        metavar='input-files',
        nargs='+',
        help='list of input files to be searched',
    )
    args = parser.parse_args()
    pgrep(args.input_files, args.expression, args.recursive)
