# ies2csv

## Overview

`ies2csv` is a utility meant to convert the `.ies` files found within `.ipf` files used by [Tree of Savior][tos] to a readable tab-separated file. `csv` is a misnomer because I discovered some fields in the `.ies` actually have commas, affecting the output from the original `csv` format.

This `ies2csv` is a fork of the [original utility](https://github.com/Doddler/ies2csv), written in C# by [**Doddler**](https://github.com/Doddler). As practice for myself, I re-implemented the code in Python, specifically Python 3.5+.

## Usage

```
Usage: ies2csv.py ([-o <new-file>] <ies-file> | --batch [<path>])

Options:
    -o <new-file>, --output=<new-file>  Output to a new file.
    --batch                             Batch mode.
    <path>                              Path for batch mode. [default: ./]
```

Default behavior overwrites the supplied file. In batch mode, manual output is disabled.

## Requirements

This code is designed around the following:

- Python 3.5+

[tos]: https://treeofsavior.com/