#!/usr/bin/env python3

from dataclasses import dataclass, field
import sys
import os
from enum import Enum
import json
import html
import csv
from pathlib import Path

ENVIRONMENT_NAME_STATE_FILE = 'SIMPLEHTML_STATE'


class ReportElementType(Enum):
    REPORT = 'report'
    TABLE = 'table'
    CELL = 'cell'
    PARAGRAPH = 'paragraph'
    HEADER = 'header'
    CODE = 'code'
    MENU_ENTRY = 'menu_entry'

    @property
    def Type(self):
        return {
            ReportElementType.REPORT: Report,
            ReportElementType.HEADER: Header,
            ReportElementType.CELL: Cell,
            ReportElementType.PARAGRAPH: Paragraph,
            ReportElementType.TABLE: Table,
            ReportElementType.CODE: Code,
            ReportElementType.MENU_ENTRY: MenuEntry
        }[self]


def format_params(params: dict):
    """ format params for HTML tag """
    return ' '.join(f'{key}="{value}"' for key,value in params.items())


def tag(tagname: str, text: str, newlines: bool = False, params: dict = None):
    """ HTML tag """
    sep = '\n' if newlines else ''
    if params is None:
        return f'<{tagname}>{sep}{text}{sep}</{tagname}>'
    return f'<{tagname} {format_params(params)}>{sep}{text}{sep}</{tagname}>'


def select(list_: list, indexes: list[int]):
    """Takes a subset of list indexes"""
    return [v for i, v in enumerate(list_) if i in indexes]


def tag_open(tagname: str):
    return f'<{tagname}>'


def tag_close(tagname: str):
    return f'</{tagname}>'


def wander_json_file(filename: str, keys: list[str]):
    """ turns (file, ["metadata", "component", "name"]) into a object available under given path """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            j = json.load(f)
            for key in keys:
                j = j[key]
            is_simple_type = lambda x: type(x) in [bool, int, float, str]
            if is_simple_type(j):
                return str(j)
            if type(j) == list and all(is_simple_type(i) for i in j):
                return str(j)
            return json.dumps(j, ensure_ascii=False, indent=4)
    except (FileNotFoundError, KeyError, IndexError, TypeError, json.JSONDecodeError):
        pass
    return ''


@dataclass
class MenuEntry:
    name: str
    filename: str

    def __str__(self):
        visible_name = self.name or self.filename
        return f'<a href={self.filename}>{visible_name}</a>'

    def to_dict(self):
        return {
            "name": self.name,
            "filename": self.filename,
            "type": ReportElementType.MENU_ENTRY.value
        }

    @staticmethod
    def FromDict(j: dict):
        return MenuEntry(
            name=j.get('name') or '',
            filename=j['filename'],
        )

    @staticmethod
    def CleanName(name: str):
        name = name.split('/')[-1]
        name.strip('.')
        return name

    @staticmethod
    def SetMenuEntriesToFile(fname: str, entries, css: str = ''):
        entries: list[MenuEntry]
        with open(fname, 'r', encoding='utf-8') as f:
            j = json.load(f)
        j['menu_entries'] = list(map(MenuEntry.to_dict, entries))
        if css:
            j['css'] = css
        with open(fname, 'w', encoding='utf-8') as f:
            json.dump(j,f)

    @staticmethod
    def GetNamesFromFile(fname: str):
        with open(fname, 'r', encoding='utf-8') as f:
            j = json.load(f)
            return j.get('page_name'), j.get('file_name'), len(j.get('menu_entries') or [])


@dataclass
class Paragraph:
    text: str
    is_bold: str = False

    def __str__(self):
        return tag('p', html.escape(self.text))

    def to_dict(self):
        return {
            "text": self.text,
            "is_bold": self.is_bold,
            "type": ReportElementType.PARAGRAPH.value
        }

    @staticmethod
    def FromDict(j: dict):
        return Paragraph(
            is_bold=j.get('is_bold') or False,
            text=j['text'],
        )


@dataclass
class Code:
    text: str
    is_spoiler: bool = False
    spoiler_name: str = ''

    def __str__(self):
        result = tag('pre', tag('code', html.escape(self.text)))
        if self.is_spoiler:
            if self.spoiler_name:
                result = tag('summary', self.spoiler_name) + '\n' + result
            result = tag('details', result)
        return result

    def to_dict(self):
        return {
            "text": self.text,
            "is_spoiler": self.is_spoiler,
            "spoiler_name": self.spoiler_name,
            "type": ReportElementType.CODE.value
        }

    @staticmethod
    def FromDict(j: dict):
        return Code(
            text=j['text'],
            is_spoiler=j.get('is_spoiler') or False,
            spoiler_name=j.get('spoiler_name') or '',
        )


