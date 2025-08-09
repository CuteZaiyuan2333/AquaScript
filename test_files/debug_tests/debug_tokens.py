#!/usr/bin/env python3

from compiler.lexer import Lexer

def debug_tokens(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        source = f.read()
    
    print(f"Source code:")
    print(repr(source))
    print("\nTokens:")
    
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    for i, token in enumerate(tokens):
        print(f"{i:2}: {token.type.value:15} '{token.value}' Line: {token.line}, Col: {token.column}")

if __name__ == "__main__":
    debug_tokens("test_class.aqua")