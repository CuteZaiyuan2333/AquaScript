"""
AquaScript字节码生成器
负责将AST转换为.acode字节码
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import struct
import json
import sys
import os

# 添加vm目录到路径以导入OpCode
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'vm'))
from aquavm import OpCode

from parser import *

@dataclass
class Instruction:
    opcode: OpCode
    operand: Optional[int] = None

@dataclass
class Function:
    name: str
    parameters: List[str]
    instructions: List[Instruction]
    local_vars: Dict[str, int]

class CodeGenerator:
    def __init__(self):
        self.constants = []          # 常量池
        self.functions = {}          # 函数表
        self.global_vars = {}        # 全局变量表
        self.instructions = []       # 主程序指令
        self.current_function = None # 当前编译的函数
        
        # 用于控制流的标签
        self.label_counter = 0
        self.break_labels = []
        self.continue_labels = []
    
    def add_constant(self, value: Any) -> int:
        """添加常量到常量池，返回索引"""
        if value in self.constants:
            return self.constants.index(value)
        self.constants.append(value)
        return len(self.constants) - 1
    
    def new_label(self) -> str:
        """生成新的标签"""
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label
    
    def emit(self, opcode: OpCode, operand: Optional[int] = None):
        """发射指令"""
        instruction = Instruction(opcode, operand)
        if self.current_function:
            self.current_function.instructions.append(instruction)
        else:
            self.instructions.append(instruction)
    
    def generate(self, ast: Program) -> bytes:
        """生成字节码"""
        # 编译所有语句
        for stmt in ast.statements:
            self.compile_statement(stmt)
        
        # 添加停机指令
        self.emit(OpCode.HALT)
        
        # 生成字节码文件
        return self.serialize_bytecode()
    
    def compile_statement(self, stmt: Statement):
        """编译语句"""
        if isinstance(stmt, ExpressionStatement):
            self.compile_expression(stmt.expression)
            self.emit(OpCode.POP)  # 丢弃表达式结果
        
        elif isinstance(stmt, Assignment):
            self.compile_expression(stmt.value)
            if self.current_function:
                # 在函数内部，首先检查是否是已存在的全局变量
                if stmt.target in self.global_vars:
                    # 如果是已存在的全局变量，使用STORE_GLOBAL
                    var_index = self.global_vars[stmt.target]
                    self.emit(OpCode.STORE_GLOBAL, var_index)
                else:
                    # 否则创建或使用局部变量
                    var_index = self.get_or_create_local_var(stmt.target)
                    self.emit(OpCode.STORE_LOCAL, var_index)
            else:
                # 在全局作用域
                var_index = self.get_or_create_global_var(stmt.target)
                self.emit(OpCode.STORE_GLOBAL, var_index)
        
        elif isinstance(stmt, AttributeAssignment):
            # 编译对象表达式
            self.compile_expression(stmt.object)
            # 编译赋值的值
            self.compile_expression(stmt.value)
            # 加载属性名
            attr_index = self.add_constant(stmt.attribute)
            self.emit(OpCode.LOAD_CONST, attr_index)
            # 设置属性
            self.emit(OpCode.SET_ATTR)
        
        elif isinstance(stmt, IndexAssignment):
            # 编译对象表达式
            self.compile_expression(stmt.object)
            # 编译索引表达式
            self.compile_expression(stmt.index)
            # 编译赋值的值
            self.compile_expression(stmt.value)
            # 设置列表项
            self.emit(OpCode.SET_ITEM)
        
        elif isinstance(stmt, FunctionDef):
            self.compile_function_def(stmt)
        
        elif isinstance(stmt, IfStatement):
            self.compile_if_statement(stmt)
        
        elif isinstance(stmt, ForLoop):
            self.compile_for_loop(stmt)
        
        elif isinstance(stmt, WhileLoop):
            self.compile_while_loop(stmt)
        
        elif isinstance(stmt, ReturnStatement):
            if stmt.value:
                self.compile_expression(stmt.value)
            else:
                const_index = self.add_constant(None)
                self.emit(OpCode.LOAD_CONST, const_index)
            self.emit(OpCode.RETURN)
        
        elif isinstance(stmt, BreakStatement):
            if self.break_labels:
                # 这里需要在后续处理中解析标签
                self.emit(OpCode.JUMP, -1)  # 占位符
        
        elif isinstance(stmt, ContinueStatement):
            if self.continue_labels:
                # 这里需要在后续处理中解析标签
                self.emit(OpCode.JUMP, -1)  # 占位符
        
        elif hasattr(stmt, '__class__') and stmt.__class__.__name__ == 'VarDeclaration':
            self.compile_var_declaration(stmt)
        
        elif hasattr(stmt, '__class__') and stmt.__class__.__name__ == 'ClassDef':
            self.compile_class_def(stmt)
        
        elif hasattr(stmt, '__class__') and stmt.__class__.__name__ == 'RepeatLoop':
            self.compile_repeat_loop(stmt)
        
        elif hasattr(stmt, '__class__') and stmt.__class__.__name__ == 'SwitchStatement':
            self.compile_switch_statement(stmt)
        
        elif hasattr(stmt, '__class__') and stmt.__class__.__name__ == 'ImportStatement':
            self.compile_import_statement(stmt)
        
        elif isinstance(stmt, TryStatement):
            self.compile_try_statement(stmt)
        
        elif isinstance(stmt, ThrowStatement):
            self.compile_throw_statement(stmt)
    
    def compile_expression(self, expr: Expression):
        """编译表达式"""
        if isinstance(expr, NumberLiteral):
            const_index = self.add_constant(expr.value)
            self.emit(OpCode.LOAD_CONST, const_index)
        
        elif isinstance(expr, StringLiteral):
            const_index = self.add_constant(expr.value)
            self.emit(OpCode.LOAD_CONST, const_index)
        
        elif isinstance(expr, FStringLiteral):
            # 编译f-string的各个部分
            for part in expr.parts:
                if part['type'] == 'text':
                    # 文本部分直接作为字符串常量
                    const_index = self.add_constant(part['value'])
                    self.emit(OpCode.LOAD_CONST, const_index)
                elif part['type'] == 'expression':
                    # 表达式部分需要解析并编译
                    from parser import Parser
                    from lexer import Lexer
                    
                    # 解析表达式
                    lexer = Lexer(part['value'])
                    tokens = lexer.tokenize()
                    parser = Parser(tokens)
                    expr_ast = parser.parse_expression()
                    
                    # 编译表达式
                    self.compile_expression(expr_ast)
                    
                    # 将结果转换为字符串 - 使用FORMAT_VALUE指令
                    self.emit(OpCode.FORMAT_VALUE)
            
            # 连接所有部分
            if len(expr.parts) > 1:
                for i in range(len(expr.parts) - 1):
                    self.emit(OpCode.ADD)
        
        elif isinstance(expr, BooleanLiteral):
            const_index = self.add_constant(expr.value)
            self.emit(OpCode.LOAD_CONST, const_index)
        
        elif isinstance(expr, NoneLiteral):
            const_index = self.add_constant(None)
            self.emit(OpCode.LOAD_CONST, const_index)
        
        elif isinstance(expr, Identifier):
            if self.current_function:
                # 在函数内部，检查是否是局部变量（包括参数）
                if expr.name in self.current_function.local_vars:
                    var_index = self.current_function.local_vars[expr.name]
                    self.emit(OpCode.LOAD_LOCAL, var_index)
                else:
                    # 不是局部变量，尝试作为全局变量
                    var_index = self.get_or_create_global_var(expr.name)
                    self.emit(OpCode.LOAD_GLOBAL, var_index)
            else:
                # 在全局作用域
                var_index = self.get_or_create_global_var(expr.name)
                self.emit(OpCode.LOAD_GLOBAL, var_index)
        
        elif isinstance(expr, BinaryOperation):
            self.compile_expression(expr.left)
            self.compile_expression(expr.right)
            
            op_map = {
                '+': OpCode.ADD,
                '-': OpCode.SUB,
                '*': OpCode.MUL,
                '/': OpCode.DIV,
                '%': OpCode.MOD,
                '**': OpCode.POW,
                '==': OpCode.EQ,
                '!=': OpCode.NE,
                '<': OpCode.LT,
                '>': OpCode.GT,
                '<=': OpCode.LE,
                    '>=': OpCode.GE,
                    'in': OpCode.IN,
                    'and': OpCode.AND,
                    'or': OpCode.OR,
            }
            
            if expr.operator in op_map:
                self.emit(op_map[expr.operator])
            else:
                raise ValueError(f"Unknown binary operator: {expr.operator}")
        
        elif isinstance(expr, UnaryOperation):
            if expr.operator == 'not':
                self.compile_expression(expr.operand)
                self.emit(OpCode.NOT)
            elif expr.operator == '-':
                # 负号：0 - operand
                const_index = self.add_constant(0)
                self.emit(OpCode.LOAD_CONST, const_index)
                self.compile_expression(expr.operand)
                self.emit(OpCode.SUB)
            elif expr.operator == '+':
                # 正号：直接编译操作数
                self.compile_expression(expr.operand)
            else:
                raise ValueError(f"Unknown unary operator: {expr.operator}")
        
        elif isinstance(expr, FunctionCall):
            # 检查是否是方法调用
            if isinstance(expr.function, AttributeAccess):
                # 方法调用：obj.method(args)
                # 编译对象表达式
                self.compile_expression(expr.function.object)
                
                # 编译参数
                for arg in expr.arguments:
                    self.compile_expression(arg)
                
                # 调用方法
                method_name_index = self.add_constant(expr.function.attribute)
                # 将参数个数编码到操作数的高16位，方法名索引到低16位
                operand = (len(expr.arguments) << 16) | method_name_index
                self.emit(OpCode.CALL_METHOD, operand)
            
            elif isinstance(expr.function, Identifier):
                # 可能是类实例化或普通函数调用
                # 先加载函数/类名
                if self.current_function:
                    # 在函数内部，检查是否是局部变量
                    if expr.function.name in self.current_function.local_vars:
                        var_index = self.current_function.local_vars[expr.function.name]
                        self.emit(OpCode.LOAD_LOCAL, var_index)
                    elif expr.function.name in self.global_vars:
                        var_index = self.global_vars[expr.function.name]
                        self.emit(OpCode.LOAD_GLOBAL, var_index)
                    else:
                        # 假设是函数名
                        func_name_index = self.add_constant(expr.function.name)
                        self.emit(OpCode.LOAD_CONST, func_name_index)
                else:
                    # 在全局作用域
                    if expr.function.name in self.global_vars:
                        var_index = self.global_vars[expr.function.name]
                        self.emit(OpCode.LOAD_GLOBAL, var_index)
                    else:
                        # 假设是函数名
                        func_name_index = self.add_constant(expr.function.name)
                        self.emit(OpCode.LOAD_CONST, func_name_index)
                
                # 然后编译参数
                for arg in expr.arguments:
                    self.compile_expression(arg)
                
                # 调用函数（可能是类构造函数）
                self.emit(OpCode.CALL, len(expr.arguments))
            
            else:
                # 对于其他表达式，正常编译
                self.compile_expression(expr.function)
                
                # 编译参数
                for arg in expr.arguments:
                    self.compile_expression(arg)
                
                # 调用函数
                self.emit(OpCode.CALL, len(expr.arguments))
        
        elif isinstance(expr, ListLiteral):
            # 编译列表中的每个元素
            for element in expr.elements:
                self.compile_expression(element)
            # 创建列表，操作数是元素个数
            self.emit(OpCode.BUILD_LIST, len(expr.elements))
        
        elif isinstance(expr, DictLiteral):
            # 编译字典中的每个键值对
            for key, value in expr.pairs:
                self.compile_expression(key)
                self.compile_expression(value)
            # 创建字典，操作数是键值对个数
            self.emit(OpCode.BUILD_DICT, len(expr.pairs))
        
        elif isinstance(expr, TupleLiteral):
            # 编译元组中的每个元素
            for element in expr.elements:
                self.compile_expression(element)
            # 创建元组，操作数是元素个数
            self.emit(OpCode.BUILD_TUPLE, len(expr.elements))
        
        elif isinstance(expr, ListComprehension):
            # 编译列表推导式: [element for variable in iterable if condition]
            # 创建空列表
            self.emit(OpCode.BUILD_LIST, 0)
            
            # 编译迭代对象
            self.compile_expression(expr.iterable)
            
            # 获取迭代器
            self.emit(OpCode.GET_ITER)
            
            # 循环开始位置
            loop_start = len(self.get_current_instructions())
            
            # 尝试获取下一个元素
            for_iter_index = len(self.get_current_instructions())
            self.emit(OpCode.FOR_ITER, 0)  # 占位符，稍后回填
            
            # 将迭代变量存储到局部变量
            if self.current_function:
                var_index = self.get_or_create_local_var(expr.variable)
                self.emit(OpCode.STORE_LOCAL, var_index)
            else:
                var_index = self.get_or_create_global_var(expr.variable)
                self.emit(OpCode.STORE_GLOBAL, var_index)
            
            # 如果有条件，编译条件表达式
            skip_jump_index = None
            if expr.condition:
                self.compile_expression(expr.condition)
                # 如果条件为假，跳过这次迭代
                skip_jump_index = len(self.get_current_instructions())
                self.emit(OpCode.JUMP_IF_FALSE, 0)  # 占位符，稍后回填
            
            # 编译元素表达式
            self.compile_expression(expr.element)
            
            # 将元素添加到列表
            self.emit(OpCode.LIST_APPEND)
            
            # 如果有条件，回填跳过跳转的目标
            if skip_jump_index is not None:
                current_instructions = self.get_current_instructions()
                current_instructions[skip_jump_index].operand = len(current_instructions)
            
            # 跳回循环开始
            self.emit(OpCode.JUMP, loop_start)
            
            # 回填FOR_ITER的跳转目标（循环结束位置）
            current_instructions = self.get_current_instructions()
            current_instructions[for_iter_index].operand = len(current_instructions)
        
        elif isinstance(expr, AttributeAccess):
            # 编译对象表达式
            self.compile_expression(expr.object)
            # 获取属性，直接传递属性名索引作为操作数
            attr_index = self.add_constant(expr.attribute)
            self.emit(OpCode.GET_ATTR, attr_index)
        
        elif isinstance(expr, IndexAccess):
            # 编译对象表达式
            self.compile_expression(expr.object)
            # 编译索引表达式
            self.compile_expression(expr.index)
            # 获取列表项
            self.emit(OpCode.GET_ITEM)
    
    def compile_function_def(self, func_def: FunctionDef):
        """编译函数定义"""
        # 保存当前状态
        old_function = self.current_function
        
        # 创建新函数
        function = Function(
            name=func_def.name,
            parameters=func_def.parameters,
            instructions=[],
            local_vars={}
        )
        
        self.current_function = function
        
        # 将参数添加到局部变量表中，确保它们有正确的索引
        for i, param in enumerate(func_def.parameters):
            function.local_vars[param] = i
        
        # 编译函数体
        for stmt in func_def.body:
            self.compile_statement(stmt)
        
        # 如果函数没有显式返回，添加返回None
        if not function.instructions or function.instructions[-1].opcode != OpCode.RETURN:
            const_index = self.add_constant(None)
            self.emit(OpCode.LOAD_CONST, const_index)
            self.emit(OpCode.RETURN)
        
        # 保存函数
        self.functions[func_def.name] = function
        
        # 恢复状态
        self.current_function = old_function
        
        # 在主程序中加载函数
        func_index = self.add_constant(func_def.name)
        self.emit(OpCode.LOAD_FUNC, func_index)
        
        # 根据上下文存储函数
        if self.current_function:
            var_index = self.get_or_create_local_var(func_def.name)
            self.emit(OpCode.STORE_LOCAL, var_index)
        else:
            var_index = self.get_or_create_global_var(func_def.name)
            self.emit(OpCode.STORE_GLOBAL, var_index)
    
    def compile_var_declaration(self, var_decl):
        """编译变量声明"""
        # 生成初始值
        if var_decl.value:
            self.compile_expression(var_decl.value)
        else:
            # 默认值根据类型决定
            if var_decl.type_hint == 'int':
                const_index = self.add_constant(0)
            elif var_decl.type_hint == 'float':
                const_index = self.add_constant(0.0)
            elif var_decl.type_hint == 'str':
                const_index = self.add_constant("")
            elif var_decl.type_hint == 'bool':
                const_index = self.add_constant(False)
            else:
                const_index = self.add_constant(None)
            self.emit(OpCode.LOAD_CONST, const_index)
        
        # 根据上下文存储变量
        if self.current_function:
            var_index = self.get_or_create_local_var(var_decl.name)
            self.emit(OpCode.STORE_LOCAL, var_index)
        else:
            var_index = self.get_or_create_global_var(var_decl.name)
            self.emit(OpCode.STORE_GLOBAL, var_index)
    
    def compile_class_def(self, class_def):
        """编译类定义"""
        # 创建类字典来存储方法名
        class_methods = {}
        
        # 编译类体中的方法
        for stmt in class_def.body:
            if isinstance(stmt, FunctionDef):
                # 编译方法
                old_function = self.current_function
                
                # 创建方法函数对象
                method_func = Function(
                    name=f"{class_def.name}.{stmt.name}",
                    parameters=stmt.parameters,
                    instructions=[],
                    local_vars={}
                )
                
                self.current_function = method_func
                
                # 将参数添加到局部变量表中
                for i, param in enumerate(stmt.parameters):
                    method_func.local_vars[param] = i
                
                # 编译方法体
                for body_stmt in stmt.body:
                    self.compile_statement(body_stmt)
                
                # 确保方法有返回值
                if not method_func.instructions or method_func.instructions[-1].opcode != OpCode.RETURN:
                    none_index = self.add_constant(None)
                    self.emit(OpCode.LOAD_CONST, none_index)
                    self.emit(OpCode.RETURN)
                
                # 保存方法函数
                self.functions[method_func.name] = method_func
                
                # 恢复状态
                self.current_function = old_function
                
                # 将方法名添加到类方法字典（而不是函数对象）
                class_methods[stmt.name] = method_func.name
        
        # 将方法字典推入栈
        methods_index = self.add_constant(class_methods)
        self.emit(OpCode.LOAD_CONST, methods_index)
        
        # 创建类
        class_name_index = self.add_constant(class_def.name)
        self.emit(OpCode.CREATE_CLASS, class_name_index)
        
        # 存储类到变量
        if self.current_function:
            var_index = self.get_or_create_local_var(class_def.name)
            self.emit(OpCode.STORE_LOCAL, var_index)
        else:
            var_index = self.get_or_create_global_var(class_def.name)
            self.emit(OpCode.STORE_GLOBAL, var_index)
    
    def compile_repeat_loop(self, repeat_stmt):
        """编译repeat循环"""
        # repeat循环等价于do-while循环
        loop_start = len(self.get_current_instructions())
        
        # 生成循环体
        for stmt in repeat_stmt.body:
            self.compile_statement(stmt)
        
        # 生成条件检查
        self.compile_expression(repeat_stmt.condition)
        
        # 如果条件为真，跳回循环开始
        self.emit(OpCode.JUMP_IF_TRUE, loop_start)
    
    def compile_switch_statement(self, switch_stmt):
        """编译switch语句"""
        # switch语句转换为一系列if-elif语句
        end_labels = []
        
        # 生成表达式值
        self.compile_expression(switch_stmt.expression)
        
        # 为每个case生成代码
        for i, case in enumerate(switch_stmt.cases):
            if case.value is not None:  # 不是default case
                # 复制表达式值用于比较
                self.emit(OpCode.DUP)
                self.compile_expression(case.value)
                self.emit(OpCode.EQ)
                
                # 如果不相等，跳到下一个case
                next_case_label = len(self.get_current_instructions())
                self.emit(OpCode.JUMP_IF_FALSE, -1)  # 占位符
                
                # 生成case体
                for stmt in case.body:
                    self.compile_statement(stmt)
                
                # 跳到switch结束
                end_label = len(self.get_current_instructions())
                self.emit(OpCode.JUMP, -1)  # 占位符
                end_labels.append(end_label)
                
                # 更新next_case_label
                self.get_current_instructions()[next_case_label].operand = len(self.get_current_instructions())
        
        # 处理default case
        for case in switch_stmt.cases:
            if case.value is None:  # default case
                for stmt in case.body:
                    self.compile_statement(stmt)
                break
        
        # 清理栈上的表达式值
        self.emit(OpCode.POP)
        
        # 更新所有end标签
        current_pos = len(self.get_current_instructions())
        for label_pos in end_labels:
            self.get_current_instructions()[label_pos].operand = current_pos
    
    def compile_import_statement(self, import_stmt):
        """编译import语句"""
        # 加载模块名
        const_index = self.add_constant(import_stmt.module)
        self.emit(OpCode.LOAD_CONST, const_index)
        
        if import_stmt.items:
            # from module import items
            items_list = [item for item in import_stmt.items]
            items_index = self.add_constant(items_list)
            self.emit(OpCode.LOAD_CONST, items_index)
            self.emit(OpCode.IMPORT_FROM)
            
            # 将导入的项存储到变量中
            for item in import_stmt.items:
                if self.current_function:
                    var_index = self.get_or_create_local_var(item)
                    self.emit(OpCode.STORE_LOCAL, var_index)
                else:
                    var_index = self.get_or_create_global_var(item)
                    self.emit(OpCode.STORE_GLOBAL, var_index)
        else:
            # import module
            self.emit(OpCode.IMPORT_MODULE)
            if self.current_function:
                var_index = self.get_or_create_local_var(import_stmt.module)
                self.emit(OpCode.STORE_LOCAL, var_index)
            else:
                var_index = self.get_or_create_global_var(import_stmt.module)
                self.emit(OpCode.STORE_GLOBAL, var_index)
    
    def compile_if_statement(self, if_stmt: IfStatement):
        """编译if语句"""
        # 编译条件
        self.compile_expression(if_stmt.condition)
        
        # 条件跳转：如果为假，跳到下一个分支
        self.emit(OpCode.JUMP_IF_FALSE, 0)  # 占位符，稍后回填
        first_false_jump = len(self.get_current_instructions()) - 1  # 记录JUMP_IF_FALSE指令的位置
        
        # 编译then分支
        for stmt in if_stmt.then_body:
            self.compile_statement(stmt)
        
        # 跳到结束（跳过所有其他分支）
        end_jumps = []
        if if_stmt.elif_clauses or if_stmt.else_body:
            self.emit(OpCode.JUMP, 0)  # 占位符，稍后回填
            end_jump = len(self.get_current_instructions()) - 1  # 记录JUMP指令的位置
            end_jumps.append(end_jump)
        
        # 更新第一个false跳转标签（跳到第一个elif或else）
        self.get_current_instructions()[first_false_jump].operand = len(self.get_current_instructions())
        
        # 编译elif分支
        for elif_clause in if_stmt.elif_clauses:
            # 编译elif条件
            self.compile_expression(elif_clause.condition)
            
            # 条件跳转：如果为假，跳到下一个分支
            self.emit(OpCode.JUMP_IF_FALSE, 0)  # 占位符，稍后回填
            elif_false_jump = len(self.get_current_instructions()) - 1  # 记录JUMP_IF_FALSE指令的位置
            
            # 编译elif分支体
            for stmt in elif_clause.body:
                self.compile_statement(stmt)
            
            # 跳到结束
            self.emit(OpCode.JUMP, 0)  # 占位符，稍后回填
            elif_end_jump = len(self.get_current_instructions()) - 1  # 记录JUMP指令的位置
            end_jumps.append(elif_end_jump)
            
            # 更新elif false跳转标签（跳到下一个elif或else）
            self.get_current_instructions()[elif_false_jump].operand = len(self.get_current_instructions())
        
        # 编译else分支
        if if_stmt.else_body:
            for stmt in if_stmt.else_body:
                self.compile_statement(stmt)
        
        # 更新所有跳转到结束的标签
        current_pos = len(self.get_current_instructions())
        for jump_pos in end_jumps:
            self.get_current_instructions()[jump_pos].operand = current_pos
    
    def compile_while_loop(self, while_stmt: WhileLoop):
        """编译while循环"""
        loop_start = len(self.get_current_instructions())
        
        # 编译条件
        self.compile_expression(while_stmt.condition)
        
        # 条件跳转
        self.emit(OpCode.JUMP_IF_FALSE, 0)  # 占位符，稍后回填
        loop_end = len(self.get_current_instructions()) - 1  # 记录JUMP_IF_FALSE指令的位置
        
        # 保存break/continue标签
        old_break = self.break_labels
        old_continue = self.continue_labels
        self.break_labels = [loop_end]
        self.continue_labels = [loop_start]
        
        # 编译循环体
        for stmt in while_stmt.body:
            self.compile_statement(stmt)
        
        # 跳回循环开始
        self.emit(OpCode.JUMP, loop_start)
        
        # 更新循环结束标签
        self.get_current_instructions()[loop_end].operand = len(self.get_current_instructions())
        
        # 恢复break/continue标签
        self.break_labels = old_break
        self.continue_labels = old_continue
    
    def compile_for_loop(self, for_stmt: ForLoop):
        """编译for循环（使用FOR_ITER操作码）"""
        # 编译iterable表达式
        self.compile_expression(for_stmt.iterable)
        
        # 获取迭代器
        self.emit(OpCode.GET_ITER)
        
        # 循环开始
        loop_start = len(self.get_current_instructions())
        
        # FOR_ITER指令：尝试获取下一个值，如果迭代结束则跳转
        self.emit(OpCode.FOR_ITER, 0)  # 占位符，稍后回填跳转目标
        for_iter_index = len(self.get_current_instructions()) - 1
        
        # 存储到循环变量
        if self.current_function:
            loop_var_idx = self.get_or_create_local_var(for_stmt.variable)
            self.emit(OpCode.STORE_LOCAL, loop_var_idx)
        else:
            loop_var_idx = self.get_or_create_global_var(for_stmt.variable)
            self.emit(OpCode.STORE_GLOBAL, loop_var_idx)
        
        # 保存break/continue标签
        old_break = self.break_labels
        old_continue = self.continue_labels
        self.break_labels = []
        self.continue_labels = []
        
        # 编译循环体
        for stmt in for_stmt.body:
            self.compile_statement(stmt)
        
        # continue标签处理
        continue_point = len(self.get_current_instructions())
        for i, label in enumerate(self.continue_labels):
            if isinstance(label, int) and label < len(self.get_current_instructions()):
                self.get_current_instructions()[label].operand = continue_point
        
        # 跳回循环开始
        self.emit(OpCode.JUMP, loop_start)
        
        # 循环结束位置
        loop_end = len(self.get_current_instructions())
        
        # 回填FOR_ITER的跳转目标（循环结束位置）
        current_instructions = self.get_current_instructions()
        current_instructions[for_iter_index].operand = loop_end
        
        # break标签处理
        for i, label in enumerate(self.break_labels):
            if isinstance(label, int) and label < len(current_instructions):
                current_instructions[label].operand = loop_end
        
        # 恢复break/continue标签
        self.break_labels = old_break
        self.continue_labels = old_continue
    
    def get_current_instructions(self) -> List[Instruction]:
        """获取当前指令列表"""
        if self.current_function:
            return self.current_function.instructions
        else:
            return self.instructions
    
    def get_or_create_var(self, name: str) -> int:
        """获取或创建变量索引（兼容性方法）"""
        if self.current_function:
            if name not in self.current_function.local_vars:
                self.current_function.local_vars[name] = len(self.current_function.local_vars)
            return self.current_function.local_vars[name]
        else:
            if name not in self.global_vars:
                self.global_vars[name] = len(self.global_vars)
            return self.global_vars[name]
    
    def get_or_create_global_var(self, name: str) -> int:
        """获取或创建全局变量索引"""
        if name not in self.global_vars:
            self.global_vars[name] = len(self.global_vars)
        return self.global_vars[name]
    
    def get_or_create_local_var(self, name: str) -> int:
        """获取或创建局部变量索引"""
        if not self.current_function:
            raise ValueError("Cannot create local variable outside function")
        if name not in self.current_function.local_vars:
            self.current_function.local_vars[name] = len(self.current_function.local_vars)
        return self.current_function.local_vars[name]
    
    def serialize_bytecode(self) -> bytes:
        """序列化字节码为二进制格式"""
        # 文件头
        header = b'AQUA'  # 魔数
        version = struct.pack('<H', 1)  # 版本号
        
        # 常量池
        constants_data = json.dumps(self.constants).encode('utf-8')
        constants_size = struct.pack('<I', len(constants_data))
        
        # 全局变量表
        globals_data = json.dumps(self.global_vars).encode('utf-8')
        globals_size = struct.pack('<I', len(globals_data))
        
        # 函数表
        functions_data = {}
        for name, func in self.functions.items():
            functions_data[name] = {
                'parameters': func.parameters,
                'local_vars': func.local_vars,
                'instructions': [(inst.opcode.value, inst.operand) for inst in func.instructions]
            }
        functions_bytes = json.dumps(functions_data).encode('utf-8')
        functions_size = struct.pack('<I', len(functions_bytes))
        
        # 主程序指令
        main_instructions = [(inst.opcode.value, inst.operand) for inst in self.instructions]
        main_data = json.dumps(main_instructions).encode('utf-8')
        main_size = struct.pack('<I', len(main_data))
        
        # 组装字节码
        bytecode = (header + version + 
                   constants_size + constants_data +
                   globals_size + globals_data +
                   functions_size + functions_bytes +
                   main_size + main_data)
        
        return bytecode
    
    def compile_try_statement(self, try_stmt: TryStatement):
        """编译try语句"""
        # 开始try块
        self.emit(OpCode.TRY_BEGIN)
        
        # 编译try块
        for stmt in try_stmt.try_body:
            self.compile_statement(stmt)
        
        # 结束try块
        self.emit(OpCode.TRY_END)
        
        # 编译catch子句
        for catch_clause in try_stmt.catch_clauses:
            self.compile_catch_clause(catch_clause)
        
        # 编译finally块（如果存在）
        if try_stmt.finally_body:
            self.emit(OpCode.FINALLY_BEGIN)
            for stmt in try_stmt.finally_body:
                self.compile_statement(stmt)
            self.emit(OpCode.FINALLY_END)
    
    def compile_catch_clause(self, catch_clause: CatchClause):
        """编译catch子句"""
        # 开始catch块
        if catch_clause.exception_type:
            # 如果指定了异常类型，将类型名作为操作数
            type_index = self.add_constant(catch_clause.exception_type)
            self.emit(OpCode.CATCH_BEGIN, type_index)
        else:
            # 捕获所有异常
            self.emit(OpCode.CATCH_BEGIN)
        
        # 如果指定了异常变量名，将异常对象存储到变量中
        if catch_clause.exception_name:
            if self.current_function:
                var_index = self.get_or_create_local_var(catch_clause.exception_name)
                self.emit(OpCode.STORE_LOCAL, var_index)
            else:
                var_index = self.get_or_create_global_var(catch_clause.exception_name)
                self.emit(OpCode.STORE_GLOBAL, var_index)
        else:
            # 如果没有异常变量名，需要弹出异常对象
            self.emit(OpCode.POP)
        
        # 编译catch块
        for stmt in catch_clause.body:
            self.compile_statement(stmt)
        
        # 结束catch块
        self.emit(OpCode.CATCH_END)
    
    def compile_throw_statement(self, throw_stmt: ThrowStatement):
        """编译throw语句"""
        # 编译异常表达式
        self.compile_expression(throw_stmt.exception)
        # 抛出异常
        self.emit(OpCode.THROW)

def main():
    # 测试代码生成器
    test_code = '''
def add(a, b):
    return a + b

result = add(3, 4)
print(result)
'''
    
    from lexer import Lexer
    from parser import Parser
    
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    codegen = CodeGenerator()
    bytecode = codegen.generate(ast)
    
    # 保存字节码文件
    with open('test.acode', 'wb') as f:
        f.write(bytecode)
    
    print(f"Generated bytecode: {len(bytecode)} bytes")
    print(f"Constants: {codegen.constants}")
    print(f"Global vars: {codegen.global_vars}")
    print(f"Functions: {list(codegen.functions.keys())}")

if __name__ == "__main__":
    main()