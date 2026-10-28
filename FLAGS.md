# Flags for Simple HTML Report 

## Common writing

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


## Code

### `-code` flag


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



## Tables

### `-row` flag


### `-csv` flag

*Do not mistake with `css` flag*

Includes CSV file as a normal table (which can be tweaked with `-tweak-table` or extended with `-row`).

Signature:
+ suffix:
  + `e` (excel mode) -- file is opened with cp1251 encoding and delimeter is `;`
  + `a` (append) -- if there is a table already, appends csv to it (otherwise: csv is included as a new table);
+ args: subset of column numbers (f.e. `-csv mytable.csv 1 3 4` includes only some columns from the file);


### `-tweak-table` flag

Applies modifications to table according to command (first arg):
+ `enum` -- adds leftmost column with numeration (N, 1, 2, 3...)
+ `spoiler` -- hides table to spoiler (second arg is used for spoiler's name, if present)



## Printing an HTML file

### `-css` flag

Adds an external CSS file to your HTML report.

Signature:
+ suffix: dropped
+ arg1: css file to use
+ arg2+: dropped

### `-render` flag (also known as `-print` and `-release`)

Prints state to HTML file.

Signature:
+ suffix: dropped
+ arg1: (optional) filename -- if not present, `-render` will use name from `-givename` flag
+ arg2+: dropped

### `-givename` flag

Gives a new name to the file to show in menu. Makes sense with `-connect`, but useless otherwise.
+ suffix: dropped
+ arg1: menu name
+ arg2: file name (affects `-render` and used in menu)
+ arg3+: dropped

### `-connect` flag

Connects multiple reports with menu. One must set their page names and file names with `-givename` beforehand.

```
! Affects multiple reports passed by name to the script with the flag.
```

Current state is always a top-most report and others reside below (so use `-connect` on title page).

+ suffix:
  + `a` -- TODO
  + `c` -- shares css of the state with all other reports
  + `1` -- disable effects to other reports (only current file gets a menu)
  + `o` -- overwrites menus of other states if present (`-connect` does nothing with such states without `-o`)
+ args: other reports to connect (will be changed)

### `-disconnect` flag

Resets menu (undoes `-connect` flag). Affects only one report, not all.

Has no args nor suffixes.

## State management flags

### `-include` flag

Extends current state with contents of some other simple html report state.
Also, can reduce headers' levels -- f.e. `-include1 doc.json` includes `doc.json` while deepening its headers by 1.

Signature:
+ suffix: delta to add (=1 if omitted)
+ arg1: file name
+ arg2+: dropped

### `-pure` flag

Suppresses state printing (for one-liners or destructive operations).

## Metaflags: syntax

### `-prefix` flag

Sets a new prefix for flags instead of `-`, f.e.:

```shell
python.exe .\main.py report.html -prefix+ +css .\example.css +header1 "This is header with lvl=1"
```

Signature:
+ suffix: a new prefix
+ arg1: if equals to `fixed`, the prefix is stored to report state (json file) and re-applied in further invocations
+ arg2+: dropped

Why? Because sometimes table cells need to contain minuses.

## Metaflags: control flow

### `-terminateif` flag

Flushes rest of the command line unless arg1 not in:
+ `0`
+ `false` (any case)
+ `no` (any case)
+ Empty line

Without arguments: does nothing.

### `-terminateifeq` and `-terminateifeqnt` flag

Compare arg1 and arg2 and flush rest of the command line if they are equal (`-terminateifeq`) or not equal (`-terminateifeqnt`).


### `-remember` flag plus `-terminateifmemeq` and `-terminateifmemeqnt` flags

`-remember` stores arg1 to report state and others operate on it in the same fashion as `-terminateifeq` and `-terminateifeqnt` flags comparing stored value with their arg1.

### `-echo` flag

Echoes its args. Useless, but good for debugging terminations.
