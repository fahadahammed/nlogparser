# nLogParser
nLogParser is a tool which parse your nginx servers logs in a well sorted way.

## How to Use?

### Convert Log File
```bash
python3 nlogparser.py filename.log convert
```

### Read Log File
```bash
python3 nlogparser.py filename.log read --head 5
```

## Help
```bash
usage: nlogparser.py [-h] [-v] file {convert,reader} ...

nLogParser is a tool which parse your nginx servers logs in a well sorted way.

positional arguments:
  file               file with location
  {convert,reader}

optional arguments:
  -h, --help         show this help message and exit
  -v, -V, --version  show program's version number and exit

The version: 1 has some specific changes like ['Convert encoded log files to
decoded ones. Extract GZ files and decode. '].
```
