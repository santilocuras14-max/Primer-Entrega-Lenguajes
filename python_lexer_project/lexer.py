
import re
from typing import Iterator, List
from tokens import Token

KEYWORDS = {
    "False","None","True","and","as","assert","async","await","break","class","continue",
    "def","del","elif","else","except","finally","for","from","global","if","import",
    "in","is","lambda","nonlocal","not","or","pass","raise","return","try","while","with","yield",
    "match","case",
}

OPERATORS = [
    '>>>', '<<=', '>>=',
    '**', '//', '==', '!=', '<=', '>=', '->', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '<<', '>>', '**=', '//=',
    '+','-','*','/','%','<','>','=','&','|','^','~','@',':','.'
]
DELIMITERS = ['(',')','[',']','{','}',';',',']

re_identifier = re.compile(r'[A-Za-z_][A-Za-z_0-9]*')
re_number = re.compile(
    r'''
    (?:
        0[bB][01](?:_?[01])* |
        0[oO][0-7](?:_?[0-7])* |
        0[xX][0-9a-fA-F](?:_?[0-9a-fA-F])* |
        (?:
            (?:\d(?:_?\d)*)?
            \.[0-9](?:_?[0-9])*
            (?:[eE][+-]?\d(?:_?\d)*)?
        )
        |
        (?:
            \d(?:_?\d)*
            (?:\.[0-9](?:_?[0-9])*)?
            (?:[eE][+-]?\d(?:_?\d)*)?
        )
    )
    ''',
    re.VERBOSE
)
re_string_simple = re.compile(r'''
    (?P<quote>["'])
    (?P<body>(?:\.|[^\\\n])*?)
    (?P=quote)
''', re.VERBOSE)
re_string_triple = re.compile(
    '(?P<quote>\'\'\'|""")(?P<body>.*?)(?P=quote)',
    re.DOTALL
)

def expand_tab_column(col: int) -> int:
    return col + (8 - (col % 8 or 8))

class Lexer:
    def __init__(self):
        self.indents: List[int] = [0]
        self.line = 1
        self.pos = 0
        self.src = ''
        self.len = 0

    def tokenize(self, src: str) -> Iterator[Token]:
        self.src = src.replace('\r\n', '\n').replace('\r', '\n')
        self.len = len(self.src)
        self.pos = 0
        self.line = 1
        self.indents = [0]
        at_line_start = True

        while self.pos < self.len:
            if at_line_start:
                col = 0
                while self.pos < self.len:
                    c = self.src[self.pos]
                    if c == ' ':
                        self.pos += 1; col += 1
                    elif c == '\t':
                        self.pos += 1; col = expand_tab_column(col)
                    else:
                        break
                if self.pos < self.len and self.src[self.pos] == '#':
                    while self.pos < self.len and self.src[self.pos] != '\n':
                        self.pos += 1
                if self.pos >= self.len or self.src[self.pos] == '\n':
                    if self.pos < self.len and self.src[self.pos] == '\n':
                        self.pos += 1
                        yield Token('NEWLINE', '\n', self.line, 1)
                        self.line += 1
                    at_line_start = True
                    continue
                else:
                    curr = self.indents[-1]
                    if col > curr:
                        self.indents.append(col)
                        yield Token('INDENT', col, self.line, 1)
                    else:
                        while col < self.indents[-1]:
                            self.indents.pop()
                            yield Token('DEDENT', col, self.line, 1)
                        if col != self.indents[-1]:
                            raise IndentationError(f'Indentación inconsistente en línea {self.line}')
                    at_line_start = False

            ch = self.src[self.pos]
            if ch == '#':
                while self.pos < self.len and self.src[self.pos] != '\n':
                    self.pos += 1
                continue
            if ch == '\n':
                self.pos += 1
                yield Token('NEWLINE', '\n', self.line, 1)
                self.line += 1
                at_line_start = True
                continue

            m = re_string_triple.match(self.src, self.pos)
            if m:
                text = m.group(0)
                col = self._col_from_line_start(self.pos)
                self.pos = m.end()
                self.line += text.count('\n')
                yield Token('STRING', text, self.line, col)
                continue

            m = re_string_simple.match(self.src, self.pos)
            if m:
                text = m.group(0)
                col = self._col_from_line_start(self.pos)
                self.pos = m.end()
                yield Token('STRING', text, self.line, col)
                continue

            m = re_number.match(self.src, self.pos)
            if m:
                text = m.group(0)
                col = self._col_from_line_start(self.pos)
                self.pos = m.end()
                yield Token('NUMBER', text, self.line, col)
                continue

            m = re_identifier.match(self.src, self.pos)
            if m:
                text = m.group(0)
                col = self._col_from_line_start(self.pos)
                self.pos = m.end()
                if text in KEYWORDS:
                    yield Token('KEYWORD', text, self.line, col)
                else:
                    yield Token('IDENTIFIER', text, self.line, col)
                continue

            found = None
            for cand in sorted(OPERATORS + DELIMITERS, key=lambda s: -len(s)):
                if self.src.startswith(cand, self.pos):
                    found = cand
                    break
            if found is not None:
                tok_type = 'OP' if found in OPERATORS else 'DELIM'
                col = self._col_from_line_start(self.pos)
                self.pos += len(found)
                yield Token(tok_type, found, self.line, col)
                continue

            if ch in ' \t':
                self.pos += 1
                continue

            col = self._col_from_line_start(self.pos)
            raise SyntaxError(f'Carácter inesperado {repr(ch)} en línea {self.line}, columna {col}')

        if not self.src.endswith('\n'):
            yield Token('NEWLINE', '\n', self.line, 1)
        while len(self.indents) > 1:
            self.indents.pop()
            yield Token('DEDENT', 0, self.line, 1)
        yield Token('EOF', '', self.line, 1)

    def _col_from_line_start(self, pos: int) -> int:
        i = pos
        start = self.src.rfind('\n', 0, i) + 1
        col = 1
        while start < i:
            c = self.src[start]
            if c == '\t':
                offs = ((8 - ((col - 1) % 8)) % 8) or 8
                col += offs
            else:
                col += 1
            start += 1
        return col
