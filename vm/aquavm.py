"""
AquaVM虚拟机
负责执行.acode字节码
"""

import struct
import json
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
import sys
import os

# 导入OpCode（与codegen.py保持一致）
class OpCode(Enum):
    # 栈操作
    LOAD_CONST = 0x01      # 加载常量
    LOAD_VAR = 0x02        # 加载变量（兼容性保留）
    STORE_VAR = 0x03       # 存储变量（兼容性保留）
    LOAD_GLOBAL = 0x04     # 加载全局变量
    STORE_GLOBAL = 0x05    # 存储全局变量
    LOAD_LOCAL = 0x06      # 加载局部变量
    STORE_LOCAL = 0x07     # 存储局部变量
    POP = 0x60             # 弹出栈顶
    DUP = 0x09             # 复制栈顶
    
    # 算术运算
    ADD = 0x10             # 加法
    SUB = 0x11             # 减法
    MUL = 0x12             # 乘法
    DIV = 0x13             # 除法
    MOD = 0x14             # 取模
    POW = 0x15             # 幂运算
    
    # 比较运算
    EQ = 0x20              # 等于
    NE = 0x21              # 不等于
    LT = 0x22              # 小于
    GT = 0x23              # 大于
    LE = 0x24              # 小于等于
    GE = 0x25              # 大于等于
    IN = 0x26              # 包含检查
    
    # 逻辑运算
    AND = 0x30             # 逻辑与
    OR = 0x31              # 逻辑或
    NOT = 0x32             # 逻辑非
    
    # 控制流
    JUMP = 0x40            # 无条件跳转
    JUMP_IF_FALSE = 0x41   # 条件跳转（假）
    JUMP_IF_TRUE = 0x42    # 条件跳转（真）
    
    # 函数操作
    CALL = 0x50            # 函数调用
    RETURN = 0x51          # 返回
    LOAD_FUNC = 0x52       # 加载函数
    
    # 类型操作
    TYPE_CHECK = 0x60      # 类型检查
    TYPE_CONVERT = 0x61    # 类型转换
    
    # 栈操作扩展
    ROT_TWO = 0x62         # 交换栈顶两个元素
    ROT_THREE = 0x63       # 旋转栈顶三个元素
    
    # 数据操作
    LEN = 0x64             # 获取长度
    GET_ITEM = 0x65        # 获取列表/字典项
    SET_ITEM = 0x66        # 设置列表/字典项
    BUILD_LIST = 0x67      # 构建列表
    SET_ATTR = 0x68        # 设置属性
    IMPORT_FROM = 0x69     # 从模块导入
    IMPORT_MODULE = 0x6A   # 导入模块
    BUILD_DICT = 0x7A      # 构建字典
    BUILD_TUPLE = 0x6B     # 构建元组
    FORMAT_VALUE = 0x6C    # 格式化值为字符串
    
    # 迭代器操作
    GET_ITER = 0x6D        # 获取迭代器
    FOR_ITER = 0x6E        # 迭代器下一个元素
    LIST_APPEND = 0x6F     # 向列表追加元素
    
    # 对象操作
    GET_ATTR = 0x70        # 获取属性
    HAS_ATTR = 0x72        # 检查属性
    
    # 类和对象操作
    CREATE_CLASS = 0x80    # 创建类
    CREATE_OBJECT = 0x81   # 创建对象实例
    CALL_METHOD = 0x82     # 调用方法
    
    # 异常处理
    TRY_BEGIN = 0x90       # 开始try块
    TRY_END = 0x91         # 结束try块
    CATCH_BEGIN = 0x92     # 开始catch块
    CATCH_END = 0x93       # 结束catch块
    FINALLY_BEGIN = 0x94   # 开始finally块
    FINALLY_END = 0x95     # 结束finally块
    THROW = 0x96           # 抛出异常
    RERAISE = 0x97         # 重新抛出异常
    
    # 其他
    PRINT = 0x98           # 打印
    HALT = 0xFF            # 停机