@dataclass
class Header(Paragraph):
    level: int = 1

    def __str__(self):
        return tag(f'h{self.level}', html.escape(self.text))

    def to_dict(self):
        return {
            "text": self.text,
            "is_bold": self.is_bold,
            "level": self.level,
            "type": ReportElementType.HEADER.value
        }

    @staticmethod
    def FromDict(j: dict):
        return Header(
            level=j['level'],
            is_bold=j.get('is_bold') or False,
            text=j['text'],
        )


@dataclass
class Cell(Paragraph):
    color: str = ''
    alignment: str = ''
    _background_color: str = ''

    @property
    def background_color(self):
        return self._background_color

    @background_color.setter
    def background_color(self, value):
        self._background_color = {
            "green": "005121",
            "yellow": "B1A749",
            "red": "B12F11",
        }.get(value) or value

    @staticmethod
    def FromText(text: str):
        return Cell(text)

    def __str__(self):
        if self.background_color:
            return tag('td', html.escape(self.text), params={"style": f"background-color: #{self.background_color};"})
        return tag('td', html.escape(self.text))

    @staticmethod
    def RowToStr(row: list):
        row_contents = ''.join(str(cell) for cell in row)
        return tag('tr', row_contents)

    def to_dict(self):
        return {
            "text": self.text,
            "is_bold": self.is_bold,
            "color": self.color,
            "alignment": self.alignment,
            "background_color": self.background_color,
            "type": ReportElementType.CELL.value,
        }

    @staticmethod
    def FromDict(j: dict):
        return Cell(
            color=j.get('color') or '',
            is_bold=j.get('is_bold') or False,
            text=j['text'],
            alignment=j.get('alignment') or '',
            _background_color=j.get('background_color') or ''
        )


@dataclass
class Table:
    body: list[list[Cell]] = field(default_factory=list)
    is_numerated: bool = False
    is_spoiler: bool = False
    spoiler_name: str = ''

    @property
    def width(self):
        if self.body:
            return len(self.body[0])
        return 0

    def append_row(self, row: list[str]):
        if self.width:
            delta = self.width - len(row)
            if delta > 0:
                row = row + [''] * delta
            elif delta < 0:
                row = row[:self.width]
        self.body.append(list(map(Cell.FromText, row)))

    def __str__(self):
        if not self.is_numerated:
            html_rows = list(map(Cell.RowToStr, self.body))
        else:
            numerate = lambda a: [tag('td', str(a[0] or 'N'))] + a[1]
            html_rows = list(map(Cell.RowToStr, map(numerate, enumerate(self.body))))
        result = tag('table', '\n'.join(html_rows), newlines=True)
        if self.is_spoiler:
            if self.spoiler_name:
                result = tag('summary', self.spoiler_name) + '\n' + result
            result = tag('details', result)
        return result

    def to_dict(self):
        return {
            "is_numerated": self.is_numerated,
            "body": [list(map(Cell.to_dict, x)) for x in self.body],
            "is_spoiler": self.is_spoiler,
            "spoiler_name": self.spoiler_name,
            "type": ReportElementType.TABLE.value
        }

    @staticmethod
    def FromDict(j: dict):
        return Table(
            is_numerated=j.get('is_numerated') or False,
            body=from_dict(j['body']),
            is_spoiler=j.get('is_spoiler'),
            spoiler_name=j.get('spoiler_name'),
        )


