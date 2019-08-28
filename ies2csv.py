#!/usr/bin/env python
import argparse
import os
import glob
import struct
from pathlib import Path


usage = """
Usage: ies2csv.py ([-o <new-file>] <ies-file> | --batch [<path>])

Options:
    -o <new-file>, --output=<new-file>  Output to a new file.
    --batch                             Batch mode.
    <path>                              Path for batch mode. [default: ./]
"""

parser = argparse.ArgumentParser(
    description = 'An .ies file to tsv converter'
    )
subparser = parser.add_subparsers(
    help = 'subcommand help',
    required = True,
    dest = 'subcommand'
    )

parser_file = subparser.add_parser(
    'file',
    help = 'file help'
    )
parser_file.add_argument(
    '--output', '-o',
    required = False,
    type = Path
    )
parser_file.add_argument(
    'ies_file',
    help = 'The .ies file to convert',
    type = Path
    )

parser_batch = subparser.add_parser(
    'batch',
    help = 'batch help'
    )
parser_batch.add_argument(
    'directory',
    help = 'The directory with .ies files to batch convert',
    type = Path
    )

NULL_BYTE = '\x00'
SEPARATOR = '\t'
LINE = '\n'

def convert_bytestring(bstr: bytes):
    """Converts a bytestring to a readable string.

    Args:
        bstr (bytes): the bytestring to decode

    Returns:
        str: the appropriate string

    """
    return bytes(
        [(int(b) ^ 0x1) for b in bstr if int(b) != 0]
        ).decode(errors='ignore').rstrip(NULL_BYTE)


def get_int_from_bytes(bstr: bytes):
    """Get `int` from `bytes`. Obviously
    Uses little endian to convert.

    Args:
        bstr (bytes): the bytestring chunk to convert

    Returns:
        int: the number converted

    """
    return int.from_bytes(bstr, byteorder = 'little')


def get_col_names(
    file: Path, bstr: bytes, ncols: int, offset: int, colint: int
    ):
    """Gets column names from the bytestring of an `.ies` file.

    Args:
        file (Path): the file itself
        bstr (bytes): the bytestring
        ncols (int): number of columns
        offset (int): offset to start from the bytestring
        colint (int): offset to specific columns

    Returns:
        dict: with key = index and value = column name
    """
    col_names = {}
    for _ in range(ncols):
        col_name = convert_bytestring(bstr[offset:offset+64])
        # `n2` is unnecessary in this port.
        # Just add 128; 64 for 64 bytes + 64 for `n2`.
        offset += 128
        col_type = get_int_from_bytes(bstr[offset:offset+2])
        # `dummy` is unnecessary in this port.
        # Just add 6; 2 for short + 4 for `dummy`.
        offset += 6
        col_idx = get_int_from_bytes(bstr[offset:offset+2])
        offset += 2

        if col_type == 0:
            try:
                if col_names[col_idx]:
                    raise Exception(
                        f'IES file {file} is invalid: '
                        f'{col_names[col_idx]} is not null'
                        )
            except KeyError:
                col_names[col_idx] = col_name
        else:
            try:
                if col_names[col_idx + colint]:
                    raise Exception(
                        f'IES file {file} is invalid: '
                        f'{col_names[col_idx+colint]} is not null')
                    return False
            except KeyError:
                col_names[col_idx + colint] = col_name

    return col_names


def get_rows(
    file: Path, bstr: bytes, tsv: list, nrows: int, offset: int,
    colint: int, colstr: int
    ):
    """Gets rows from the bytestring of an `.ies` file.

    Args:
        file (Path): the file itself
        bstr (bytes): the bytestring
        tsv (list): the tsv in list form
        nrows (int): number of rows
        offset: offset to specify columns
        colint (int): offset to specific columns
        colstr (int): offset to specific columns

    Returns:
        list: `tsv` with rows populated

    """
    for i in range(nrows):
        rowid = get_int_from_bytes(bstr[offset:offset+4])
        offset += 4
        l = get_int_from_bytes(bstr[offset:offset+2])
        # `lookupkey` is unnecessary in this port.
        offset += 2 + l

        objs = {}

        for j in range(colint):
            # Equivalent to `br.ReadSingle`, line 103.
            objs[j] = struct.unpack('<f', bstr[offset:offset+4])[0]
            offset += 4

        for j in range(colstr):
            # Equivalent to `br.ReadUInt16`, line 110.
            col_len = struct.unpack('<H', bstr[offset:offset+2])[0]
            offset += 2
            objs[j+colint] = convert_bytestring(bstr[offset:offset+col_len])
            offset += col_len

        row = []
        for obj in objs.values():
            if not obj:
                raise Exception(
                    f'IES file {file} is invalid: obj is null'
                    )
            # Equivalent to *both* `csv.WriteField`, lines 120 & 122.
            row.append(str(obj))
        tsv.append(row)

        offset += colstr

    return tsv


