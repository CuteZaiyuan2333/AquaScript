#!/usr/bin/env python3
"""字节码解析工具"""

import struct
import json
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from vm.optimized_aquavm import OpCode

def parse_bytecode(filename):
    """解析字节码文件"""
    with open(filename, 'rb') as f:
        data = f.read()
    
    # 解析文件头
    if data[:4] != b'AQUA':
        raise ValueError("Invalid bytecode file")
    
    version = struct.unpack('<H', data[4:6])[0]
    print(f"Version: {version}")
    
    offset = 6
    
    # 解析常量池
    constants_size = struct.unpack('<I', data[offset:offset+4])[0]
    offset += 4
    constants_data = data[offset:offset+constants_size]
    constants = json.loads(constants_data.decode('utf-8'))
    offset += constants_size
    print(f"Constants ({len(constants)}): {constants}")
    
    # 解析全局变量表
    globals_size = struct.unpack('<I', data[offset:offset+4])[0]
    offset += 4
    globals_data = data[offset:offset+globals_size]
    global_vars = json.loads(globals_data.decode('utf-8'))
    offset += globals_size
    print(f"Global vars: {global_vars}")
    
    # 解析函数表
    functions_size = struct.unpack('<I', data[offset:offset+4])[0]
    offset += 4
    functions_data = data[offset:offset+functions_size]
    functions = json.loads(functions_data.decode('utf-8'))
    offset += functions_size
    print(f"Functions: {list(functions.keys())}")
    
    # 解析主程序指令
    main_size = struct.unpack('<I', data[offset:offset+4])[0]
    offset += 4
    main_data = data[offset:offset+main_size]
    main_instructions = json.loads(main_data.decode('utf-8'))
    
    print("\n=== Main Program Instructions ===")
    for i, (opcode_val, operand) in enumerate(main_instructions):
        opcode = OpCode(opcode_val)
        print(f"{i:3d}: {opcode.name:15} {operand}")
    
    # 解析函数指令
    for func_name, func_data in functions.items():
        print(f"\n=== Function: {func_name} ===")
        print(f"Parameters: {func_data['parameters']}")
        print(f"Local vars: {func_data['local_vars']}")
        print("Instructions:")
        for i, (opcode_val, operand) in enumerate(func_data['instructions']):
            opcode = OpCode(opcode_val)
            print(f"{i:3d}: {opcode.name:15} {operand}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python debug_bytecode.py <bytecode_file>")
        sys.exit(1)
    
    parse_bytecode(sys.argv[1])