class Instruction:
    def __init__(self, opcode: OpCode, operand: Optional[int] = None):
        self.opcode = opcode
        self.operand = operand
    
    def __repr__(self):
        return f"Instruction(opcode={self.opcode}, operand={self.operand})"

class AquaFunction:
    def __init__(self, name: str, parameters: List[str], instructions: List[Instruction], local_vars: Dict[str, int]):
        self.name = name
        self.parameters = parameters
        self.instructions = instructions
        self.local_vars = local_vars

class CallFrame:
    def __init__(self, function: AquaFunction, return_address: int):
        self.function = function
        self.return_address = return_address
        self.pc = 0  # 程序计数器
        self.locals = [None] * len(function.local_vars)  # 局部变量

class AquaException(Exception):
    """AquaScript异常基类"""
    def __init__(self, message: str, exception_type: str = "Exception"):
        super().__init__(message)
        self.message = message
        self.exception_type = exception_type
    
    def __str__(self):
        return self.message

class ExceptionHandler:
    """异常处理器"""
    def __init__(self, exception_type: Optional[str], catch_pc: int, finally_pc: Optional[int] = None):
        self.exception_type = exception_type  # None表示捕获所有异常
        self.catch_pc = catch_pc             # catch块的程序计数器
        self.finally_pc = finally_pc         # finally块的程序计数器（可选）
        self.in_function = False             # 是否在函数中

