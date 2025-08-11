"""
AquaVM 完善的Python版本
高性能、功能完整的AquaScript虚拟机

特性：
- 优化的指令执行
- 完整的全局变量初始化
- 错误处理和调试支持
- 性能统计
- 内存优化
- 扩展的内置函数库
"""

import struct
import json
import sys
import os
import time
import traceback
from typing import List, Dict, Any, Optional, Callable, Union
from enum import IntEnum
from collections import deque
import array

# 使用IntEnum提升性能
class OpCode(IntEnum):
    # 栈操作
    LOAD_CONST = 0x01      # 加载常量
    LOAD_VAR = 0x02        # 加载变量（兼容性保留）
    STORE_VAR = 0x03       # 存储变量（兼容性保留）
    LOAD_GLOBAL = 0x04     # 加载全局变量
    STORE_GLOBAL = 0x05    # 存储全局变量
    LOAD_LOCAL = 0x06      # 加载局部变量
    STORE_LOCAL = 0x07     # 存储局部变量
    POP = 0x08
    DUP = 0x09
    
    # 算术运算
    ADD = 0x10
    SUB = 0x11
    MUL = 0x12
    DIV = 0x13
    MOD = 0x14
    POW = 0x15
    
    # 比较运算
    EQ = 0x20
    NE = 0x21
    LT = 0x22
    GT = 0x23
    LE = 0x24
    GE = 0x25
    IN = 0x26              # 成员运算符
    
    # 逻辑运算
    AND = 0x30
    OR = 0x31
    NOT = 0x32
    
    # 控制流
    JUMP = 0x40
    JUMP_IF_FALSE = 0x41   # 条件跳转（假）
    JUMP_IF_TRUE = 0x42    # 条件跳转（真）
    
    # 函数操作
    CALL = 0x50
    RETURN = 0x51
    LOAD_FUNC = 0x52
    
    # 栈操作扩展
    ROT_TWO = 0x62         # 交换栈顶两个元素
    ROT_THREE = 0x63       # 旋转栈顶三个元素
    
    # 数据操作
    LEN = 0x64             # 获取长度
    GET_ITEM = 0x65        # 获取列表项
    SET_ITEM = 0x66        # 设置列表项
    BUILD_LIST = 0x67      # 构建列表
    SET_ATTR = 0x68        # 设置属性
    BUILD_DICT = 0x7A      # 构建字典
    BUILD_TUPLE = 0x6B     # 构建元组
    FORMAT_VALUE = 0x6C    # 格式化值为字符串
    
    # 迭代器操作
    GET_ITER = 0x6D        # 获取迭代器
    FOR_ITER = 0x6E        # 迭代器下一个元素
    LIST_APPEND = 0x6F     # 向列表追加元素
    
    # 模块操作
    IMPORT_MODULE = 0x6A   # 导入模块
    IMPORT_FROM = 0x69     # 从模块导入
    
    # 类型操作
    TYPE_CHECK = 0x60
    GET_ATTR = 0x70        # 获取属性
    
    # 类和对象操作
    CREATE_CLASS = 0x80    # 创建类
    CREATE_OBJECT = 0x81   # 创建对象实例
    CALL_METHOD = 0x82     # 调用方法
    
    # 其他
    HALT = 0xFF

class VMError(Exception):
    """虚拟机错误基类"""
    pass

class StackUnderflowError(VMError):
    """栈下溢错误"""
    pass

class FunctionNotFoundError(VMError):
    """函数未找到错误"""
    pass

class TypeMismatchError(VMError):
    """类型不匹配错误"""
    pass

class OptimizedAquaFunction:
    """优化的函数对象，使用__slots__减少内存占用"""
    __slots__ = ('name', 'parameters', 'instructions', 'local_vars', 'instruction_count', 'return_type')
    
    def __init__(self, name: str, parameters: List[str], instructions: List[tuple], local_vars: Dict[str, int], return_type: str = None):
        self.name = name
        self.parameters = parameters
        self.instructions = instructions
        self.local_vars = local_vars
        self.instruction_count = len(instructions)
        self.return_type = return_type

class AquaClass:
    """AquaScript类对象"""
    __slots__ = ('name', 'methods', 'attributes', 'parent')
    
    def __init__(self, name: str, methods: Dict[str, OptimizedAquaFunction] = None, attributes: Dict[str, Any] = None, parent: 'AquaClass' = None):
        self.name = name
        self.methods = methods or {}
        self.attributes = attributes or {}
        self.parent = parent
    
    def get_method(self, name: str) -> Optional[OptimizedAquaFunction]:
        """获取方法，支持继承"""
        if name in self.methods:
            return self.methods[name]
        elif self.parent:
            return self.parent.get_method(name)
        return None
    
    def has_method(self, name: str) -> bool:
        """检查是否有指定方法"""
        return self.get_method(name) is not None

class AquaObject:
    """AquaScript对象实例"""
    __slots__ = ('class_ref', 'attributes')
    
    def __init__(self, class_ref: AquaClass):
        self.class_ref = class_ref
        self.attributes = {}
        # 复制类的默认属性
        for name, value in class_ref.attributes.items():
            self.attributes[name] = value
    
    def get_attribute(self, name: str) -> Any:
        """获取属性"""
        if name in self.attributes:
            return self.attributes[name]
        elif name in self.class_ref.attributes:
            return self.class_ref.attributes[name]
        else:
            raise AttributeError(f"'{self.class_ref.name}' object has no attribute '{name}'")
    
    def set_attribute(self, name: str, value: Any):
        """设置属性"""
        self.attributes[name] = value
    
    def get_method(self, name: str) -> Optional[OptimizedAquaFunction]:
        """获取方法"""
        return self.class_ref.get_method(name)

