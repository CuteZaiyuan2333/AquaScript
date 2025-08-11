#!/usr/bin/env python3
"""
测试新的导入语法解析
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'compiler'))

from lexer import Lexer
from parser import Parser

def test_new_import_syntax():
    """测试新的导入语法"""
    
    test_cases = [
        # 传统语法
        "import math",
        "import os.path",
        
        # 新语法
        "import typing.(TypeVar, Generic, Union)",
        "import collections.(defaultdict, Counter)",
        "import asyncio.(Queue, Event, Semaphore, Lock)",
        
        # 复杂情况
        "import urllib.(parse, request, error)",
        "import concurrent.futures.(ThreadPoolExecutor, ProcessPoolExecutor)",
    ]
    
    print("=== 测试新的导入语法解析 ===\n")
    
    for i, code in enumerate(test_cases, 1):
        print(f"测试 {i}: {code}")
        
        try:
            # 词法分析
            lexer = Lexer(code)
            tokens = list(lexer.tokenize())
            print(f"  Tokens: {[f'{t.type.value}({t.value})' for t in tokens if t.type.value != 'EOF']}")
            
            # 语法分析
            parser = Parser(tokens)
            ast = parser.parse_import_statement()
            print(f"  AST: module='{ast.module}', items={ast.items}")
            print("  ✅ 解析成功")
            
        except Exception as e:
            print(f"  ❌ 解析失败: {e}")
        
        print()

if __name__ == "__main__":
    test_new_import_syntax()