@dataclass
class Report:
    body: list[Paragraph | Header | Table | Code] = field(default_factory=list)
    css: str = ''
    flag_handle: str = '-'
    remembered: str = ''
    menu_entries: list[MenuEntry] = field(default_factory=list)
    page_name: str = ''
    file_name: str = ''

    def append(self, item):
        self.body.append(item)

    def to_text(self):
        return map(str, self.body)

    def reduce_headers(self, new_zero: int):
        for entry in self.body:
            if type(entry) == Header:
                entry: Header
                entry.level += new_zero

    def ensure_table(self, force_new: bool = False):
        if not self.body or type(self.body[-1]) != Table or force_new:
            self.body.append(Table())
        return self.body[-1]

    def to_dict(self):
        return {
            "css": self.css,
            "body": [x.to_dict() for x in self.body],
            'flag_handle': self.flag_handle,
            'remembered': self.remembered,
            "type": ReportElementType.REPORT.value,
            'menu_entries': [x.to_dict() for x in self.menu_entries],
            'page_name': self.page_name,
            'file_name': self.file_name
        }

    @staticmethod
    def FromDict(j: dict):
        return Report(
            css=j.get('css') or '',
            flag_handle=j.get('flag_handle') or '-',
            remembered=j.get('remembered') or '',
            body=from_dict(j['body']),
            menu_entries=list(map(MenuEntry.FromDict, j.get('menu_entries') or [])),
            page_name=j.get('page_name') or '',
            file_name=j.get('file_name') or ''
        )

    def print(self, file_object):
        file_object.write(tag_open('html') + '\n')
        file_object.write(tag_open('head') + '\n')
        if self.css:
            file_object.write(tag_open('style') + '\n')
            file_object.write(self.css + '\n')
            file_object.write(tag_close('style') + '\n')
        file_object.write(tag_close('head') + '\n')
        file_object.write(tag_open('body') + '\n')

        if self.menu_entries:
            file_object.write('<div class="sidebar">\n')
            file_object.write('<h2>Меню</h2>\n')
            for entry in self.menu_entries:
                file_object.write(f'{entry}\n')
            file_object.write('</div>')
            file_object.write('<div class="content">')
        else:
            file_object.write('<div>')

        for entry in self.to_text():
            file_object.write(entry + '\n')

        file_object.write('</div>')
        file_object.write(tag_close('body') + '\n')
        file_object.write(tag_close('html'))


def from_dict(j: dict | list):
    if type(j) == list:
        return list(map(from_dict, j))
    return ReportElementType(j['type']).Type.FromDict(j)


FLAG_HANDLE = '-'  # session flag handle
script_name, filename, *args = sys.argv
if filename.startswith('-') or filename.startswith('%'):
    args = [filename] + args
    filename = os.environ[ENVIRONMENT_NAME_STATE_FILE]
try:
    with open(filename, 'r', encoding='utf-8') as f:
        report: Report = from_dict(json.load(f))
        FLAG_HANDLE = report.flag_handle
except FileNotFoundError:
    report = Report()
    report.flag_handle = '-'


def test_flag(a: str, flag_prefix=''):
    suffix = a.removeprefix(FLAG_HANDLE + flag_prefix)
    if suffix != a:
        return suffix or ' '
    return ''


def scroll(args_: list[str]):
    result = []
    while args_ and not test_flag(args_[-1]):
        result += [args_.pop()]
    return result


