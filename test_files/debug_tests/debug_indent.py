"""
调试缩进问题
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'compiler'))

from lexer import Lexer, TokenType

def debug_indentation():
    """调试缩进处理"""
    code = '''def test():
    if True:
        print("Hello")
    else:
        print("World")
'''
    
    print("Source code:")
    print(repr(code))
    
    print("\nLine by line analysis:")
    lines = code.split('\n')
    for i, line in enumerate(lines, 1):
        if line.strip():  # 只显示非空行
            indent_count = len(line) - len(line.lstrip())
            print(f"Line {i}: indent={indent_count:2} '{line}'")
    
    print("\nTokens:")
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    
    indent_count = 0
    dedent_count = 0
    
    for i, token in enumerate(tokens):
        if token.type in [TokenType.INDENT, TokenType.DEDENT, TokenType.NEWLINE, TokenType.DEF, TokenType.IF, TokenType.ELSE]:
            print(f"{i:2}: {token.type.value:15} '{token.value}' Line: {token.line}, Col: {token.column}")
            
            if token.type == TokenType.INDENT:
                indent_count += 1
            elif token.type == TokenType.DEDENT:
                dedent_count += 1
    
    print(f"\nINDENT count: {indent_count}")
    print(f"DEDENT count: {dedent_count}")

if __name__ == "__main__":
    debug_indentation()