class OptimizedCallFrame:
    """优化的调用帧，使用__slots__"""
    __slots__ = ('function', 'return_address', 'pc', 'locals')
    
    def __init__(self, function: OptimizedAquaFunction, return_address: int):
        self.function = function
        self.return_address = return_address
        self.pc = 0
        # 初始化局部变量数组，包含参数和局部变量
        total_locals = len(function.parameters) + len(function.local_vars)
        self.locals = [None] * total_locals

class VMStats:
    """虚拟机性能统计"""
    __slots__ = ('instructions_executed', 'function_calls', 'peak_stack_size', 'peak_call_depth', 'start_time', 'execution_time')
    
    def __init__(self):
        self.instructions_executed = 0
        self.function_calls = 0
        self.peak_stack_size = 0
        self.peak_call_depth = 0
        self.start_time = 0
        self.execution_time = 0
    
    def start_timing(self):
        self.start_time = time.perf_counter()
    
    def stop_timing(self):
        self.execution_time = time.perf_counter() - self.start_time
    
    def __str__(self):
        return f"""VM Statistics:
Instructions executed: {self.instructions_executed:,}
Function calls: {self.function_calls:,}
Peak stack size: {self.peak_stack_size}
Peak call depth: {self.peak_call_depth}
Execution time: {self.execution_time:.6f}s
Instructions/second: {self.instructions_executed / max(self.execution_time, 0.000001):,.0f}"""

