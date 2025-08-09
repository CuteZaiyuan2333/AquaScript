#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'compiler'))
from lexer import Lexer
from parser import Parser

def debug_parse():
    with open('examples/new_syntax_demo.aqua', 'r', encoding='utf-8') as f:
        code = f.read()
    
    print("开始词法分析...")
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    print(f"生成了 {len(tokens)} 个token")
    
    # 打印前50个token
    print("\n前50个token:")
    for i, token in enumerate(tokens[:50]):
        print(f"{i:2d}: {token.type.name:15} {repr(token.value)}")
    
    print("\n开始语法分析...")
    parser = Parser(tokens)
    
    try:
        ast = parser.parse()
        print("语法分析成功!")
    except Exception as e:
        print(f"语法分析失败: {e}")
        print(f"当前位置: {parser.position}")
        print(f"当前token: {parser.current_token}")
        
        # 打印当前位置附近的token
        print("\n当前位置附近的token:")
        start = max(0, parser.position - 5)
        end = min(len(tokens), parser.position + 5)
        for i in range(start, end):
            marker = " -> " if i == parser.position else "    "
            print(f"{marker}{i:2d}: {tokens[i].type.name:15} {repr(tokens[i].value)}")

if __name__ == "__main__":
    debug_parse()