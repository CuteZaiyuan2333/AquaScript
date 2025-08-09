# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True

"""
AquaVM Cython 加速版本
使用Cython编译为C扩展，大幅提升性能
"""

import struct
import json
from typing import List, Dict, Any, Optional
cimport cython
from libc.stdlib cimport malloc, free
from libc.string cimport memcpy

# C结构体定义
cdef struct Instruction:
    int opcode
    int operand

cdef struct CallFrame:
    int function_id
    int return_address
    int pc
    object* locals
    int locals_count

cdef class CythonAquaVM:
    """Cython优化的AquaVM"""
    
    cdef:
        list constants
        list globals
        dict functions
        dict global_vars
        dict builtins
        
        # 运行时状态
        list stack
        list call_stack
        int pc
        
        # 指令缓存
        Instruction* instructions
        int instruction_count
        
        # 性能计数器
        long long instruction_executed
    
    def __init__(self):
        self.constants = []
        self.globals = []
        self.functions = {}
        self.global_vars = {}
        self.stack = []
        self.call_stack = []
        self.pc = 0
        self.instructions = NULL
        self.instruction_count = 0
        self.instruction_executed = 0
        
        # 内置函数
        self.builtins = {
            'print': self._builtin_print,
            'str': self._builtin_str,
            'int': self._builtin_int,
            'float': self._builtin_float,
            'len': self._builtin_len,
        }
    
    def __dealloc__(self):
        if self.instructions != NULL:
            free(self.instructions)
    
    def load_bytecode(self, bytes bytecode):
        """加载字节码"""
        cdef int offset = 0
        
        # 读取文件头
        magic = bytecode[offset:offset+4]
        if magic != b'AQUA':
            raise ValueError("Invalid bytecode file")
        offset += 4
        
        version = struct.unpack('<H', bytecode[offset:offset+2])[0]
        offset += 2
        
        # 读取常量池
        constants_size = struct.unpack('<I', bytecode[offset:offset+4])[0]
        offset += 4
        constants_data = bytecode[offset:offset+constants_size]
        self.constants = json.loads(constants_data.decode('utf-8'))
        offset += constants_size
        
        # 读取全局变量表
        globals_size = struct.unpack('<I', bytecode[offset:offset+4])[0]
        offset += 4
        globals_data = bytecode[offset:offset+globals_size]
        global_vars_map = json.loads(globals_data.decode('utf-8'))
        self.globals = [None] * len(global_vars_map)
        self.global_vars = global_vars_map
        offset += globals_size
        
        # 读取函数表
        functions_size = struct.unpack('<I', bytecode[offset:offset+4])[0]
        offset += 4
        functions_data = bytecode[offset:offset+functions_size]
        self.functions = json.loads(functions_data.decode('utf-8'))
        offset += functions_size
        
        # 读取主程序指令并预编译
        main_size = struct.unpack('<I', bytecode[offset:offset+4])[0]
        offset += 4
        main_data = bytecode[offset:offset+main_size]
        instructions_list = json.loads(main_data.decode('utf-8'))
        
        # 预编译指令到C结构体
        self.instruction_count = len(instructions_list)
        self.instructions = <Instruction*>malloc(self.instruction_count * sizeof(Instruction))
        
        cdef int i
        for i in range(self.instruction_count):
            self.instructions[i].opcode = instructions_list[i][0]
            self.instructions[i].operand = instructions_list[i][1]
    
    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef void execute_fast(self):
        """快速执行循环 - C级别优化"""
        cdef int opcode, operand
        cdef object a, b, result
        cdef int i
        
        while self.pc < self.instruction_count:
            opcode = self.instructions[self.pc].opcode
            operand = self.instructions[self.pc].operand
            self.pc += 1
            self.instruction_executed += 1
            
            # 内联常用操作码处理
            if opcode == 0x01:  # LOAD_CONST
                self.stack.append(self.constants[operand])
            elif opcode == 0x02:  # LOAD_VAR
                if self.call_stack:
                    # 在函数中
                    pass  # 简化处理
                else:
                    self.stack.append(self.globals[operand])
            elif opcode == 0x03:  # STORE_VAR
                if self.call_stack:
                    pass  # 简化处理
                else:
                    self.globals[operand] = self.stack.pop()
            elif opcode == 0x10:  # ADD
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a + b)
            elif opcode == 0x11:  # SUB
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a - b)
            elif opcode == 0x12:  # MUL
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a * b)
            elif opcode == 0x13:  # DIV
                b = self.stack.pop()
                a = self.stack.pop()
                if b == 0:
                    raise ZeroDivisionError("Division by zero")
                self.stack.append(a / b)
            elif opcode == 0x50:  # CALL
                self.handle_call(operand)
            elif opcode == 0x60:  # TYPE_CHECK
                pass  # 跳过类型检查
            elif opcode == 0xFF:  # HALT
                break
            else:
                # 其他操作码的处理
                self.handle_other_opcodes(opcode, operand)
    
    cdef void handle_call(self, int argc):
        """处理函数调用"""
        cdef list args = []
        cdef int i
        
        for i in range(argc):
            args.insert(0, self.stack.pop())
        
        func = self.stack.pop()
        
        if isinstance(func, str):
            if func in self.builtins:
                result = self.builtins[func](*args)
                self.stack.append(result)
            else:
                raise NameError(f"Function '{func}' not found")
    
    cdef void handle_other_opcodes(self, int opcode, int operand):
        """处理其他操作码"""
        if opcode == 0x20:  # EQ
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a == b)
        elif opcode == 0x40:  # JUMP
            self.pc = operand
        elif opcode == 0x41:  # JUMP_IF_TRUE
            condition = self.stack.pop()
            if condition:
                self.pc = operand
        elif opcode == 0x42:  # JUMP_IF_FALSE
            condition = self.stack.pop()
            if not condition:
                self.pc = operand
        elif opcode == 0x52:  # LOAD_FUNC
            func_name = self.constants[operand]
            self.stack.append(func_name)
    
    def run(self):
        """运行虚拟机"""
        try:
            self.execute_fast()
        except Exception as e:
            print(f"Runtime error: {e}")
    
    def get_stats(self):
        """获取性能统计"""
        return {
            'instructions_executed': self.instruction_executed,
            'stack_size': len(self.stack),
            'call_stack_depth': len(self.call_stack)
        }
    
    # 内置函数
    def _builtin_print(self, *args):
        output = ' '.join(str(arg) for arg in args)
        print(output)
        return None
    
    def _builtin_str(self, obj):
        return str(obj)
    
    def _builtin_int(self, obj):
        return int(obj)
    
    def _builtin_float(self, obj):
        return float(obj)
    
    def _builtin_len(self, obj):
        return len(obj)