ill = ''
args = list(reversed(args))
scroll(args)
PURE = False
while args:
    arg: str = args.pop()

    if new := test_flag(arg, 'prefix'):
        new = new.strip()
        FLAG_HANDLE = new
        if not new:
            ill = arg
            break
        if 'fixed' in scroll(args):
            report.flag_handle = FLAG_HANDLE

    elif new := test_flag(arg, 'header'):
        header_name = args.pop()
        report.append(Header(text=header_name, level=int(new.strip() or 1)))
        scroll(args)

    elif test_flag(arg, 'par'):
        paragraph_text = args.pop()
        report.append(Paragraph(text=paragraph_text))
        scroll(args)

    elif test_flag(arg, 'css'):
        css_file = args.pop()
        with open(css_file, 'r', encoding='utf-8') as f:
            report.css = ''.join(f)
        scroll(args)

    elif suffix := test_flag(arg, 'code'):
        code_file, *others = scroll(args)
        if 'j' in suffix:  # json wander mode
            code_as_text = wander_json_file(code_file, list(others))
        else:
            with open(code_file, 'r', encoding='utf-8') as f:
                code_as_text = ''.join(f)
        code = Code(code_as_text)
        report.append(code)

    elif test_flag(arg, 'row'):
        table: Table = report.ensure_table()
        row = scroll(args)
        table.append_row(row)

    elif suffix := test_flag(arg, 'set-cell'):
        table: Table = report.ensure_table()
        if not table.body:
            continue
        i, value, *others = scroll(args)
        i = int(i)
        if 'e' in suffix and table.body[-1][i].text:
            continue
        if 'j' in suffix:
            value = wander_json_file(value, list(others))
        table.body[-1][i].text = value

    elif test_flag(arg, 'style'):
        table: Table = report.ensure_table()
        col, action, arg, *others = scroll(args)
        if action == 'color':
            table.body[-1][int(col)].background_color = arg

    elif new := test_flag(arg, 'tweak'):
        cmd, *others = scroll(args)
        if new == '-table':
            table: Table = report.ensure_table()
            if cmd == 'enum':
                table.is_numerated = True
            elif cmd == 'spoiler':
                table.is_spoiler = True
                if others:
                    table.spoiler_name = others[0]
        elif new == '-code':
            code: Code = report.body[-1]
            if cmd == 'spoiler':
                code.is_spoiler = True
                if others:
                    code.spoiler_name = others[0]
        elif new == '-json':
            code: Code = report.body[-1]
            try:
                code_json_as_dict: dict | list = json.loads(code.text)
                if type(code_json_as_dict) != dict:
                    continue
            except json.JSONDecodeError:
                continue
            allowed_x_denied = set(others)
            cmd = cmd.lower()
            if cmd == 'w':
                code_json_as_dict = dict((k, v) for k, v in code_json_as_dict.items() if k in allowed_x_denied)
                code.text = json.dumps(code_json_as_dict, ensure_ascii=True, indent=4)
            elif cmd == 'b':
                code_json_as_dict = dict((k, v) for k, v in code_json_as_dict.items() if k not in allowed_x_denied)
                code.text = json.dumps(code_json_as_dict, ensure_ascii=True, indent=4)

    elif new := test_flag(arg, 'include'):
        if not new.isdecimal():
            new = 0
        filename2, *others = scroll(args)
        with open(filename2, 'r', encoding='utf-8') as f:
            secondary_report: Report = from_dict(json.load(f))
        secondary_report.reduce_headers(int(new))
        report.body += secondary_report.body

    elif (new := test_flag(arg, 'csv')) != '':
        filename2, *others = scroll(args)
        subset = [int(i) for i in others if str(i).isdecimal()]
        is_excel_mode = 'e' in new
        encoding = 'cp1251' if is_excel_mode else 'utf-8'
        with open(filename2, 'r', encoding=encoding) as f:
            reader = csv.reader(f, delimiter=';' if is_excel_mode else ',', lineterminator='\n')
            data = list(reader)
        if subset:
            data = [select(line, subset) for line in data]
        is_append_mode = 'a' in new
        table: Table = report.ensure_table(force_new=not is_append_mode)
        for row in data:
            table.append_row(row)

    elif test_flag(arg, 'release') or test_flag(arg, 'render') or test_flag(arg, 'print'):
        filename2, *others = scroll(args) + ['']
        filename2 = filename2 or report.file_name
        if not filename2:
            continue
        with open(filename2, 'w', encoding='utf-8') as report_release_file:
            report.print(report_release_file)

    elif new := test_flag(arg, 'givename'):
        others = scroll(args) + ['']
        name, filename2, *others = others
        filename2 = filename2 or name.replace(' ', '_')
        report.page_name = name
        report.file_name = filename2

    elif new := test_flag(arg, 'connect'):
        if report.menu_entries and 'a' not in new:
            continue
        others = scroll(args)
        if 's' not in new:
            others = [path for path in others if Path(path).resolve(strict=False) != Path(filename).resolve(strict=False)]
        menu = []
        files = []
        for path in others:
            page_name, file_name, has_menu = MenuEntry.GetNamesFromFile(path)
            if has_menu and 'o' not in new:
                continue
            menu.append(MenuEntry(page_name, file_name))
            files.append(path)
        menu = [MenuEntry(report.page_name, report.file_name)] + menu
        report.menu_entries = menu
        if '1' in new:
            continue
        if len(menu) == 1:
            continue
        for path in files:
            MenuEntry.SetMenuEntriesToFile(path, menu, report.css if 'c' in new else '')

    elif test_flag(arg, 'disconnect'):
        others = scroll(args)
        report.menu_entries = []

    elif new := test_flag(arg, 'remember'):
        value, *others = scroll(args)
        report.remembered = value

    elif new := test_flag(arg, 'terminateif'):
        if new == 'eq':
            arg1, arg2, *others = scroll(args)
            if arg1 == arg2:
                break
        elif new == 'eqnt':
            arg1, arg2, *others = scroll(args)
            if arg1 != arg2:
                break
        elif new == 'memeq':
            arg1, *others = scroll(args)
            if arg1 == report.remembered:
                break
        elif new == 'memeqnt':
            arg1, *others = scroll(args)
            if arg1 != report.remembered:
                break
        else:
            others = scroll(args)
            if others:
                arg1, *others = others
                arg1 = arg1.lower()
                if arg1 not in ['0', 'false', '', 'no']:
                    break

    elif test_flag(arg, 'pure'):
        PURE = True
        scroll(args)

    elif test_flag(arg, 'echo'):
        print(scroll(args))

if ill:
    raise ValueError(f'Ill-formed argument: "{ill}"')

if not PURE:
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report.to_dict(), f, ensure_ascii=False, indent=4)

