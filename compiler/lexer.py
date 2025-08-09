"""
AquaScript词法分析器
负责将源代码转换为token流
"""

import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Iterator

class TokenType(Enum):
    # 字面量
    NUMBER = "NUMBER"
    STRING = "STRING"
    F_STRING = "F_STRING"   # f-string字面量
    IDENTIFIER = "IDENTIFIER"
    
    # 关键字
    FUNC = "FUNC"           # func (函数定义)
    VAR = "VAR"             # var (变量定义)
    IF = "IF"
    ELSE = "ELSE"
    ELIF = "ELIF"
    FOR = "FOR"
    WHILE = "WHILE"
    REPEAT = "REPEAT"       # repeat (重复循环)
    IN = "IN"
    RETURN = "RETURN"
    BREAK = "BREAK"
    CONTINUE = "CONTINUE"
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    TRUE = "TRUE"
    FALSE = "FALSE"
    NONE = "NONE"
    CLASS = "CLASS"         # class (类定义)
    SELF = "SELF"           # self
    IMPORT = "IMPORT"       # import
    FROM = "FROM"           # from
    SWITCH = "SWITCH"       # switch
    CASE = "CASE"           # case
    DEFAULT = "DEFAULT"     # default
    TRY = "TRY"             # try
    CATCH = "CATCH"         # catch
    FINALLY = "FINALLY"     # finally
    THROW = "THROW"         # throw
    AS = "AS"               # as (用于 catch Exception as e)
    
    # 类型关键字
    INT = "INT"             # int
    FLOAT = "FLOAT"         # float
    STR = "STR"             # str
    BOOL = "BOOL"           # bool
    LIST = "LIST"           # list
    
    # 运算符
    PLUS = "PLUS"           # +
    MINUS = "MINUS"         # -
    MULTIPLY = "MULTIPLY"   # *
    DIVIDE = "DIVIDE"       # /
    MODULO = "MODULO"       # %
    POWER = "POWER"         # **
    
    # 比较运算符
    EQUAL = "EQUAL"         # ==
    NOT_EQUAL = "NOT_EQUAL" # !=
    LESS = "LESS"           # <
    GREATER = "GREATER"     # >
    LESS_EQUAL = "LESS_EQUAL"     # <=
    GREATER_EQUAL = "GREATER_EQUAL" # >=
    ARROW = "ARROW"         # ->
    
    # 赋值
    ASSIGN = "ASSIGN"       # =
    
    # 分隔符
    LPAREN = "LPAREN"       # (
    RPAREN = "RPAREN"       # )
    LBRACKET = "LBRACKET"   # [
    RBRACKET = "RBRACKET"   # ]
    LBRACE = "LBRACE"       # {
    RBRACE = "RBRACE"       # }
    COMMA = "COMMA"         # ,
    COLON = "COLON"         # :
    DOT = "DOT"             # .
    
    # 特殊
    NEWLINE = "NEWLINE"
    INDENT = "INDENT"
    DEDENT = "DEDENT"
    EOF = "EOF"
    COMMENT = "COMMENT"

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

