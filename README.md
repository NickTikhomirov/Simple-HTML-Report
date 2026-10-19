
*Warning: user discretion is advised. This tool (as well as its source code) may be upsetting or disturbing.*

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

See at [FLAGS.md](FLAGS.md).