def convert_file(file: Path, dest: Path = None):
    """Converts a `file` fully from bytes to string.
    Optionally outputs to new file `dest`, if not run in batch mode.
    (`dest` is not None.)

    Args:
        file (Path): the file to convert
        dest (Path, optional): the destination output; defaults to None

    Returns:
        bool: True if successful; False otherwise

    Raises:
        Exception: if the file was corrupt in any way

    """
    bstr = file.read_bytes()
    table_name = bstr[0:128].decode().rstrip(NULL_BYTE)
    # Equivalent to original `val1`, `offset1`, `offset2`, and `filesize`.
    # I interpreted it as `value`, but I am unsure.
    # Four value slicing equivalent to `ReadInt32`.
    value, offset1, offset2, file_size = [
        get_int_from_bytes(bstr[i:i+4])
        for i
        in (128, 132, 136, 140)
        ]

    if len(bstr) != file_size:
        raise Exception(
            f'IES file {file} has invalid length specified: {len(bstr)}'
            )
    if value != 1:
        raise Exception(
            f'IES file {file} has incorrect value: {value}'
            )

    # Equivalent to original `rows`, `cols`, `colint`, and `colstr`.
    # `short1` is unnecessary in this port.
    # Two value slicing equivalent to `ReadInt16`.
    nrows, ncols, colint, colstr = [
        get_int_from_bytes(bstr[i:i+2])
        for i
        in (146, 148, 150, 152)
        ]

    if ncols != colint + colstr:
        raise Exception(
            f'IES file {file} has mismatched cols: {ncols}!={colint}+{colstr}'
            )

    # Equivalent to `ms.Seek`.`
    offset_idx = file_size - offset1 - offset2

    col_names = get_col_names(file, bstr, ncols, offset_idx, colint)

    tsv = []

    row = []
    for i in range(ncols):
        if not col_names[i]:
            raise Exception(
                f'IES file {file} is invalid: '
                f'col_names at index {i} is null'
                )
        row.append(str(col_names[i]))
    tsv.append(row)

    offset_idx = file_size - offset2 # equivalent to `ms.Seek`, line 89

    tsv = get_rows(file, bstr, tsv, nrows, offset_idx, colint, colstr)

    out = Path(f'{file.stem}.tsv' if dest is None else dest)
    out.write_text(
        LINE.join(
            [SEPARATOR.join(line) for line in tsv]
            )
        )

    return True


def batch_convert_dir(directory: Path):
    """Traverses a `directory` with max-depth of 1 to convert all
    `.ies` files.

    Args:
        directory (Path): the directory itself (usually relative)

    Returns:
        None

    """
    for file in directory.glob('*.ies'):
        convert_file(file)

    return


if __name__ == "__main__":
    args = parser.parse_args()
    print(args)

    if args.subcommand == 'file':
        convert_file(args.ies_file, args.output)
    # try:
    #     if sys.argv[1] == '-o' or sys.argv[1] == '--output':
    #         outfile = sys.argv[2]
    #         files = sys.argv[3:]

    #     elif '--output=' in sys.argv[1]:
    #         outfile = sys.argv[1].split('=')[1]
    #         files = sys.argv[2:]

    #     elif sys.argv[1] == '--batch':
    #         if len(sys.argv) < 3:
    #             files = ['.']
    #         else:
    #             files = sys.argv[2:]

    #     else:
    #         raise IndexError

    # except IndexError:
    #     sys.exit(usage)

    # for f in files:
    #     if os.path.isfile(f) and f.endswith('.ies'):
    #         try:
    #             convert_file(f, outfile)
    #         except NameError:
    #             pass

    #     elif os.path.isdir(f):
    #         batch_convert_dir(f)

    #     else:
    #         print('File not recognized: ' + f)
    #         continue