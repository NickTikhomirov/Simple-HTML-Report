
# Simple HTML Report

This is a simple shell-friendly HTML report generator. It allows generating a simple (non-customizable) HTML report file with bash code.

## Example

```shell
$ ./main.py ./example.json -header1 'This is header' -par 'This is some text'
$ ./main.py ./example.json -row 'Cell1' 'Cell2' 'Cell3'
$ ./main.py ./example.json -row 'CellA' 'CellB' 'CellC' -row 'CellX' 'CellY' 'CellZ'
$ ./main.py ./example.json -tweak-table enum -prefix% %header2 'This is header level 2' %par 'This is some text'
$ ./main.py ./example.json -css ./example.css -render example.html
```

### With environment variables

Filename of report state can be stored to `SIMPLEHTML_STATE` env variable for brevity

```shell
$ export SIMPLEHTML_STATE=./example.json
$ ./main.py -header1 'This is header' -par 'This is some text'
$ ./main.py -row 'Cell1' 'Cell2' 'Cell3'
$ ./main.py -row 'CellA' 'CellB' 'CellC' -row 'CellX' 'CellY' 'CellZ'
$ ./main.py -tweak-table enum -prefix% %header2 'This is header level 2' %par 'This is some text'
$ ./main.py -css ./example.css -render example.html
```

## Supported flags

### `-headerI` flag

Appends a new header with respective level:

Signature:
+ suffix: level (=1 if omitted)
+ arg1: header name
+ arg2+: dropped


### `-par` flag

Simple text paragraph.

Signature:
+ suffix: ignored
+ arg1: text
+ arg2+: dropped

### `-row` flag

### `-tweak-table` flag

Applies modifications to table according to command (first arg):
+ `enum` -- adds leftmost column with numeration (N, 1, 2, 3...)
+ `spoiler` -- hides table to spoiler (second arg is used for spoiler's name, if present)

### `-tweak-code` flag
+ `spoiler` -- hides code to spoiler (second arg is used for spoiler's name, if present)

### `-includeI` flag

Extends current state with contents of some other simple html report state.
Also, can reduce headers' levels -- f.e. `-include1 doc.json` includes `doc.json` while deepening its headers by 1.

Signature:
+ suffix: delta to add (=1 if omitted)
+ arg1: file name
+ arg2+: dropped

### `-css` flag

Adds an external CSS file to your HTML report.

Signature:
+ suffix: dropped
+ arg1: css file to use
+ arg2+: dropped

### `-prefix` flag

Sets a new prefix for flags instead of `-`, f.e.:

```shell
python.exe .\main.py report.html -prefix+ +css .\example.css +header1 "This is header with lvl=1"
```

Signature:
+ suffix: a new prefix
+ arg1: if equals to `fixed`, the prefix is stored to report state (json file) and re-applied in further invocations
+ arg2+: dropped

