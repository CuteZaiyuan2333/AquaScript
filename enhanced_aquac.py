#!/usr/bin/env python3
"""
增强版AquaScript编译器
支持新的语法特性和Python生态系统集成
"""

import sys
import os
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.codegen import CodeGenerator
from vm.enhanced_aquavm import EnhancedAquaVM

def compile_file(source_file: str, output_file: str = None, verbose: bool = False):
    """编译AquaScript文件"""
    try:
        # 读取源文件
        with open(source_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        if verbose:
            print(f"正在编译: {source_file}")
        
        # 词法分析
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        if verbose:
            print(f"词法分析完成，生成 {len(tokens)} 个token")
        
        # 语法分析
        parser = Parser(tokens)
        ast = parser.parse()
        
        if verbose:
            print("语法分析完成")
        
        # 代码生成
        codegen = CodeGenerator()
        bytecode = codegen.generate(ast)
        
        if verbose:
            print("代码生成完成")
        
        # 确定输出文件名
        if output_file is None:
            output_file = source_file.replace('.aqua', '.acode')
        
        # 写入字节码文件
        with open(output_file, 'wb') as f:
            f.write(bytecode)
        
        if verbose:
            print(f"字节码已写入: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"编译错误: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False

def run_file(bytecode_file: str, verbose: bool = False):
    """运行AquaScript字节码文件"""
    try:
        # 创建增强版虚拟机
        vm = EnhancedAquaVM()
        
        if verbose:
            print(f"正在运行: {bytecode_file}")
        
        # 加载并运行字节码
        with open(bytecode_file, 'rb') as f:
            bytecode = f.read()
        
        vm.load_bytecode(bytecode)
        vm.run()
        
        if verbose:
            print("程序执行完成")
        
        return True
        
    except Exception as e:
        print(f"运行错误: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False

def compile_and_run(source_file: str, verbose: bool = False):
    """编译并运行AquaScript文件"""
    # 生成临时字节码文件名
    bytecode_file = source_file.replace('.aqua', '.acode')
    
    # 编译
    if compile_file(source_file, bytecode_file, verbose):
        # 运行
        return run_file(bytecode_file, verbose)
    
    return False

def interactive_mode():
    """交互式模式"""
    print("AquaScript 增强版交互式解释器")
    print("输入 'exit' 或 'quit' 退出")
    print("输入 'help' 查看帮助")
    
    vm = EnhancedAquaVM()
    
    while True:
        try:
            line = input(">>> ").strip()
            
            if line in ['exit', 'quit']:
                break
            elif line == 'help':
                print_help()
                continue
            elif line == '':
                continue
            
            # 编译并执行单行代码
            lexer = Lexer(line)
            tokens = lexer.tokenize()
            
            parser = Parser(tokens)
            ast = parser.parse()
            
            codegen = CodeGenerator()
            bytecode = codegen.generate(ast)
            
            vm.load_bytecode(bytecode)
            vm.run()
            
        except KeyboardInterrupt:
            print("\n使用 'exit' 或 'quit' 退出")
        except Exception as e:
            print(f"错误: {e}")

def print_help():
    """打印帮助信息"""
    help_text = """
AquaScript 增强版编译器帮助

新语法特性:
1. 函数定义: func name(params) -> return_type:
2. 变量声明: var name: type = value
3. 类定义: class ClassName:
4. repeat循环: repeat: ... while condition
5. switch语句: switch expr: case value: ...
6. Python模块导入: import module / from module import items

类型系统:
- int: 整数
- float: 浮点数
- str: 字符串
- bool: 布尔值
- list: 列表
- dict: 字典

Python集成:
- 可以导入和使用Python标准库
- 支持调用Python函数和类
- 自动类型转换

示例:
    import math
    var radius: float = 5.0
    var area: float = math.pi * radius * radius
    print("Area: " + str(area))
"""
    print(help_text)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AquaScript 增强版编译器')
    parser.add_argument('file', nargs='?', help='要编译/运行的AquaScript文件')
    parser.add_argument('-c', '--compile', action='store_true', help='只编译，不运行')
    parser.add_argument('-r', '--run', action='store_true', help='运行字节码文件')
    parser.add_argument('-o', '--output', help='输出文件名')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    parser.add_argument('-i', '--interactive', action='store_true', help='交互式模式')
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
        return
    
    if not args.file:
        print("错误: 请指定要处理的文件")
        parser.print_help()
        return
    
    if not os.path.exists(args.file):
        print(f"错误: 文件 '{args.file}' 不存在")
        return
    
    if args.run:
        # 运行字节码文件
        success = run_file(args.file, args.verbose)
    elif args.compile:
        # 只编译
        success = compile_file(args.file, args.output, args.verbose)
    else:
        # 编译并运行
        success = compile_and_run(args.file, args.verbose)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()