class AquaVM:
    def __init__(self):
        self.constants = []          # 常量池
        self.global_vars = {}        # 全局变量
        self.functions = {}          # 函数表
        self.instructions = []       # 主程序指令
        
        self.stack = []              # 操作数栈
        self.call_stack = []         # 调用栈
        self.pc = 0                  # 程序计数器
        self.globals = []            # 全局变量数组
        
        # 异常处理
        self.exception_stack = []    # 异常处理栈
        self.current_exception = None # 当前异常
        
        # 内置函数
        self.builtins = {
            'print': self._builtin_print,
            'str': self._builtin_str,
            'int': self._builtin_int,
            'float': self._builtin_float,
            'len': self._builtin_len,
            'range': self._builtin_range,
        }
    
    def load_bytecode(self, bytecode: bytes):
        """加载字节码文件"""
        offset = 0
        
        # 读取文件头
        magic = bytecode[offset:offset+4]
        if magic != b'AQUA':
            raise ValueError("Invalid bytecode file: wrong magic number")
        offset += 4
        
        version = struct.unpack('<H', bytecode[offset:offset+2])[0]
        if version != 1:
            raise ValueError(f"Unsupported bytecode version: {version}")
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
        functions_dict = json.loads(functions_data.decode('utf-8'))
        
        for name, func_data in functions_dict.items():
            instructions = [Instruction(OpCode(opcode), operand) for opcode, operand in func_data['instructions']]
            self.functions[name] = AquaFunction(
                name=name,
                parameters=func_data['parameters'],
                instructions=instructions,
                local_vars=func_data['local_vars']
            )
        offset += functions_size
        
        # 读取主程序指令
        main_size = struct.unpack('<I', bytecode[offset:offset+4])[0]
        offset += 4
        main_data = bytecode[offset:offset+main_size]
        instructions_data = json.loads(main_data.decode('utf-8'))
        self.instructions = [Instruction(OpCode(opcode), operand) for opcode, operand in instructions_data]
    
    def run(self):
        """运行虚拟机"""
        self.pc = 0
        
        try:
            while self.pc < len(self.instructions):
                self.execute_instruction()
        except SystemExit:
            pass
        except Exception as e:
            print(f"Runtime error: {e}")
            self.print_stack_trace()
    
    def execute_instruction(self):
        """执行单条指令"""
        if self.call_stack:
            # 在函数中执行
            frame = self.call_stack[-1]
            if frame.pc >= len(frame.function.instructions):
                return
            
            instruction = frame.function.instructions[frame.pc]
            frame.pc += 1
        else:
            # 在主程序中执行
            if self.pc >= len(self.instructions):
                return
            
            instruction = self.instructions[self.pc]
            self.pc += 1
        
        opcode = instruction.opcode
        operand = instruction.operand
        
        # 执行指令
        if opcode == OpCode.LOAD_CONST:
            self.stack.append(self.constants[operand])
        
        elif opcode == OpCode.LOAD_VAR:
            if self.call_stack:
                # 局部变量
                frame = self.call_stack[-1]
                self.stack.append(frame.locals[operand])
            else:
                # 全局变量
                self.stack.append(self.globals[operand])
        
        elif opcode == OpCode.STORE_VAR:
            value = self.stack.pop()
            if self.call_stack:
                # 局部变量
                frame = self.call_stack[-1]
                frame.locals[operand] = value
            else:
                # 全局变量
                self.globals[operand] = value
        
        elif opcode == OpCode.LOAD_GLOBAL:
            # 加载全局变量
            self.stack.append(self.globals[operand])
        
        elif opcode == OpCode.STORE_GLOBAL:
            # 存储全局变量
            value = self.stack.pop()
            self.globals[operand] = value
        
        elif opcode == OpCode.LOAD_LOCAL:
            # 加载局部变量
            if self.call_stack:
                frame = self.call_stack[-1]
                self.stack.append(frame.locals[operand])
            else:
                raise RuntimeError("LOAD_LOCAL called outside function context")
        
        elif opcode == OpCode.STORE_LOCAL:
            # 存储局部变量
            if self.call_stack:
                frame = self.call_stack[-1]
                value = self.stack.pop()
                frame.locals[operand] = value
            else:
                raise RuntimeError("STORE_LOCAL called outside function context")
        
        elif opcode == OpCode.ADD:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a + b)
        
        elif opcode == OpCode.SUB:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a - b)
        
        elif opcode == OpCode.MUL:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a * b)
        
        elif opcode == OpCode.DIV:
            b = self.stack.pop()
            a = self.stack.pop()
            if b == 0:
                raise ZeroDivisionError("Division by zero")
            self.stack.append(a / b)
        
        elif opcode == OpCode.MOD:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a % b)
        
        elif opcode == OpCode.POW:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a ** b)
        
        elif opcode == OpCode.EQ:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a == b)
        
        elif opcode == OpCode.NE:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a != b)
        
        elif opcode == OpCode.LT:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a < b)
        
        elif opcode == OpCode.GT:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a > b)
        
        elif opcode == OpCode.LE:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a <= b)
        
        elif opcode == OpCode.GE:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a >= b)
        
        elif opcode == OpCode.IN:
            b = self.stack.pop()  # 容器
            a = self.stack.pop()  # 要查找的元素
            try:
                self.stack.append(a in b)
            except TypeError as e:
                raise RuntimeError(f"Cannot check if {type(a).__name__} is in {type(b).__name__}: {e}")
        
        elif opcode == OpCode.AND:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a and b)
        
        elif opcode == OpCode.OR:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a or b)
        
        elif opcode == OpCode.NOT:
            a = self.stack.pop()
            self.stack.append(not a)
        
        elif opcode == OpCode.JUMP:
            if self.call_stack:
                self.call_stack[-1].pc = operand
            else:
                self.pc = operand
        
        elif opcode == OpCode.JUMP_IF_FALSE:
            condition = self.stack.pop()
            if not condition:
                if self.call_stack:
                    self.call_stack[-1].pc = operand
                else:
                    self.pc = operand
        
        elif opcode == OpCode.JUMP_IF_TRUE:
            condition = self.stack.pop()
            if condition:
                if self.call_stack:
                    self.call_stack[-1].pc = operand
                else:
                    self.pc = operand
        
        elif opcode == OpCode.CALL:
            argc = operand
            args = []
            for _ in range(argc):
                args.insert(0, self.stack.pop())
            
            func = self.stack.pop()
            
            if isinstance(func, str):
                # 内置函数或用户定义函数
                if func in self.builtins:
                    result = self.builtins[func](*args)
                    self.stack.append(result)
                elif func in self.functions:
                    self.call_function(self.functions[func], args)
                else:
                    raise NameError(f"Function '{func}' not found")
            else:
                raise TypeError(f"'{type(func).__name__}' object is not callable")
        
        elif opcode == OpCode.RETURN:
            return_value = self.stack.pop()
            if self.call_stack:
                frame = self.call_stack.pop()
                self.pc = frame.return_address
            self.stack.append(return_value)
        
        elif opcode == OpCode.LOAD_FUNC:
            func_name = self.constants[operand]
            self.stack.append(func_name)
        
        elif opcode == OpCode.POP:
            self.stack.pop()
        
        elif opcode == OpCode.DUP:
            self.stack.append(self.stack[-1])
        
        elif opcode == OpCode.HALT:
            raise SystemExit(0)
        
        elif opcode == OpCode.TYPE_CHECK:
            # 类型检查操作码 - 暂时跳过，不做实际检查
            pass
        
        elif opcode == OpCode.TRY_BEGIN:
            # 开始try块 - 记录异常处理器
            # 查找对应的CATCH_BEGIN指令位置
            catch_pc = self._find_catch_block()
            handler = ExceptionHandler(None, catch_pc)
            handler.in_function = bool(self.call_stack)
            self.exception_stack.append(handler)
        
        elif opcode == OpCode.TRY_END:
            # 结束try块 - 如果没有异常，跳过catch块
            if not self.current_exception:
                # 跳过所有catch块，找到catch块结束位置
                self._skip_catch_blocks()
        
        elif opcode == OpCode.CATCH_BEGIN:
            # 开始catch块 - 只有在有异常时才执行
            if not self.current_exception:
                # 如果没有异常，跳过这个catch块
                self._skip_current_catch_block()
                return
            
            # 检查异常类型是否匹配
            if operand is not None:
                exception_type = self.constants[operand]
                if self.current_exception.exception_type != exception_type:
                    # 类型不匹配，跳过这个catch块
                    self._skip_current_catch_block()
                    return
            
            # 异常匹配，将异常对象压入栈供catch块使用
            self.stack.append(self.current_exception)
        
        elif opcode == OpCode.CATCH_END:
            # 结束catch块
            if self.exception_stack:
                self.exception_stack.pop()
            self.current_exception = None
        
        elif opcode == OpCode.FINALLY_BEGIN:
            # 开始finally块
            if self.exception_stack:
                handler = self.exception_stack[-1]
                if self.call_stack:
                    handler.finally_pc = self.call_stack[-1].pc
                else:
                    handler.finally_pc = self.pc
        
        elif opcode == OpCode.FINALLY_END:
            # 结束finally块
            if self.current_exception:
                # 如果有未处理的异常，重新抛出
                self._handle_exception(self.current_exception)
        
        elif opcode == OpCode.THROW:
            # 抛出异常
            exception_obj = self.stack.pop()
            if isinstance(exception_obj, str):
                exception = AquaException(exception_obj)
            else:
                exception = AquaException(str(exception_obj))
            self._handle_exception(exception)
        
        elif opcode == OpCode.RERAISE:
            # 重新抛出当前异常
            if self.current_exception:
                self._handle_exception(self.current_exception)
            else:
                raise RuntimeError("No active exception to reraise")
        
        elif opcode == OpCode.BUILD_LIST:
            # 构建列表，operand是元素个数
            elements = []
            for _ in range(operand):
                elements.insert(0, self.stack.pop())
            self.stack.append(elements)
        
        elif opcode == OpCode.BUILD_DICT:
            # 构建字典，operand是键值对个数
            pairs = {}
            for _ in range(operand):
                value = self.stack.pop()
                key = self.stack.pop()
                pairs[key] = value
            self.stack.append(pairs)
        
        elif opcode == OpCode.BUILD_TUPLE:
            # 构建元组，operand是元素个数
            elements = []
            for _ in range(operand):
                elements.insert(0, self.stack.pop())
            self.stack.append(tuple(elements))
        
        elif opcode == OpCode.FORMAT_VALUE:
            # 格式化值为字符串
            value = self.stack.pop()
            formatted = str(value)
            self.stack.append(formatted)
        
        elif opcode == OpCode.GET_ITEM:
            # 获取列表/字典项 obj[index]
            index = self.stack.pop()
            obj = self.stack.pop()
            try:
                item = obj[index]
                self.stack.append(item)
            except (IndexError, KeyError, TypeError) as e:
                raise RuntimeError(f"Cannot get item from {type(obj).__name__}: {e}")
        
        elif opcode == OpCode.SET_ITEM:
            # 设置列表/字典项 obj[index] = value
            value = self.stack.pop()
            index = self.stack.pop()
            obj = self.stack.pop()
            try:
                obj[index] = value
            except (IndexError, KeyError, TypeError) as e:
                raise RuntimeError(f"Cannot set item in {type(obj).__name__}: {e}")
        
        elif opcode == OpCode.GET_ITER:
            # 获取迭代器
            iterable = self.stack.pop()
            try:
                iterator = iter(iterable)
                self.stack.append(iterator)
            except TypeError:
                raise RuntimeError(f"'{type(iterable).__name__}' object is not iterable")
        
        elif opcode == OpCode.FOR_ITER:
            # 迭代器下一个元素
            iterator = self.stack[-1]  # 保持迭代器在栈上
            try:
                next_value = next(iterator)
                self.stack.append(next_value)
            except StopIteration:
                # 迭代结束，跳转到循环结束位置
                self.stack.pop()  # 移除迭代器
                if self.call_stack:
                    self.call_stack[-1].pc = operand
                else:
                    self.pc = operand
        
        elif opcode == OpCode.LIST_APPEND:
            # 向列表追加元素
            # 栈布局：[list, iterator, element] -> [list, iterator]
            element = self.stack.pop()
            # 找到列表（在迭代器下面）
            if len(self.stack) >= 2:
                # 栈从底到顶：[list, iterator]
                list_obj = self.stack[-2]  # 列表在迭代器下面
                if isinstance(list_obj, list):
                    list_obj.append(element)
                else:
                    raise RuntimeError(f"Cannot append to {type(list_obj).__name__}")
            else:
                raise RuntimeError("Stack underflow in LIST_APPEND")
        
        elif opcode == OpCode.LEN:
            # 获取长度
            obj = self.stack.pop()
            try:
                length = len(obj)
                self.stack.append(length)
            except TypeError as e:
                raise RuntimeError(f"Object of type {type(obj).__name__} has no len(): {e}")
        
        elif opcode == OpCode.ROT_TWO:
            # 交换栈顶两个元素
            if len(self.stack) < 2:
                raise RuntimeError("ROT_TWO requires 2 operands")
            a = self.stack.pop()
            b = self.stack.pop()
            self.stack.append(a)
            self.stack.append(b)
        
        elif opcode == OpCode.ROT_THREE:
            # 旋转栈顶三个元素 (a, b, c) -> (c, a, b)
            if len(self.stack) < 3:
                raise RuntimeError("Stack underflow: ROT_THREE requires at least 3 elements")
            c = self.stack.pop()
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(c)
            self.stack.append(a)
            self.stack.append(b)
        
        elif opcode == OpCode.IMPORT_MODULE:
            # 导入模块
            if not self.stack:
                raise RuntimeError("IMPORT_MODULE requires 1 operand")
            module_name = self.stack.pop()
            try:
                import importlib
                module = importlib.import_module(module_name)
                self.stack.append(module)
            except ImportError as e:
                raise RuntimeError(f"Cannot import module '{module_name}': {e}")
        
        elif opcode == OpCode.IMPORT_FROM:
            # 从模块导入指定项
            if len(self.stack) < 2:
                raise RuntimeError("IMPORT_FROM requires 2 operands")
            items = self.stack.pop()  # 要导入的项列表
            module_name = self.stack.pop()  # 模块名
            try:
                import importlib
                module = importlib.import_module(module_name)
                # 按照导入顺序将每个项推入栈中（逆序推入，因为后续会逆序弹出）
                for item in reversed(items):
                    if hasattr(module, item):
                        self.stack.append(getattr(module, item))
                    else:
                        raise AttributeError(f"module '{module_name}' has no attribute '{item}'")
            except (ImportError, AttributeError) as e:
                raise RuntimeError(f"Cannot import from module '{module_name}': {e}")
        
        else:
            raise ValueError(f"Unknown opcode: {opcode}")
    
    def call_function(self, function: AquaFunction, args: List[Any]):
        """调用函数"""
        if len(args) != len(function.parameters):
            raise TypeError(f"Function '{function.name}' takes {len(function.parameters)} arguments but {len(args)} were given")
        
        # 创建调用帧
        return_address = self.pc
        frame = CallFrame(function, return_address)
        
        # 设置参数
        for i, arg in enumerate(args):
            frame.locals[i] = arg
        
        self.call_stack.append(frame)
    
    def print_stack_trace(self):
        """打印调用栈"""
        print("Call stack:")
        for i, frame in enumerate(reversed(self.call_stack)):
            print(f"  {i}: {frame.function.name} at instruction {frame.pc}")
    
    def _find_catch_block(self):
        """查找对应的CATCH_BEGIN指令位置"""
        instructions = self.instructions if not self.call_stack else self.call_stack[-1].function.instructions
        pc = self.pc if not self.call_stack else self.call_stack[-1].pc
        
        # 从当前位置开始查找CATCH_BEGIN
        for i in range(pc + 1, len(instructions)):
            if instructions[i].opcode == OpCode.CATCH_BEGIN:
                return i
        return -1
    
    def _skip_catch_blocks(self):
        """跳过所有catch块"""
        instructions = self.instructions if not self.call_stack else self.call_stack[-1].function.instructions
        catch_depth = 0
        
        while True:
            if self.call_stack:
                if self.call_stack[-1].pc >= len(instructions):
                    break
                instr = instructions[self.call_stack[-1].pc]
                self.call_stack[-1].pc += 1
            else:
                if self.pc >= len(instructions):
                    break
                instr = instructions[self.pc]
                self.pc += 1
            
            if instr.opcode == OpCode.CATCH_BEGIN:
                catch_depth += 1
            elif instr.opcode == OpCode.CATCH_END:
                catch_depth -= 1
                if catch_depth == 0:
                    break
    
    def _skip_current_catch_block(self):
        """跳过当前catch块"""
        instructions = self.instructions if not self.call_stack else self.call_stack[-1].function.instructions
        
        while True:
            if self.call_stack:
                if self.call_stack[-1].pc >= len(instructions):
                    break
                instr = instructions[self.call_stack[-1].pc]
                self.call_stack[-1].pc += 1
            else:
                if self.pc >= len(instructions):
                    break
                instr = instructions[self.pc]
                self.pc += 1
            
            if instr.opcode == OpCode.CATCH_END:
                break
    
    def _handle_exception(self, exception: AquaException):
        """处理异常"""
        self.current_exception = exception
        
        # 查找合适的异常处理器
        while self.exception_stack:
            handler = self.exception_stack[-1]
            
            # 跳转到catch块
            if handler.catch_pc != -1:
                if handler.in_function and self.call_stack:
                    self.call_stack[-1].pc = handler.catch_pc
                else:
                    self.pc = handler.catch_pc
                return
            
            # 如果没有找到处理器，继续向上查找
            self.exception_stack.pop()
        
        # 没有找到处理器，抛出Python异常
        raise exception
    
    # 内置函数实现
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
    
    def _builtin_range(self, *args):
        if len(args) == 1:
            return list(range(args[0]))
        elif len(args) == 2:
            return list(range(args[0], args[1]))
        elif len(args) == 3:
            return list(range(args[0], args[1], args[2]))
        else:
            raise TypeError("range() takes 1 to 3 arguments")

def main():
    if len(sys.argv) != 2:
        print("Usage: python aquavm.py <bytecode_file>")
        sys.exit(1)
    
    bytecode_file = sys.argv[1]
    
    if not os.path.exists(bytecode_file):
        print(f"Error: File '{bytecode_file}' not found")
        sys.exit(1)
    
    # 加载并运行字节码
    vm = AquaVM()
    
    with open(bytecode_file, 'rb') as f:
        bytecode = f.read()
    
    vm.load_bytecode(bytecode)
    vm.run()

if __name__ == "__main__":
    main()