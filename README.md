# ies2csv

## Overview

`ies2csv` is a utility meant to convert the `.ies` files found within `.ipf` files used by [Tree of Savior][tos] to a readable tab-separated file. `csv` is a misnomer because I discovered some fields in the `.ies` actually have commas, affecting the output from the original `csv` format.

This `ies2csv` is a fork of the [original utility](https://github.com/Doddler/ies2csv), written in C# by [**Doddler**](https://github.com/Doddler). As practice for myself, I re-implemented the code in Python, specifically Python 3.5+.

Each resulting `.tsv` file has a structure like so:
- `ncols_int`: number of numeric/integer fields, like `ClassID` (ID) and `NeedCount` (flag)
- `ncols_str`: the rest of the fields, usually strings
- `ncols = ncols_int + ncols_str`

## Usage

### Main
```
$ python ies2csv.py -h
usage: ies2csv.py [-h] {file,batch} ...

An .ies file to tsv converter

positional arguments:
  {file,batch}  subcommand help
    file        file help
    batch       batch help

optional arguments:
  -h, --help    show this help message and exit
```

### File-based operations
```
usage: ies2csv.py file [-h] [--output OUTPUT] ies_file

positional arguments:
  ies_file              The .ies file to convert

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
```

⚠ Default behavior creates a `.tsv` file with the same 'stem' name.

### Batch operations
```
$ python ies2csv.py batch -h
usage: ies2csv.py batch [-h] directory

positional arguments:
  directory   The directory with .ies files to batch convert

optional arguments:
  -h, --help  show this help message and exit
```

⚠ In batch mode, manual output is disabled.

## Requirements

This code is designed around the following:

- Python 3.5+

## Disclaimer

This project is not affiliated with or endorsed by [Tree of Savior][tos]. See [`LICENSE`](LICENSE) for more detail.

[tos]: https://treeofsavior.com/
