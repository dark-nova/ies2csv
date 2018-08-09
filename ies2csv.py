#!/usr/bin/env python
import sys, os, glob
from pathlib import Path

usage = """
Usage: ies2csv.py ([-o <new-file>] <ies-file> | --batch [<path>])

Options:
    -o <new-file>, --output=<new-file>  Output to a new file.
    --batch                             Batch mode.
    <path>                              Path for batch mode. [default: ./]
"""


# from original code; may not be necessary
def get_string(a_str, len: int):
    pass


def convert_file(file, dest=None):
    """
    :func:`convert_files` converts a file fully from byte to string.
    Optionally outputs to new file, if not run in batch mode (dest is not None).

    Args:
        file (str): the file name
        dest (str): the destination file name (default: None)

    Returns:
        True
    """
    
    p = Path(file)

    out = Path(file if dest is None else dest)
    #out.write_text(txt)

    return True


def handle_dir(d):
    """
    :func:`handle_dir` changes into a directory to traverse and batch-edit .ies files.
    Once complete, the function changes back to the original directory.

    Args:
        d (str): the string representing the directory's name (usually relative)

    Returns:
        True
    """
    cdir = os.getcwd()
    os.chdir(d)
    for file in glob.glob('*.ies'):
        convert_file(file)
    os.chdir(cdir)
    return True


if __name__ == "__main__":
    try:
        if sys.argv[1] == '-o' or sys.argv[1] == '--output':
            outfile = sys.argv[2]
            files = sys.argv[3:]
            
        elif '--output=' in sys.argv[1]:
            outfile = sys.argv[1].split('=')[1]
            files = sys.argv[2:]

        elif sys.argv[1] == '--batch':
            if len(sys.argv) < 3:
                files = ['.']
            else:
                files = sys.argv[2:]

        else:
            raise IndexError

    except IndexError:
        sys.exit(usage)

    for f in files:
        if os.path.isfile(f) and f.endswith('.ies'):
            try:
                pass
            except NameError:
                pass

        elif os.path.isdir(f):
            handle_dir(f)

        else:
            continue