class OptimizedAquaVM:
    """完善的AquaVM Python版本"""
    
    def __init__(self, debug_mode: bool = False, enable_stats: bool = True):
        # 基础数据
        self.constants = []
        self.global_vars = {}
        self.functions = {}
        self.classes = {}  # 存储类定义
        self.instructions = []
        
        # 运行时状态
        self.stack = []
        self.call_stack = []
        self.pc = 0
        self.globals = []
        
        # 配置选项
        self.debug_mode = debug_mode
        self.enable_stats = enable_stats
        self.stats = VMStats() if enable_stats else None
        
        # 预编译操作码映射，避免运行时查找
        self._opcode_handlers = {
            OpCode.LOAD_CONST: self._op_load_const,
            OpCode.LOAD_VAR: self._op_load_var,
            OpCode.STORE_VAR: self._op_store_var,
            OpCode.LOAD_GLOBAL: self._op_load_global,
            OpCode.STORE_GLOBAL: self._op_store_global,
            OpCode.LOAD_LOCAL: self._op_load_local,
            OpCode.STORE_LOCAL: self._op_store_local,
            OpCode.ADD: self._op_add,
            OpCode.SUB: self._op_sub,
            OpCode.MUL: self._op_mul,
            OpCode.DIV: self._op_div,
            OpCode.MOD: self._op_mod,
            OpCode.POW: self._op_pow,
            OpCode.EQ: self._op_eq,
            OpCode.NE: self._op_ne,
            OpCode.LT: self._op_lt,
            OpCode.GT: self._op_gt,
            OpCode.LE: self._op_le,
            OpCode.GE: self._op_ge,
            OpCode.IN: self._op_in,
            OpCode.AND: self._op_and,
            OpCode.OR: self._op_or,
            OpCode.NOT: self._op_not,
            OpCode.JUMP: self._op_jump,
            OpCode.JUMP_IF_TRUE: self._op_jump_if_true,
            OpCode.JUMP_IF_FALSE: self._op_jump_if_false,
            OpCode.CALL: self._op_call,
            OpCode.RETURN: self._op_return,
            OpCode.LOAD_FUNC: self._op_load_func,
            OpCode.POP: self._op_pop,
            OpCode.DUP: self._op_dup,
            OpCode.ROT_TWO: self._op_rot_two,
            OpCode.ROT_THREE: self._op_rot_three,
            OpCode.LEN: self._op_len,
            OpCode.GET_ITEM: self._op_get_item,
            OpCode.SET_ITEM: self._op_set_item,
            OpCode.BUILD_LIST: self._op_build_list,
            OpCode.BUILD_DICT: self._op_build_dict,
            OpCode.BUILD_TUPLE: self._op_build_tuple,
            OpCode.SET_ATTR: self._op_set_attr,
            OpCode.FORMAT_VALUE: self._op_format_value,
            OpCode.IMPORT_MODULE: self._op_import_module,
            OpCode.IMPORT_FROM: self._op_import_from,
            OpCode.GET_ATTR: self._op_get_attr,
            OpCode.TYPE_CHECK: self._op_type_check,
            OpCode.CREATE_CLASS: self._op_create_class,
            OpCode.CREATE_OBJECT: self._op_create_object,
            OpCode.CALL_METHOD: self._op_call_method,
            OpCode.GET_ITER: self._op_get_iter,
            OpCode.FOR_ITER: self._op_for_iter,
            OpCode.LIST_APPEND: self._op_list_append,
            OpCode.HALT: self._op_halt,
        }
        
        # 内置函数
        self.builtins = {
            'print': self._builtin_print,
            'str': self._builtin_str,
            'int': self._builtin_int,
            'float': self._builtin_float,
            'bool': self._builtin_bool,
            'len': self._builtin_len,
            'range': self._builtin_range,
            'type': self._builtin_type,
            'abs': self._builtin_abs,
            'min': self._builtin_min,
            'max': self._builtin_max,
            'sum': self._builtin_sum,
            'round': self._builtin_round,
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
        self.global_vars = global_vars_map
        self.globals = [None] * len(global_vars_map)
        offset += globals_size
        
        # 读取函数表
        functions_size = struct.unpack('<I', bytecode[offset:offset+4])[0]
        offset += 4
        functions_data = bytecode[offset:offset+functions_size]
        functions_dict = json.loads(functions_data.decode('utf-8'))
        
        for name, func_data in functions_dict.items():
            self.functions[name] = OptimizedAquaFunction(
                name=name,
                parameters=func_data['parameters'],
                instructions=func_data['instructions'],
                local_vars=func_data['local_vars'],
                return_type=func_data.get('return_type')
            )
        offset += functions_size
        
        # 读取主程序指令
        main_size = struct.unpack('<I', bytecode[offset:offset+4])[0]
        offset += 4
        main_data = bytecode[offset:offset+main_size]
        self.instructions = json.loads(main_data.decode('utf-8'))
        
        # 执行全局变量初始化
        self._initialize_globals()
    
    def _initialize_globals(self):
        """执行全局变量初始化代码"""
        if self.debug_mode:
            print("Initializing global variables...")
        
        # 执行全局变量初始化 - 运行主程序的前几条指令
        # 这些指令通常是全局变量的初始化
        saved_pc = self.pc
        self.pc = 0
        
        # 执行指令直到遇到函数定义或条件判断
        while self.pc < len(self.instructions):
            opcode_value, operand = self.instructions[self.pc]
            self.pc += 1
            
            # 如果遇到函数调用或条件跳转，停止初始化
            if opcode_value in [OpCode.CALL, OpCode.JUMP_IF_TRUE, OpCode.JUMP_IF_FALSE, OpCode.JUMP]:
                break
            
            # 执行初始化指令
            if opcode_value == OpCode.LOAD_CONST:
                self._op_load_const(operand)
            elif opcode_value == OpCode.STORE_VAR:
                self._op_store_var(operand)
                if self.debug_mode:
                    print(f"  Initialized global[{operand}] = {self.globals[operand]}")
            elif opcode_value == OpCode.LOAD_FUNC:
                self._op_load_func(operand)
            elif opcode_value == OpCode.TYPE_CHECK:
                pass  # 跳过类型检查
            else:
                # 遇到其他指令，停止初始化
                break
        
        # 恢复PC到开始位置，准备正常执行
        self.pc = 0
        self.stack.clear()  # 清空栈
        
        # 为未初始化的全局变量设置默认值
        for i in range(len(self.globals)):
            if self.globals[i] is None:
                self.globals[i] = None  # 保持None作为默认值
                if self.debug_mode:
                    print(f"  Set global[{i}] = None (default)")
    
    def run(self):
        """运行虚拟机 - 优化版本"""
        if self.enable_stats:
            self.stats.start_timing()
        
        self.pc = 0
        
        try:
            # 主执行循环 - 减少函数调用开销
            while True:
                if self.call_stack:
                    # 在函数中执行
                    frame = self.call_stack[-1]
                    if frame.pc >= frame.function.instruction_count:
                        # 函数执行完毕，自动返回None
                        self.stack.append(None)
                        self._op_return(0)
                        continue
                    
                    opcode_value, operand = frame.function.instructions[frame.pc]
                    frame.pc += 1
                else:
                    # 在主程序中执行
                    if self.pc >= len(self.instructions):
                        break
                    
                    opcode_value, operand = self.instructions[self.pc]
                    self.pc += 1
                
                # 更新统计信息
                if self.enable_stats:
                    self.stats.instructions_executed += 1
                    self.stats.peak_stack_size = max(self.stats.peak_stack_size, len(self.stack))
                    self.stats.peak_call_depth = max(self.stats.peak_call_depth, len(self.call_stack))
                
                # 调试输出
                if self.debug_mode:
                    self._debug_instruction(opcode_value, operand)
                
                # 直接调用处理函数，避免额外的分发开销
                handler = self._opcode_handlers.get(opcode_value)
                if handler:
                    handler(operand)
                else:
                    raise VMError(f"Unknown opcode: {opcode_value}")
                    
        except SystemExit:
            pass
        except Exception as e:
            print(f"Runtime error: {e}")
            if self.debug_mode:
                traceback.print_exc()
            self.print_stack_trace()
        finally:
            if self.enable_stats:
                self.stats.stop_timing()
    
    def _debug_instruction(self, opcode: int, operand: int):
        """调试输出当前指令"""
        try:
            opcode_name = OpCode(opcode).name
        except ValueError:
            opcode_name = f"UNKNOWN({opcode})"
        
        stack_preview = str(self.stack[-3:]) if len(self.stack) > 0 else "[]"
        
        # 确保operand不是None
        operand_str = str(operand) if operand is not None else "None"
        
        if self.call_stack:
            frame = self.call_stack[-1]
            print(f"[{frame.function.name}:{frame.pc-1:3d}] {opcode_name:12s} {operand_str:>3s} | Stack: {stack_preview}")
        else:
            print(f"[main:{self.pc-1:3d}] {opcode_name:12s} {operand_str:>3s} | Stack: {stack_preview}")
    
    # 操作码处理函数 - 内联优化
    def _op_load_const(self, operand):
        self.stack.append(self.constants[operand])
    
    def _op_load_var(self, operand):
        if self.call_stack:
            value = self.call_stack[-1].locals[operand]
        else:
            value = self.globals[operand]
        self.stack.append(value)
    
    def _op_store_var(self, operand):
        if not self.stack:
            raise StackUnderflowError("Cannot store variable: stack is empty")
        
        value = self.stack.pop()
        if self.call_stack:
            self.call_stack[-1].locals[operand] = value
        else:
            self.globals[operand] = value
    
    def _op_load_global(self, operand):
        """加载全局变量"""
        if operand >= len(self.globals):
            raise VMError(f"Global variable index {operand} out of range")
        value = self.globals[operand]
        self.stack.append(value)
    
    def _op_store_global(self, operand):
        """存储全局变量"""
        if not self.stack:
            raise StackUnderflowError("Cannot store global variable: stack is empty")
        
        value = self.stack.pop()
        # 扩展全局变量数组如果需要
        while len(self.globals) <= operand:
            self.globals.append(None)
        self.globals[operand] = value
    
    def _op_load_local(self, operand):
        """加载局部变量"""
        if not self.call_stack:
            raise VMError("Cannot load local variable: not in function context")
        
        frame = self.call_stack[-1]
        if operand >= len(frame.locals):
            raise VMError(f"Local variable index {operand} out of range")
        
        value = frame.locals[operand]
        self.stack.append(value)
    
    def _op_store_local(self, operand):
        """存储局部变量"""
        if not self.call_stack:
            raise VMError("Cannot store local variable: not in function context")
        
        if not self.stack:
            raise StackUnderflowError("Cannot store local variable: stack is empty")
        
        value = self.stack.pop()
        frame = self.call_stack[-1]
        
        # 扩展局部变量数组如果需要
        while len(frame.locals) <= operand:
            frame.locals.append(None)
        
        frame.locals[operand] = value
    
    def _op_add(self, operand):
        if len(self.stack) < 2:
            raise StackUnderflowError("ADD requires 2 operands")
        b = self.stack.pop()
        a = self.stack.pop()
        try:
            self.stack.append(a + b)
        except TypeError as e:
            raise TypeMismatchError(f"Cannot add {type(a).__name__} and {type(b).__name__}: {e}")
    
    def _op_sub(self, operand):
        if len(self.stack) < 2:
            raise StackUnderflowError("SUB requires 2 operands")
        b = self.stack.pop()
        a = self.stack.pop()
        try:
            self.stack.append(a - b)
        except TypeError as e:
            raise TypeMismatchError(f"Cannot subtract {type(b).__name__} from {type(a).__name__}: {e}")
    
    def _op_mul(self, operand):
        if len(self.stack) < 2:
            raise StackUnderflowError("MUL requires 2 operands")
        b = self.stack.pop()
        a = self.stack.pop()
        try:
            self.stack.append(a * b)
        except TypeError as e:
            raise TypeMismatchError(f"Cannot multiply {type(a).__name__} and {type(b).__name__}: {e}")
    
    def _op_div(self, operand):
        if len(self.stack) < 2:
            raise StackUnderflowError("DIV requires 2 operands")
        b = self.stack.pop()
        a = self.stack.pop()
        if b == 0:
            raise ZeroDivisionError("Division by zero")
        try:
            self.stack.append(a / b)
        except TypeError as e:
            raise TypeMismatchError(f"Cannot divide {type(a).__name__} by {type(b).__name__}: {e}")
    
    def _op_mod(self, operand):
        if len(self.stack) < 2:
            raise StackUnderflowError("MOD requires 2 operands")
        b = self.stack.pop()
        a = self.stack.pop()
        try:
            self.stack.append(a % b)
        except TypeError as e:
            raise TypeMismatchError(f"Cannot compute {type(a).__name__} % {type(b).__name__}: {e}")
    
    def _op_pow(self, operand):
        if len(self.stack) < 2:
            raise StackUnderflowError("POW requires 2 operands")
        b = self.stack.pop()
        a = self.stack.pop()
        try:
            self.stack.append(a ** b)
        except TypeError as e:
            raise TypeMismatchError(f"Cannot compute {type(a).__name__} ** {type(b).__name__}: {e}")
    
    def _op_eq(self, operand):
        if len(self.stack) < 2:
            raise StackUnderflowError("EQ requires 2 operands")
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(a == b)
    
    def _op_ne(self, operand):
        if len(self.stack) < 2:
            raise StackUnderflowError("NE requires 2 operands")
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(a != b)
    
    def _op_lt(self, operand):
        if len(self.stack) < 2:
            raise StackUnderflowError("LT requires 2 operands")
        b = self.stack.pop()
        a = self.stack.pop()
        try:
            self.stack.append(a < b)
        except TypeError as e:
            raise TypeMismatchError(f"Cannot compare {type(a).__name__} < {type(b).__name__}: {e}")
    
    def _op_gt(self, operand):
        if len(self.stack) < 2:
            raise StackUnderflowError("GT requires 2 operands")
        b = self.stack.pop()
        a = self.stack.pop()
        try:
            self.stack.append(a > b)
        except TypeError as e:
            raise TypeMismatchError(f"Cannot compare {type(a).__name__} > {type(b).__name__}: {e}")
    
    def _op_le(self, operand):
        if len(self.stack) < 2:
            raise StackUnderflowError("LE requires 2 operands")
        b = self.stack.pop()
        a = self.stack.pop()
        try:
            self.stack.append(a <= b)
        except TypeError as e:
            raise TypeMismatchError(f"Cannot compare {type(a).__name__} <= {type(b).__name__}: {e}")
    
    def _op_ge(self, operand):
        if len(self.stack) < 2:
            raise StackUnderflowError("GE requires 2 operands")
        b = self.stack.pop()
        a = self.stack.pop()
        try:
            self.stack.append(a >= b)
        except TypeError as e:
            raise TypeMismatchError(f"Cannot compare {type(a).__name__} >= {type(b).__name__}: {e}")
    
    def _op_in(self, operand):
        if len(self.stack) < 2:
            raise StackUnderflowError("IN requires 2 operands")
        b = self.stack.pop()  # 容器
        a = self.stack.pop()  # 要查找的元素
        try:
            self.stack.append(a in b)
        except TypeError as e:
            raise TypeMismatchError(f"Cannot check if {type(a).__name__} is in {type(b).__name__}: {e}")
    
    def _op_and(self, operand):
        if len(self.stack) < 2:
            raise StackUnderflowError("AND requires 2 operands")
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(a and b)
    
    def _op_or(self, operand):
        if len(self.stack) < 2:
            raise StackUnderflowError("OR requires 2 operands")
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(a or b)
    
    def _op_not(self, operand):
        if not self.stack:
            raise StackUnderflowError("NOT requires 1 operand")
        a = self.stack.pop()
        self.stack.append(not a)
    
    def _op_jump(self, operand):
        if self.call_stack:
            self.call_stack[-1].pc = operand
        else:
            self.pc = operand
    
    def _op_jump_if_false(self, operand):
        if not self.stack:
            raise StackUnderflowError("JUMP_IF_FALSE requires 1 operand")
        condition = self.stack.pop()
        if not condition:
            if self.call_stack:
                self.call_stack[-1].pc = operand
            else:
                self.pc = operand
    
    def _op_jump_if_true(self, operand):
        if not self.stack:
            raise StackUnderflowError("JUMP_IF_TRUE requires 1 operand")
        condition = self.stack.pop()
        if condition:
            if self.call_stack:
                self.call_stack[-1].pc = operand
            else:
                self.pc = operand
    
    def _op_call(self, operand):
        argc = operand
        
        if len(self.stack) < argc + 1:
            raise StackUnderflowError(f"CALL requires {argc + 1} operands")
        
        args = []
        for _ in range(argc):
            args.insert(0, self.stack.pop())
        
        func = self.stack.pop()
        
        if self.enable_stats:
            self.stats.function_calls += 1
        
        if isinstance(func, str):
            # 检查是否是类名
            if func in self.classes:
                # 类实例化
                class_obj = self.classes[func]
                instance = AquaObject(class_obj)
                
                # 调用构造函数（如果存在）
                if class_obj.has_method('__init__'):
                    init_method = class_obj.get_method('__init__')
                    # 将实例推入栈，这样构造函数返回后可以正确处理
                    self.stack.append(instance)
                    # 将实例作为第一个参数传递给构造函数
                    self.call_function(init_method, [instance] + args)
                else:
                    # 没有构造函数，直接返回实例
                    if args:
                        raise VMError(f"Class '{func}' has no constructor but arguments were provided")
                    self.stack.append(instance)
            elif func in self.builtins:
                try:
                    result = self.builtins[func](*args)
                    self.stack.append(result)
                except Exception as e:
                    raise VMError(f"Error in builtin function '{func}': {e}")
            elif func in self.functions:
                self.call_function(self.functions[func], args)
            else:
                raise FunctionNotFoundError(f"Function '{func}' not found")
        elif isinstance(func, AquaClass):
            # 直接使用类对象进行实例化
            instance = AquaObject(func)
            
            # 调用构造函数（如果存在）
            if func.has_method('__init__'):
                init_method = func.get_method('__init__')
                # 将实例推入栈，这样构造函数返回后可以正确处理
                self.stack.append(instance)
                # 将实例作为第一个参数传递给构造函数
                self.call_function(init_method, [instance] + args)
            else:
                # 没有构造函数，直接返回实例
                if args:
                    raise VMError(f"Class has no constructor but arguments were provided")
                self.stack.append(instance)
        else:
            raise TypeMismatchError(f"'{type(func).__name__}' object is not callable")
    
    def _op_return(self, operand):
        if not self.stack:
            raise StackUnderflowError("RETURN requires 1 operand")
        
        return_value = self.stack.pop()
        if self.call_stack:
            frame = self.call_stack.pop()
            self.pc = frame.return_address
            
            # 检查是否是构造函数返回
            if (frame.function.name.endswith('.__init__') and 
                len(self.stack) > 0 and 
                isinstance(self.stack[-1], AquaObject) and 
                return_value is None):
                # 构造函数返回None，保留栈中的实例对象
                pass
            else:
                # 普通函数返回，推入返回值
                self.stack.append(return_value)
        else:
            self.stack.append(return_value)
    
    def _op_load_func(self, operand):
        func_name = self.constants[operand]
        self.stack.append(func_name)
    
    def _op_pop(self, operand):
        if not self.stack:
            raise StackUnderflowError("POP requires 1 operand")
        self.stack.pop()
    
    def _op_dup(self, operand):
        if not self.stack:
            raise StackUnderflowError("DUP requires 1 operand")
        self.stack.append(self.stack[-1])
    
    def _op_rot_two(self, operand):
        """交换栈顶两个元素"""
        if len(self.stack) < 2:
            raise StackUnderflowError("ROT_TWO requires 2 operands")
        self.stack[-1], self.stack[-2] = self.stack[-2], self.stack[-1]
    
    def _op_rot_three(self, operand):
        """旋转栈顶三个元素 (a, b, c) -> (c, a, b)"""
        if len(self.stack) < 3:
            raise StackUnderflowError("ROT_THREE requires 3 operands")
        # 将栈顶元素移到第三个位置
        top = self.stack.pop()
        self.stack.insert(-2, top)
    
    def _op_len(self, operand):
        """获取对象长度"""
        if not self.stack:
            raise StackUnderflowError("LEN requires 1 operand")
        obj = self.stack.pop()
        try:
            length = len(obj)
            self.stack.append(length)
        except TypeError as e:
            raise TypeMismatchError(f"Object of type {type(obj).__name__} has no len(): {e}")
    
    def _op_get_item(self, operand):
        """获取列表/字典项 obj[index]"""
        if len(self.stack) < 2:
            raise StackUnderflowError("GET_ITEM requires 2 operands")
        index = self.stack.pop()
        obj = self.stack.pop()
        try:
            item = obj[index]
            self.stack.append(item)
        except (IndexError, KeyError, TypeError) as e:
            raise TypeMismatchError(f"Cannot get item from {type(obj).__name__}: {e}")
    
    def _op_get_attr(self, operand):
        """获取对象属性"""
        if not self.stack:
            raise StackUnderflowError("GET_ATTR requires 1 operand")
        obj = self.stack.pop()
        attr_name = self.constants[operand]
        try:
            if isinstance(obj, AquaObject):
                attr_value = obj.get_attribute(attr_name)
            else:
                attr_value = getattr(obj, attr_name)
            self.stack.append(attr_value)
        except AttributeError as e:
            raise TypeMismatchError(f"'{type(obj).__name__}' object has no attribute '{attr_name}': {e}")
    
    def _op_set_item(self, operand):
        """设置列表/字典项 obj[index] = value"""
        if len(self.stack) < 3:
            raise StackUnderflowError("SET_ITEM requires 3 operands")
        value = self.stack.pop()
        index = self.stack.pop()
        obj = self.stack.pop()
        try:
            obj[index] = value
        except (IndexError, KeyError, TypeError) as e:
            raise TypeMismatchError(f"Cannot set item in {type(obj).__name__}: {e}")
    
    def _op_build_list(self, operand):
        """构建列表，operand是元素个数"""
        if len(self.stack) < operand:
            raise StackUnderflowError(f"BUILD_LIST requires {operand} operands")
        
        # 从栈中弹出指定数量的元素
        elements = []
        for _ in range(operand):
            elements.append(self.stack.pop())
        
        # 由于是从栈中弹出的，需要反转顺序
        elements.reverse()
        
        # 将列表推入栈
        self.stack.append(elements)
    
    def _op_build_dict(self, operand):
        """构建字典，operand是键值对个数"""
        if len(self.stack) < operand * 2:
            raise StackUnderflowError(f"BUILD_DICT requires {operand * 2} operands")
        
        # 构建字典
        pairs = {}
        for _ in range(operand):
            value = self.stack.pop()
            key = self.stack.pop()
            pairs[key] = value
        
        # 将字典推入栈
        self.stack.append(pairs)
    
    def _op_build_tuple(self, operand):
        """构建元组，operand是元素个数"""
        if len(self.stack) < operand:
            raise StackUnderflowError(f"BUILD_TUPLE requires {operand} operands")
        
        # 从栈中弹出指定数量的元素
        elements = []
        for _ in range(operand):
            elements.append(self.stack.pop())
        
        # 由于是从栈中弹出的，需要反转顺序
        elements.reverse()
        
        # 将元组推入栈
        self.stack.append(tuple(elements))
    
    def _op_set_attr(self, operand):
        """设置对象属性"""
        if len(self.stack) < 3:
            raise StackUnderflowError("SET_ATTR requires 3 operands")
        attr_name = self.stack.pop()
        value = self.stack.pop()
        obj = self.stack.pop()
        try:
            if isinstance(obj, AquaObject):
                obj.set_attribute(attr_name, value)
            else:
                setattr(obj, attr_name, value)
        except AttributeError as e:
            raise TypeMismatchError(f"Cannot set attribute '{attr_name}' on {type(obj).__name__}: {e}")
    
    def _op_format_value(self, operand):
        """格式化值为字符串 FORMAT_VALUE"""
        if not self.stack:
            raise StackUnderflowError("FORMAT_VALUE requires 1 operand")
        
        value = self.stack.pop()
        formatted_str = str(value)
        self.stack.append(formatted_str)
    
    def _op_import_module(self, operand):

        """导入模块"""
        if not self.stack:
            raise StackUnderflowError("IMPORT_MODULE requires 1 operand")
        module_name = self.stack.pop()
        try:
            import importlib
            module = importlib.import_module(module_name)
            self.stack.append(module)
        except ImportError as e:
            raise VMError(f"Cannot import module '{module_name}': {e}")
    
    def _op_import_from(self, operand):
        """从模块导入指定项"""
        if len(self.stack) < 2:
            raise StackUnderflowError("IMPORT_FROM requires 2 operands")
        items = self.stack.pop()  # 要导入的项列表
        module_name = self.stack.pop()  # 模块名
        try:
            import importlib
            module = importlib.import_module(module_name)
            imported_items = {}
            for item in items:
                if hasattr(module, item):
                    imported_items[item] = getattr(module, item)
                else:
                    raise AttributeError(f"module '{module_name}' has no attribute '{item}'")
            self.stack.append(imported_items)
        except (ImportError, AttributeError) as e:
            raise VMError(f"Cannot import from module '{module_name}': {e}")
    
    def _op_type_check(self, operand):
        """类型检查操作"""
        # 如果操作数为None，跳过类型检查
        if operand is None:
            return
            
        if not self.stack:
            raise StackUnderflowError("TYPE_CHECK requires 1 operand")
        
        obj = self.stack[-1]  # 不弹出，只检查
        expected_type = self.constants[operand]
        
        # 类型映射
        type_map = {
            'int': int,
            'float': float,
            'str': str,
            'bool': bool,
            'list': list,
            'dict': dict,
            'NoneType': type(None)
        }
        
        if expected_type in type_map:
            if not isinstance(obj, type_map[expected_type]):
                raise TypeMismatchError(f"Expected {expected_type}, got {type(obj).__name__}")
        else:
            # 对于自定义类型，检查类型名称
            if type(obj).__name__ != expected_type:
                raise TypeMismatchError(f"Expected {expected_type}, got {type(obj).__name__}")
    
    def _op_halt(self, operand):
        raise SystemExit(0)
    
    def _op_create_class(self, operand):
        """创建类 CREATE_CLASS class_name_index"""
        class_name = self.constants[operand]
        
        # 从栈中获取方法字典
        if not self.stack:
            raise StackUnderflowError("CREATE_CLASS requires methods dict on stack")
        
        methods_dict = self.stack.pop()
        if not isinstance(methods_dict, dict):
            raise TypeMismatchError("CREATE_CLASS requires methods dict")
        
        # 将方法名转换为函数对象
        class_methods = {}
        for method_name, func_name in methods_dict.items():
            if func_name in self.functions:
                class_methods[method_name] = self.functions[func_name]
            else:
                raise FunctionNotFoundError(f"Method function '{func_name}' not found")
        
        # 创建类对象
        aqua_class = AquaClass(class_name, class_methods)
        
        # 存储类定义
        self.classes[class_name] = aqua_class
        
        # 将类对象推入栈
        self.stack.append(aqua_class)
    
    def _op_create_object(self, operand):
        """创建对象实例 CREATE_OBJECT"""
        if not self.stack:
            raise StackUnderflowError("CREATE_OBJECT requires class on stack")
        
        class_obj = self.stack.pop()
        if not isinstance(class_obj, AquaClass):
            raise TypeMismatchError("CREATE_OBJECT requires AquaClass object")
        
        # 创建对象实例
        obj_instance = AquaObject(class_obj)
        
        # 将对象实例推入栈
        self.stack.append(obj_instance)
    
    def _op_call_method(self, operand):
        """调用方法 CALL_METHOD method_name_index arg_count"""
        method_name = self.constants[operand & 0xFFFF]  # 低16位是方法名索引
        arg_count = operand >> 16  # 高16位是参数个数
        
        if len(self.stack) < arg_count + 1:
            raise StackUnderflowError(f"CALL_METHOD requires {arg_count + 1} operands")
        
        # 获取参数
        args = []
        for _ in range(arg_count):
            args.append(self.stack.pop())
        args.reverse()  # 恢复参数顺序
        
        # 获取对象
        obj = self.stack.pop()
        if not isinstance(obj, AquaObject):
            raise TypeMismatchError("CALL_METHOD requires AquaObject")
        
        # 获取方法
        method = obj.get_method(method_name)
        if method is None:
            raise FunctionNotFoundError(f"Method '{method_name}' not found in class '{obj.class_ref.name}'")
        
        # 调用方法（将self作为第一个参数）
        all_args = [obj] + args
        self.call_function(method, all_args)
    
    def _op_get_iter(self, operand):
        """获取迭代器 GET_ITER"""
        if not self.stack:
            raise StackUnderflowError("GET_ITER requires 1 operand")
        
        obj = self.stack.pop()
        
        # 创建迭代器状态：[对象, 当前索引, 长度]
        if hasattr(obj, '__iter__') or isinstance(obj, (list, tuple, str)):
            iterator_state = [obj, 0, len(obj)]
            self.stack.append(iterator_state)
        else:
            raise TypeMismatchError(f"'{type(obj).__name__}' object is not iterable")
    
    def _op_for_iter(self, operand):
        """迭代器下一个元素 FOR_ITER jump_offset"""
        if not self.stack:
            raise StackUnderflowError("FOR_ITER requires iterator on stack")
        
        iterator_state = self.stack[-1]  # 不弹出，保持在栈上
        
        if not isinstance(iterator_state, list) or len(iterator_state) != 3:
            raise TypeMismatchError("Invalid iterator state")
        
        obj, current_index, length = iterator_state
        
        # 检查是否还有元素
        if current_index >= length:
            # 迭代结束，弹出迭代器，跳转到指定位置
            self.stack.pop()
            if self.call_stack:
                self.call_stack[-1].pc = operand
            else:
                self.pc = operand
        else:
            # 获取当前元素并推入栈
            current_element = obj[current_index]
            self.stack.append(current_element)
            
            # 更新迭代器状态
            iterator_state[1] = current_index + 1
    
    def _op_list_append(self, operand):
        """向列表追加元素 LIST_APPEND"""
        if len(self.stack) < 1:
            raise StackUnderflowError("LIST_APPEND requires 1 operand")
        
        # 弹出要追加的元素
        element = self.stack.pop()
        
        # 找到列表（在迭代器下面）
        if len(self.stack) >= 2:
            # 栈从底到顶：[list, iterator]
            target_list = self.stack[-2]  # 列表在迭代器下面
            if isinstance(target_list, list):
                target_list.append(element)
            else:
                raise TypeMismatchError(f"Cannot append to {type(target_list).__name__}")
        else:
            raise StackUnderflowError("Stack underflow in LIST_APPEND")
    
    def call_function(self, function: OptimizedAquaFunction, args: List[Any]):
        """调用函数"""
        if len(args) != len(function.parameters):
            raise TypeMismatchError(f"Function '{function.name}' takes {len(function.parameters)} arguments but {len(args)} were given")
        
        return_address = self.pc
        frame = OptimizedCallFrame(function, return_address)
        
        # 设置参数
        for i, arg in enumerate(args):
            frame.locals[i] = arg
        
        self.call_stack.append(frame)
    
    def print_stack_trace(self):
        """打印调用栈"""
        print("\nCall stack:")
        if not self.call_stack:
            print("  (empty)")
            return
        
        for i, frame in enumerate(reversed(self.call_stack)):
            print(f"  {i}: {frame.function.name} at instruction {frame.pc}")
        
        print(f"\nStack contents: {self.stack}")
        print(f"Global variables: {self.globals}")
    
    def get_stats(self) -> VMStats:
        """获取性能统计"""
        return self.stats
    
    # 内置函数实现
    def _builtin_print(self, *args):
        if args:
            output = ' '.join(str(arg) for arg in args)
        else:
            output = ''
        print(output)
        return None
    
    def _builtin_str(self, obj):
        return str(obj)
    
    def _builtin_int(self, obj):
        try:
            return int(obj)
        except (ValueError, TypeError) as e:
            raise TypeMismatchError(f"Cannot convert {type(obj).__name__} to int: {e}")
    
    def _builtin_float(self, obj):
        try:
            return float(obj)
        except (ValueError, TypeError) as e:
            raise TypeMismatchError(f"Cannot convert {type(obj).__name__} to float: {e}")
    
    def _builtin_bool(self, obj):
        return bool(obj)
    
    def _builtin_len(self, obj):
        try:
            return len(obj)
        except TypeError as e:
            raise TypeMismatchError(f"Object of type {type(obj).__name__} has no len(): {e}")
    
    def _builtin_range(self, *args):
        try:
            if len(args) == 1:
                return list(range(int(args[0])))
            elif len(args) == 2:
                return list(range(int(args[0]), int(args[1])))
            elif len(args) == 3:
                return list(range(int(args[0]), int(args[1]), int(args[2])))
            else:
                raise TypeMismatchError("range() takes 1 to 3 arguments")
        except (ValueError, TypeError) as e:
            raise TypeMismatchError(f"Invalid arguments for range(): {e}")
    
    def _builtin_type(self, obj):
        return type(obj).__name__
    
    def _builtin_abs(self, obj):
        try:
            return abs(obj)
        except TypeError as e:
            raise TypeMismatchError(f"Cannot compute abs() of {type(obj).__name__}: {e}")
    
    def _builtin_min(self, *args):
        if not args:
            raise TypeMismatchError("min() requires at least 1 argument")
        try:
            return min(args)
        except TypeError as e:
            raise TypeMismatchError(f"Cannot compute min(): {e}")
    
    def _builtin_max(self, *args):
        if not args:
            raise TypeMismatchError("max() requires at least 1 argument")
        try:
            return max(args)
        except TypeError as e:
            raise TypeMismatchError(f"Cannot compute max(): {e}")
    
    def _builtin_sum(self, iterable, start=0):
        try:
            return sum(iterable, start)
        except TypeError as e:
            raise TypeMismatchError(f"Cannot compute sum(): {e}")
    
    def _builtin_round(self, number, ndigits=None):
        try:
            if ndigits is None:
                return round(number)
            else:
                return round(number, ndigits)
        except TypeError as e:
            raise TypeMismatchError(f"Cannot round {type(number).__name__}: {e}")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: python optimized_aquavm.py <bytecode_file> [--debug] [--no-stats]")
        print("Options:")
        print("  --debug     Enable debug mode")
        print("  --no-stats  Disable performance statistics")
        sys.exit(1)
    
    bytecode_file = sys.argv[1]
    debug_mode = '--debug' in sys.argv
    enable_stats = '--no-stats' not in sys.argv
    
    if not os.path.exists(bytecode_file):
        print(f"Error: File '{bytecode_file}' not found")
        sys.exit(1)
    
    vm = OptimizedAquaVM(debug_mode=debug_mode, enable_stats=enable_stats)
    
    try:
        with open(bytecode_file, 'rb') as f:
            bytecode = f.read()
        
        vm.load_bytecode(bytecode)
        vm.run()
        
        # 显示性能统计
        if enable_stats and vm.stats:
            print(f"\n{vm.stats}")
            
    except Exception as e:
        print(f"Error: {e}")
        if debug_mode:
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()