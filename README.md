
# Simple HTML Report

This is a simple shell-friendly HTML report generator. It allows generating a simple (non-customizable) HTML report file with bash code.

State filename cannot start with `-` or `%`.

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

### `-tweak-json` flag

Can be applied if last component is `Code` with json text inside and the json top-level component is dict:
+ `w` filters dict in whitelist mode
+ `b` filters dict in blacklist mode

For example, this code imports sbom root component as a code and removes `bom-ref` field from it:
```shell
$ python3 ./main.py root_of_sbom.json \
  -codej sbom.json metadata component \
  -tweak-code spoiler "This is root of our SBoM" \
  -tweak-json b bom-ref 
```

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

### `-pure` flag

Suppresses state printing (for one-liners or destructive operations).

### `-terminateif` flag

Flushes rest of the command line unless arg1 not in:
+ `0`
+ `false` (any case)
+ `no` (any case)
+ Empty line

Without arguments: does nothing.

### `-terminateifeq` and `-terminateifeqnt` flag

Compare arg1 and arg2 and flush rest of the command line if they are equal (`-terminateifeq`) or not equal (`-terminateifeqnt`).


