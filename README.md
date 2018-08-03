# ies2csv
#### _A [Tree of Savior][tos] utility._

### Originally authored by **Doddler** on Github here: https://github.com/Doddler/ies2csv

## Overview

*ies2csv* is a utility meant to convert the `.ies` files found within `.ipf` for Tree of Savior. The original utility was written in *C#* while this implementation written from scratch is written in *Python* for more universal environment.

```
Usage: ies2csv.py ([-o <new-file>] <ies-file> | --batch [<path>])

Options:
    -o <new-file>, --output=<new-file>  Output to a new file.
    --batch                             Batch mode.
    <path>                              Path for batch mode. [default: ./]
```

Default behavior overwrites the supplied file. In batch mode, manual output is disabled.

#### File last modified: 2018-08-03 16:08 (UTC-7)

[tos]: https://treeofsavior.com/