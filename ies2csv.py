#!/usr/bin/env python
import sys, os, glob, struct
from pathlib import Path

usage = """
Usage: ies2csv.py ([-o <new-file>] <ies-file> | --batch [<path>])

Options:
    -o <new-file>, --output=<new-file>  Output to a new file.
    --batch                             Batch mode.
    <path>                              Path for batch mode. [default: ./]
"""

NULL_BYTE = '\x00'
SEPARATOR = '\t'
LINE = '\n'

def convert_file(file, dest=None):
    """
    :func:`convert_files` converts a file fully from byte to string.
    Optionally outputs to new file, if not run in batch mode (dest is not None).

    Args:
        file (str): the file name
        dest (str): the destination file name (default: None)

    Returns:
        True if successful; False otherwise
    """
    p = Path(file)

    bstr = p.read_bytes()
    table_name = bstr[0:128].decode().rstrip(NULL_BYTE)
    valid = int.from_bytes(bstr[128:132], byteorder='little') # equivalent to original `val1`
    offset1 = int.from_bytes(bstr[132:136], byteorder='little')
    offset2 = int.from_bytes(bstr[136:140], byteorder='little')
    filesize = int.from_bytes(bstr[140:144], byteorder='little')

    if len(bstr) != filesize:
        print('IES file has invalid length specified:', file)
        return False
    elif valid != 1:
        print('IES file has incorrect value:', file)

    # `short1` is unnecessary in this port
    rows = int.from_bytes(bstr[146:148], byteorder='little')
    cols = int.from_bytes(bstr[148:150], byteorder='little')
    colint = int.from_bytes(bstr[150:152], byteorder='little')
    colstr = int.from_bytes(bstr[140:144], byteorder='little')

    if cols != colint + colstr:
        print('IES file has mismatched cols:', file)
        return False

    offset_idx = filesize - offset1 - offset2 # equivalent to `ms.Seek`, line 50

    colnames = {}

    for i in range(cols):
        new_offset = offset_idx
        n1 = bstr[new_offset:new_offset+64]
        new_offset += 64
        n2 = bstr[new_offset:new_offset+64]
        new_offset += 64
        typ = bstr[new_offset:new_offset+2]
        new_offset += 6 # 2 for short + 4 for `dummy`
        # `dummy` is unnecessary in this port
        pos = bstr[new_offset:new_offset+2]
        new_offset += 2

        if typ == 0:
            try:
                if colnames[pos] is not None:
                    print('IES file is wrong:', file, ', value: colnames[pos]')
                    return False
            except KeyError:
                pass
            colnames[pos] = n1
        else:
            try:
                if colnames[pos + colint] is not None:
                    print('IES file is wrong:', file, ', value: colnames[pos+colint]')
                    return False
            except KeyError:
                pass
            colnames[pos + colint] = n1
        
    csv = [] # equivalent to `csv`
    csv[0] = []

    for i in range(cols):
        if cols[i] is None:
            print('IES file is wrong: ', file, ', value: cols[i]')
            return False
        csv[0].append(str(cols[i]))

    offset_idx = filesize - offset2 # equivalent to `ms.Seek`, line 89

    for i in range(rows):
        new_offset = offset_idx
        rowid = int.from_bytes(bstr[new_offset:new_offset+4], byteorder='little')
        new_offset += 4
        l = int.from_bytes(bstr[new_offset:new_offset+2], byteorder='little')
        new_offset += 2
        lookupkey = bstr[new_offset:new_offset+l].decode().rstrip(NULL_BYTE) # equivalent to `GetString`
        new_offset += l

        objs = {}

        for j in range(colint):
            objs[j] = struct.unpack('<f', bstr[new_offset:new_offset+4])[0] # equivalent to `br.ReadSingle`, line 103
            new_offset += 4

        for j in range(colstr):
            _l = struct.unpack('<H', bstr[new_offset:new_offset+2])[0] # equivalent to `br.ReadUInt16`, line 110
            new_offset += 2
            objs[j+colint] = bstr[new_offset:new_offset+l].decode().rstrip(NULL_BYTE) # equivalent to `GetString`
            new_offset += l

        for obj in objs.values():
            if obj is None:
                print('IES file is wrong: ', file, ', value: obj')
                return False
            csv[i+1].append(str(obj)) # equivalent to *both* `csv.WriteField`, lines 120 & 122

    for c in csv:
        SEPARATOR.join(c)

    txt = LINE.join([SEPARATOR.join(line for line in csv)])

    out = Path(file if dest is None else dest)
    out.write_text(txt)

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
            print('File not recognized: ' + f)
            continue