class Lexer:
    def __init__(self, source_code: str):
        self.source = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.indent_stack = [0]  # 缩进栈
        
        # 关键字映射
        self.keywords = {
            'func': TokenType.FUNC,
            'var': TokenType.VAR,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'elif': TokenType.ELIF,
            'for': TokenType.FOR,
            'while': TokenType.WHILE,
            'repeat': TokenType.REPEAT,
            'in': TokenType.IN,
            'return': TokenType.RETURN,
            'break': TokenType.BREAK,
            'continue': TokenType.CONTINUE,
            'and': TokenType.AND,
            'or': TokenType.OR,
            'not': TokenType.NOT,
            'True': TokenType.TRUE,
            'False': TokenType.FALSE,
            'true': TokenType.TRUE,
            'false': TokenType.FALSE,
            'None': TokenType.NONE,
            'class': TokenType.CLASS,
            'self': TokenType.SELF,
            'import': TokenType.IMPORT,
            'from': TokenType.FROM,
            'switch': TokenType.SWITCH,
            'case': TokenType.CASE,
            'default': TokenType.DEFAULT,
            'try': TokenType.TRY,
            'catch': TokenType.CATCH,
            'finally': TokenType.FINALLY,
            'throw': TokenType.THROW,
            'as': TokenType.AS,
            # 类型关键字
            'int': TokenType.INT,
            'float': TokenType.FLOAT,
            'str': TokenType.STR,
            'bool': TokenType.BOOL,
            'list': TokenType.LIST,
        }
    
    def current_char(self) -> Optional[str]:
        if self.position >= len(self.source):
            return None
        return self.source[self.position]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        peek_pos = self.position + offset
        if peek_pos >= len(self.source):
            return None
        return self.source[peek_pos]
    
    def advance(self):
        if self.position < len(self.source) and self.source[self.position] == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.position += 1
    
    def skip_whitespace(self):
        while self.current_char() and self.current_char() in ' \t':
            self.advance()
    
    def read_number(self) -> Token:
        start_pos = self.position
        start_col = self.column
        
        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            self.advance()
        
        value = self.source[start_pos:self.position]
        return Token(TokenType.NUMBER, value, self.line, start_col)
    
    def read_string(self) -> Token:
        start_col = self.column
        quote_char = self.current_char()
        self.advance()  # 跳过开始引号
        
        value = ""
        while self.current_char() and self.current_char() != quote_char:
            if self.current_char() == '\\':
                self.advance()
                if self.current_char():
                    # 处理转义字符
                    escape_chars = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', '"': '"', "'": "'"}
                    value += escape_chars.get(self.current_char(), self.current_char())
                    self.advance()
            else:
                value += self.current_char()
                self.advance()
        
        if self.current_char() == quote_char:
            self.advance()  # 跳过结束引号
        
        return Token(TokenType.STRING, value, self.line, start_col)
    
    def read_f_string(self) -> Token:
        """读取f-string字面量，格式如 f"Hello {name}" """
        start_col = self.column
        self.advance()  # 跳过 'f'
        quote_char = self.current_char()
        self.advance()  # 跳过开始引号
        
        # 存储f-string的各个部分：文本和表达式
        parts = []
        current_text = ""
        
        while self.current_char() and self.current_char() != quote_char:
            if self.current_char() == '\\':
                self.advance()
                if self.current_char():
                    # 处理转义字符
                    escape_chars = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', '"': '"', "'": "'"}
                    current_text += escape_chars.get(self.current_char(), self.current_char())
                    self.advance()
            elif self.current_char() == '{':
                # 保存当前文本部分
                if current_text:
                    parts.append({'type': 'text', 'value': current_text})
                    current_text = ""
                
                # 读取表达式
                self.advance()  # 跳过 '{'
                expr = ""
                brace_count = 1
                
                while self.current_char() and brace_count > 0:
                    if self.current_char() == '{':
                        brace_count += 1
                    elif self.current_char() == '}':
                        brace_count -= 1
                    
                    if brace_count > 0:
                        expr += self.current_char()
                    self.advance()
                
                parts.append({'type': 'expression', 'value': expr.strip()})
            else:
                current_text += self.current_char()
                self.advance()
        
        # 保存最后的文本部分
        if current_text:
            parts.append({'type': 'text', 'value': current_text})
        
        if self.current_char() == quote_char:
            self.advance()  # 跳过结束引号
        
        # 将parts编码为字符串，用于传递给parser
        import json
        value = json.dumps(parts)
        return Token(TokenType.F_STRING, value, self.line, start_col)
    
    def read_identifier(self) -> Token:
        start_pos = self.position
        start_col = self.column
        
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            self.advance()
        
        value = self.source[start_pos:self.position]
        token_type = self.keywords.get(value, TokenType.IDENTIFIER)
        return Token(token_type, value, self.line, start_col)
    
    def read_comment(self) -> Token:
        start_col = self.column
        self.advance()  # 跳过 #
        
        value = ""
        while self.current_char() and self.current_char() != '\n':
            value += self.current_char()
            self.advance()
        
        return Token(TokenType.COMMENT, value.strip(), self.line, start_col)
    
    def handle_indentation(self, line_start_pos: int) -> List[Token]:
        """处理行首的缩进"""
        indent_level = 0
        pos = line_start_pos
        
        while pos < len(self.source) and self.source[pos] in ' \t':
            if self.source[pos] == ' ':
                indent_level += 1
            elif self.source[pos] == '\t':
                indent_level += 4  # tab = 4 spaces
            pos += 1
        
        tokens = []
        current_indent = self.indent_stack[-1]
        
        if indent_level > current_indent:
            self.indent_stack.append(indent_level)
            tokens.append(Token(TokenType.INDENT, "", self.line, 1))
        elif indent_level < current_indent:
            while self.indent_stack and self.indent_stack[-1] > indent_level:
                self.indent_stack.pop()
                tokens.append(Token(TokenType.DEDENT, "", self.line, 1))
        
        return tokens
    
    def tokenize(self) -> List[Token]:
        tokens = []
        line_start = True
        
        while self.position < len(self.source):
            char = self.current_char()
            
            if char is None:
                break
            
            # 换行符
            if char == '\n':
                tokens.append(Token(TokenType.NEWLINE, char, self.line, self.column))
                self.advance()
                line_start = True
                continue
            
            # 处理行首缩进
            if line_start:
                # 检查这一行是否只有空白字符
                temp_pos = self.position
                while temp_pos < len(self.source) and self.source[temp_pos] in ' \t':
                    temp_pos += 1
                
                # 如果这一行不是空行且不是注释行，处理缩进
                if temp_pos < len(self.source) and self.source[temp_pos] not in '\n#':
                    indent_tokens = self.handle_indentation(self.position)
                    tokens.extend(indent_tokens)
                
                # 跳过行首的空白字符
                self.skip_whitespace()
                line_start = False
                continue
            
            # 跳过空格和制表符
            if char in ' \t':
                self.skip_whitespace()
                continue
            
            # 注释
            if char == '#':
                comment_token = self.read_comment()
                tokens.append(comment_token)
                continue
            
            # 数字
            if char.isdigit():
                tokens.append(self.read_number())
                continue
            
            # 字符串
            if char in '"\'':
                tokens.append(self.read_string())
                continue
            
            # f-string 检查
            if char == 'f' and self.peek_char() in '"\'':
                tokens.append(self.read_f_string())
                continue
            
            # 标识符和关键字
            if char.isalpha() or char == '_':
                tokens.append(self.read_identifier())
                continue
            
            # 双字符运算符
            if char == '*' and self.peek_char() == '*':
                tokens.append(Token(TokenType.POWER, "**", self.line, self.column))
                self.advance()
                self.advance()
                continue
            
            if char == '=' and self.peek_char() == '=':
                tokens.append(Token(TokenType.EQUAL, "==", self.line, self.column))
                self.advance()
                self.advance()
                continue
            
            if char == '!' and self.peek_char() == '=':
                tokens.append(Token(TokenType.NOT_EQUAL, "!=", self.line, self.column))
                self.advance()
                self.advance()
                continue
            
            if char == '<' and self.peek_char() == '=':
                tokens.append(Token(TokenType.LESS_EQUAL, "<=", self.line, self.column))
                self.advance()
                self.advance()
                continue
            
            if char == '>' and self.peek_char() == '=':
                tokens.append(Token(TokenType.GREATER_EQUAL, ">=", self.line, self.column))
                self.advance()
                self.advance()
                continue
            
            # 检查箭头运算符 ->
            if char == '-' and self.peek_char() == '>':
                tokens.append(Token(TokenType.ARROW, "->", self.line, self.column))
                self.advance()
                self.advance()
                continue
            
            # 单字符token
            single_char_tokens = {
                '+': TokenType.PLUS,
                '-': TokenType.MINUS,
                '*': TokenType.MULTIPLY,
                '/': TokenType.DIVIDE,
                '%': TokenType.MODULO,
                '=': TokenType.ASSIGN,
                '<': TokenType.LESS,
                '>': TokenType.GREATER,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                '[': TokenType.LBRACKET,
                ']': TokenType.RBRACKET,
                '{': TokenType.LBRACE,
                '}': TokenType.RBRACE,
                ',': TokenType.COMMA,
                ':': TokenType.COLON,
                '.': TokenType.DOT,
            }
            
            if char in single_char_tokens:
                tokens.append(Token(single_char_tokens[char], char, self.line, self.column))
                self.advance()
                continue
            
            # 未知字符
            raise SyntaxError(f"Unexpected character '{char}' at line {self.line}, column {self.column}")
        
        # 处理文件结尾的DEDENT
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            tokens.append(Token(TokenType.DEDENT, "", self.line, self.column))
        
        tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return tokens

def main():
    # 测试词法分析器
    test_code = '''
def greet(name):
    if name:
        print("Hello, " + name + "!")
    else:
        print("Hello, World!")
    return True

greet("AquaScript")
'''
    
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    
    for token in tokens:
        print(f"{token.type.value:15} {token.value:10} Line: {token.line}, Col: {token.column}")

if __name__ == "__main__":
    main()