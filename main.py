from dataclasses import dataclass, field
import sys
from enum import Enum
import json
import html


class ReportElementType(Enum):
    REPORT = 'report'
    TABLE = 'table'
    CELL = 'cell'
    PARAGRAPH = 'paragraph'
    HEADER = 'header'

    @property
    def Type(self):
        return {
            ReportElementType.REPORT: Report,
            ReportElementType.HEADER: Header,
            ReportElementType.CELL: Cell,
            ReportElementType.PARAGRAPH: Paragraph,
            ReportElementType.TABLE: Table,
        }[self]


def tag_open(tagname: str):
    return f'<{tagname}>'


def tag(tagname: str, text: str, newlines: bool = False):
    sep = '\n' if newlines else ''
    return f'<{tagname}>{sep}{text}{sep}</{tagname}>'


def tag_close(tagname: str):
    return f'</{tagname}>'


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
            is_bold=j['is_bold'],
            text=j['text'],
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
            is_bold=j['is_bold'],
            text=j['text'],
        )


@dataclass
class Cell(Paragraph):
    color: str = ''
    alignment: str = ''

    @staticmethod
    def FromText(text: str):
        return Cell(text)

    def __str__(self):
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
            "type": ReportElementType.CELL.value
        }

    @staticmethod
    def FromDict(j: dict):
        return Cell(
            color=j['color'],
            is_bold=j['is_bold'],
            text=j['text'],
            alignment=j['alignment'],
        )


@dataclass
class Table:
    body: list[list[Cell]] = field(default_factory=list)
    is_numerated: bool = False

    def append_row(self, row: list[str]):
        if self.body and (delta := len(self.body[0]) - len(row)) > 0:
            row = row + [''] * delta
        self.body.append(list(map(Cell.FromText, row)))

    def __str__(self):
        if not self.is_numerated:
            html_rows = list(map(Cell.RowToStr, self.body))
        else:
            numerate = lambda a: [tag('td', str(a[0] or 'N'))] + a[1]
            html_rows = list(map(Cell.RowToStr, map(numerate, enumerate(self.body))))
        return tag('table', '\n'.join(html_rows), newlines=True)

    def to_dict(self):
        return {
            "is_numerated": self.is_numerated,
            "body": [list(map(Cell.to_dict, x)) for x in self.body],
            "type": ReportElementType.TABLE.value
        }

    @staticmethod
    def FromDict(j: dict):
        return Table(
            is_numerated=j['is_numerated'],
            body=from_dict(j['body'])
        )


@dataclass
class Report:
    body: list[Paragraph | Header | Table] = field(default_factory=list)
    css: str = ''

    def append(self, item):
        self.body.append(item)

    def to_text(self):
        return map(str, self.body)

    def reduce_headers(self, new_zero: int):
        for entry in self.body:
            if type(entry) == Header:
                entry: Header
                entry.level += new_zero

    def ensure_table(self):
        if not self.body or type(self.body[-1]) != Table:
            self.body.append(Table())
        return self.body[-1]

    def to_dict(self):
        return {
            "css": self.css,
            "body": [x.to_dict() for x in self.body],
            "type": ReportElementType.REPORT.value
        }

    @staticmethod
    def FromDict(j: dict):
        return Report(
            css=j['css'],
            body=from_dict(j['body'])
        )


def from_dict(j: dict | list):
    if type(j) == list:
        return list(map(from_dict, j))
    return ReportElementType(j['type']).Type.FromDict(j)


FLAG_HANDLE = '-'
script_name, filename, *args = sys.argv
try:
    with open(filename, 'r', encoding='utf-8') as f:
        report: Report = from_dict(json.load(f))
except FileNotFoundError:
    report = Report()


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
while args:
    arg: str = args.pop()

    if new := test_flag(arg, 'prefix'):
        new = new.strip()
        FLAG_HANDLE = new
        if not new:
            ill = arg
            break

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

    elif test_flag(arg, 'row'):
        table: Table = report.ensure_table()
        row = scroll(args)
        table.append_row(row)

    elif test_flag(arg, 'tweak-table'):
        table: Table = report.ensure_table()
        cmd = args.pop()
        if cmd == 'enum':
            table.is_numerated = True
        scroll(args)

    elif (new := test_flag(arg, 'include')) != '':
        if not new.isdecimal():
            new = 0
        filename2, *others = scroll(args)
        with open(filename2, 'r', encoding='utf-8') as f:
            secondary_report: Report = from_dict(json.load(f))
        secondary_report.reduce_headers(int(new))
        report.body += secondary_report.body

    elif test_flag(arg, 'release') or test_flag(arg, 'render'):
        filename2, *others = scroll(args)
        with open(filename2, 'w', encoding='utf-8') as report_release_file:
            report_release_file.write(tag_open('html') + '\n')
            report_release_file.write(tag_open('head') + '\n')
            if report.css:
                report_release_file.write(tag_open('style') + '\n')
                report_release_file.write(report.css + '\n')
                report_release_file.write(tag_close('style') + '\n')
            report_release_file.write(tag_close('head') + '\n')
            report_release_file.write(tag_open('body') + '\n')

            for entry in report.to_text():
                report_release_file.write(entry + '\n')

            report_release_file.write(tag_close('body') + '\n')
            report_release_file.write(tag_close('html'))
            report_release_file.close()

if ill:
    raise ValueError(f'Ill-formed argument: "{ill}"')

with open(filename, 'w', encoding='utf-8') as f:
    json.dump(report.to_dict(), f, ensure_ascii=False, indent=4)

