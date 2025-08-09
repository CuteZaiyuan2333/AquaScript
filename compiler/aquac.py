"""
AquaScript编译器主程序
将.aqua源文件编译为.acode字节码
"""

import sys
import os
import argparse
from lexer import Lexer
from parser import Parser
from codegen import CodeGenerator

def compile_file(source_file: str, output_file: str = None):
    """编译AquaScript源文件"""
    
    # 检查源文件是否存在
    if not os.path.exists(source_file):
        print(f"Error: Source file '{source_file}' not found")
        return False
    
    # 确定输出文件名
    if output_file is None:
        base_name = os.path.splitext(source_file)[0]
        output_file = base_name + '.acode'
    
    try:
        # 读取源代码
        with open(source_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        print(f"Compiling {source_file}...")
        
        # 词法分析
        print("  Lexical analysis...")
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        # 语法分析
        print("  Syntax analysis...")
        parser = Parser(tokens)
        ast = parser.parse()
        
        # 代码生成
        print("  Code generation...")
        codegen = CodeGenerator()
        bytecode = codegen.generate(ast)
        
        # 写入字节码文件
        with open(output_file, 'wb') as f:
            f.write(bytecode)
        
        print(f"  Output: {output_file}")
        print(f"  Size: {len(bytecode)} bytes")
        print(f"  Constants: {len(codegen.constants)}")
        print(f"  Functions: {len(codegen.functions)}")
        print("Compilation successful!")
        
        return True
        
    except SyntaxError as e:
        print(f"Syntax Error: {e}")
        return False
    except Exception as e:
        print(f"Compilation Error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='AquaScript Compiler')
    parser.add_argument('source', help='Source file (.aqua)')
    parser.add_argument('-o', '--output', help='Output file (.acode)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # 检查源文件扩展名
    if not args.source.endswith('.aqua'):
        print("Warning: Source file should have .aqua extension")
    
    # 编译文件
    success = compile_file(args.source, args.output)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()