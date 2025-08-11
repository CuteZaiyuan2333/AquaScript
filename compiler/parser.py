"""
AquaScript语法分析器
负责将token流转换为抽象语法树(AST)
"""

from typing import List, Optional, Union, Any
from dataclasses import dataclass, field
from lexer import Token, TokenType, Lexer

# AST节点基类
@dataclass
class ASTNode:
    pass

# 表达式节点
@dataclass
class Expression(ASTNode):
    pass

@dataclass
class NumberLiteral(Expression):
    value: float

@dataclass
class StringLiteral(Expression):
    value: str

@dataclass
class BooleanLiteral(Expression):
    value: bool

@dataclass
class NoneLiteral(Expression):
    pass

@dataclass
class Identifier(Expression):
    name: str

@dataclass
class BinaryOperation(Expression):
    left: Expression
    operator: str
    right: Expression

@dataclass
class UnaryOperation(Expression):
    operator: str
    operand: Expression

@dataclass
class FunctionCall(Expression):
    function: Expression
    arguments: List[Expression]

@dataclass
class ListLiteral(Expression):
    elements: List[Expression]

@dataclass
class DictLiteral(Expression):
    pairs: List[tuple[Expression, Expression]]  # 键值对列表

@dataclass
class TupleLiteral(Expression):
    elements: List[Expression]

@dataclass
class ListComprehension(Expression):
    element: Expression  # 生成的元素表达式
    variable: str  # 迭代变量
    iterable: Expression  # 迭代对象
    condition: Optional[Expression] = None  # 可选的条件表达式

@dataclass
class FStringLiteral(Expression):
    parts: List[tuple[str, str]]  # (type, content) - type: 'text' or 'expr'

@dataclass
class AttributeAccess(Expression):
    object: Expression
    attribute: str

@dataclass
class IndexAccess(Expression):
    object: Expression
    index: Expression

# 语句节点
@dataclass
class Statement(ASTNode):
    pass

@dataclass
class ExpressionStatement(Statement):
    expression: Expression

@dataclass
class VarDeclaration(Statement):
    name: str
    value: Expression
    type_hint: Optional[str] = None

@dataclass
class Assignment(Statement):
    target: str
    value: Expression

@dataclass
class AttributeAssignment(Statement):
    object: Expression
    attribute: str
    value: Expression

@dataclass
class IndexAssignment(Statement):
    object: Expression
    index: Expression
    value: Expression

@dataclass
class FunctionDef(Statement):
    name: str
    parameters: List[str]
    body: List[Statement]

@dataclass
class ClassDef(Statement):
    name: str
    body: List[Statement]

@dataclass
class ElifClause(ASTNode):
    condition: Expression
    body: List[Statement]

@dataclass
class IfStatement(Statement):
    condition: Expression
    then_body: List[Statement]
    elif_clauses: List[ElifClause] = field(default_factory=list)
    else_body: Optional[List[Statement]] = None

@dataclass
class ForLoop(Statement):
    variable: str
    iterable: Expression
    body: List[Statement]

@dataclass
class WhileLoop(Statement):
    condition: Expression
    body: List[Statement]

@dataclass
class RepeatLoop(Statement):
    condition: Expression
    body: List[Statement]

@dataclass
class SwitchStatement(Statement):
    expression: Expression
    cases: List['CaseClause']
    default_case: Optional[List[Statement]] = None

@dataclass
class CaseClause(ASTNode):
    value: Expression
    body: List[Statement]

@dataclass
class ImportStatement(Statement):
    module: str
    items: Optional[List[str]] = None  # None表示导入整个模块

@dataclass
class ReturnStatement(Statement):
    value: Optional[Expression] = None

@dataclass
class BreakStatement(Statement):
    pass

@dataclass
class ContinueStatement(Statement):
    pass

@dataclass
class TryStatement(Statement):
    try_body: List[Statement]
    catch_clauses: List['CatchClause']
    finally_body: Optional[List[Statement]] = None

@dataclass
class CatchClause(ASTNode):
    exception_type: Optional[str]  # 异常类型，None表示捕获所有异常
    exception_name: Optional[str]  # 异常变量名
    body: List[Statement]

@dataclass
class ThrowStatement(Statement):
    exception: Expression

# 新增高级特性的AST节点
@dataclass
class LambdaExpression(Expression):
    parameters: List[str]
    body: Expression

@dataclass
class YieldExpression(Expression):
    value: Optional[Expression] = None

@dataclass
class AwaitExpression(Expression):
    expression: Expression

@dataclass
class WithStatement(Statement):
    context_expr: Expression
    optional_vars: Optional[str]
    body: List[Statement]

@dataclass
class AsyncFunctionDef(Statement):
    name: str
    parameters: List[str]
    body: List[Statement]

@dataclass
class GlobalStatement(Statement):
    names: List[str]

@dataclass
class NonlocalStatement(Statement):
    names: List[str]

@dataclass
class AssertStatement(Statement):
    test: Expression
    msg: Optional[Expression] = None

@dataclass
class DelStatement(Statement):
    targets: List[Expression]

@dataclass
class PassStatement(Statement):
    pass

@dataclass
class Decorator(ASTNode):
    name: str
    args: List[Expression]

@dataclass
class DecoratedFunction(Statement):
    decorators: List[Decorator]
    function: FunctionDef

@dataclass
class GeneratorExpression(Expression):
    element: Expression
    generators: List['Comprehension']

@dataclass
class Comprehension(ASTNode):
    target: str
    iter: Expression
    ifs: List[Expression]

@dataclass
class Program(ASTNode):
    statements: List[Statement]

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.current_token = self.tokens[0] if tokens else None
    
    def advance(self):
        """移动到下一个token"""
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
        else:
            self.current_token = None
    
    def peek(self, offset: int = 1) -> Optional[Token]:
        """查看前面的token"""
        peek_pos = self.position + offset
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return None
    
    def match(self, *token_types: TokenType) -> bool:
        """检查当前token是否匹配指定类型"""
        if self.current_token is None:
            return False
        return self.current_token.type in token_types
    
    def consume(self, token_type: TokenType, error_message: str = "") -> Token:
        """消费指定类型的token"""
        if not self.match(token_type):
            raise SyntaxError(f"Expected {token_type.value}, got {self.current_token.type.value if self.current_token else 'EOF'}. {error_message}")
        token = self.current_token
        self.advance()
        return token
    
    def skip_newlines(self):
        """跳过换行符和注释"""
        while self.match(TokenType.NEWLINE, TokenType.COMMENT):
            self.advance()
    
    def parse_block(self) -> List[Statement]:
        """解析大括号块语句"""
        statements = []
        self.consume(TokenType.LBRACE)
        self.skip_newlines()
        
        # 跳过可能的缩进
        if self.match(TokenType.INDENT):
            self.advance()
        
        while not self.match(TokenType.RBRACE, TokenType.EOF):
            if self.match(TokenType.NEWLINE, TokenType.COMMENT):
                self.advance()
                continue
            
            # 跳过缩进和反缩进
            if self.match(TokenType.INDENT, TokenType.DEDENT):
                self.advance()
                continue
            
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()
        
        # 跳过可能的反缩进
        if self.match(TokenType.DEDENT):
            self.advance()
        
        self.consume(TokenType.RBRACE)
        return statements
    
    def parse(self) -> Program:
        """解析整个程序"""
        statements = []
        self.skip_newlines()
        
        while self.current_token and not self.match(TokenType.EOF):
            if self.match(TokenType.NEWLINE, TokenType.COMMENT):
                self.advance()
                continue
            
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()
        
        return Program(statements)
    
    def parse_statement(self) -> Optional[Statement]:
        """解析语句"""
        # 检查装饰器
        if self.match(TokenType.AT):
            return self.parse_decorated_function()
        elif self.match(TokenType.ASYNC):
            return self.parse_async_function_def()
        elif self.match(TokenType.FUNC):
            return self.parse_function_def()
        elif self.match(TokenType.VAR):
            return self.parse_var_declaration()
        elif self.match(TokenType.CLASS):
            return self.parse_class_def()
        elif self.match(TokenType.IF):
            return self.parse_if_statement()
        elif self.match(TokenType.FOR):
            return self.parse_for_loop()
        elif self.match(TokenType.WHILE):
            return self.parse_while_loop()
        elif self.match(TokenType.REPEAT):
            return self.parse_repeat_loop()
        elif self.match(TokenType.SWITCH):
            return self.parse_switch_statement()
        elif self.match(TokenType.WITH):
            return self.parse_with_statement()
        elif self.match(TokenType.IMPORT, TokenType.FROM):
            return self.parse_import_statement()
        elif self.match(TokenType.RETURN):
            return self.parse_return_statement()
        elif self.match(TokenType.BREAK):
            self.advance()
            return BreakStatement()
        elif self.match(TokenType.CONTINUE):
            self.advance()
            return ContinueStatement()
        elif self.match(TokenType.GLOBAL):
            return self.parse_global_statement()
        elif self.match(TokenType.NONLOCAL):
            return self.parse_nonlocal_statement()
        elif self.match(TokenType.ASSERT):
            return self.parse_assert_statement()
        elif self.match(TokenType.DEL):
            return self.parse_del_statement()
        elif self.match(TokenType.PASS):
            self.advance()
            return PassStatement()
        elif self.match(TokenType.TRY):
            return self.parse_try_statement()
        elif self.match(TokenType.THROW):
            return self.parse_throw_statement()
        else:
            return self.parse_expression_or_assignment()
    
    def parse_function_def(self) -> FunctionDef:
        """解析函数定义"""
        self.consume(TokenType.FUNC)
        name = self.consume(TokenType.IDENTIFIER).value
        
        self.consume(TokenType.LPAREN)
        parameters = []
        
        if not self.match(TokenType.RPAREN):
            # 解析参数（可能包含类型注解）
            if self.match(TokenType.SELF):
                param_name = self.current_token.value
                self.advance()
            else:
                param_name = self.consume(TokenType.IDENTIFIER).value
            
            if self.match(TokenType.COLON):
                self.advance()
                # 跳过参数类型注解
                if self.current_token.type in [TokenType.INT, TokenType.FLOAT, TokenType.STR, TokenType.BOOL]:
                    self.advance()
                else:
                    self.consume(TokenType.IDENTIFIER)
            parameters.append(param_name)
            
            while self.match(TokenType.COMMA):
                self.advance()
                if self.match(TokenType.SELF):
                    param_name = self.current_token.value
                    self.advance()
                else:
                    param_name = self.consume(TokenType.IDENTIFIER).value
                
                if self.match(TokenType.COLON):
                    self.advance()
                    # 跳过参数类型注解
                    if self.current_token.type in [TokenType.INT, TokenType.FLOAT, TokenType.STR, TokenType.BOOL]:
                        self.advance()
                    else:
                        self.consume(TokenType.IDENTIFIER)
                parameters.append(param_name)
        
        self.consume(TokenType.RPAREN)
        
        # 可选的返回类型注解
        if self.match(TokenType.ARROW):
            self.advance()  # 消费箭头
            # 跳过返回类型注解
            if self.current_token and self.current_token.type in [TokenType.INT, TokenType.FLOAT, TokenType.STR, TokenType.BOOL]:
                self.advance()
            elif self.current_token and self.current_token.type == TokenType.IDENTIFIER:
                self.advance()
            # 如果没有类型注解，继续
        
        # 支持两种语法：大括号语法和Python风格的缩进语法
        if self.match(TokenType.LBRACE):
            # 大括号语法: func name() { ... }
            body = self.parse_block()
        else:
            # Python风格的缩进语法: func name(): ...
            self.consume(TokenType.COLON)
            self.skip_newlines()
            
            # 解析函数体
            self.consume(TokenType.INDENT)
            body = []
            
            while not self.match(TokenType.DEDENT, TokenType.EOF):
                if self.match(TokenType.NEWLINE):
                    self.advance()
                    continue
                stmt = self.parse_statement()
                if stmt:
                    body.append(stmt)
                self.skip_newlines()
            
            if self.match(TokenType.DEDENT):
                self.advance()
        
        return FunctionDef(name, parameters, body)
    
    def parse_var_declaration(self) -> VarDeclaration:
        """解析变量声明: var name: type = value"""
        self.consume(TokenType.VAR)
        name = self.consume(TokenType.IDENTIFIER).value
        
        # 可选的类型注解
        type_hint = None
        if self.match(TokenType.COLON):
            self.advance()
            # 类型可以是标识符或内置类型关键字
            if self.current_token.type in [TokenType.INT, TokenType.FLOAT, TokenType.STR, TokenType.BOOL]:
                type_hint = self.current_token.value
                self.advance()
            else:
                type_hint = self.consume(TokenType.IDENTIFIER).value
        
        # 可选的初始值
        value = None
        if self.match(TokenType.ASSIGN):
            self.advance()
            value = self.parse_expression()
        
        return VarDeclaration(name, value, type_hint)
    
    def parse_class_def(self) -> ClassDef:
        """解析类定义"""
        self.consume(TokenType.CLASS)
        name = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.COLON)
        self.skip_newlines()
        
        self.consume(TokenType.INDENT)
        body = []
        
        while not self.match(TokenType.DEDENT, TokenType.EOF):
            if self.match(TokenType.NEWLINE, TokenType.COMMENT):
                self.advance()
                continue
            
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        
        if self.match(TokenType.DEDENT):
            self.advance()
        
        return ClassDef(name, body)
    
    def parse_repeat_loop(self) -> RepeatLoop:
        """解析repeat循环（do-while风格）"""
        self.consume(TokenType.REPEAT)
        self.consume(TokenType.COLON)
        self.skip_newlines()
        
        # 解析循环体
        self.consume(TokenType.INDENT)
        body = []
        
        while not self.match(TokenType.DEDENT, TokenType.EOF):
            if self.match(TokenType.NEWLINE, TokenType.COMMENT):
                self.advance()
                continue
            
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        
        if self.match(TokenType.DEDENT):
            self.advance()
        
        # 解析while条件
        self.consume(TokenType.WHILE)
        condition = self.parse_expression()
        
        return RepeatLoop(condition, body)
    
    def parse_switch_statement(self) -> SwitchStatement:
        """解析switch语句"""
        self.consume(TokenType.SWITCH)
        expression = self.parse_expression()
        self.consume(TokenType.COLON)
        self.skip_newlines()
        
        self.consume(TokenType.INDENT)
        cases = []
        default_case = None
        
        while not self.match(TokenType.DEDENT, TokenType.EOF):
            if self.match(TokenType.NEWLINE, TokenType.COMMENT):
                self.advance()
                continue
            
            if self.match(TokenType.CASE):
                self.advance()
                case_value = self.parse_expression()
                self.consume(TokenType.COLON)
                self.skip_newlines()
                
                # 处理case语句体的缩进
                case_body = []
                if self.match(TokenType.INDENT):
                    self.advance()
                    
                    while not self.match(TokenType.DEDENT, TokenType.EOF):
                        if self.match(TokenType.NEWLINE, TokenType.COMMENT):
                            self.advance()
                            continue
                        
                        stmt = self.parse_statement()
                        if stmt:
                            case_body.append(stmt)
                    
                    if self.match(TokenType.DEDENT):
                        self.advance()
                
                cases.append(CaseClause(case_value, case_body))
            
            elif self.match(TokenType.DEFAULT):
                self.advance()
                self.consume(TokenType.COLON)
                self.skip_newlines()
                
                default_case = []
                if self.match(TokenType.INDENT):
                    self.advance()
                    
                    while not self.match(TokenType.DEDENT, TokenType.EOF):
                        if self.match(TokenType.NEWLINE, TokenType.COMMENT):
                            self.advance()
                            continue
                        
                        stmt = self.parse_statement()
                        if stmt:
                            default_case.append(stmt)
                    
                    if self.match(TokenType.DEDENT):
                        self.advance()
                break
        
        if self.match(TokenType.DEDENT):
            self.advance()
        
        return SwitchStatement(expression, cases, default_case)
    
    def parse_import_statement(self) -> ImportStatement:
        """解析import语句"""
        if self.match(TokenType.FROM):
            # from module import item1, item2
            self.advance()
            module = self.consume(TokenType.IDENTIFIER).value
            self.consume(TokenType.IMPORT)
            
            items = []
            items.append(self.consume(TokenType.IDENTIFIER).value)
            
            while self.match(TokenType.COMMA):
                self.advance()
                items.append(self.consume(TokenType.IDENTIFIER).value)
            
            return ImportStatement(module, items)
        else:
            # import module
            self.consume(TokenType.IMPORT)
            module = self.consume(TokenType.IDENTIFIER).value
            
            # 支持 import module.submodule 形式
            while self.match(TokenType.DOT):
                self.advance()
                
                # 检查是否是新语法: import module.(item1, item2, ...)
                if self.match(TokenType.LPAREN):
                    self.advance()  # 消费 (
                    
                    items = []
                    items.append(self.consume(TokenType.IDENTIFIER).value)
                    
                    while self.match(TokenType.COMMA):
                        self.advance()
                        items.append(self.consume(TokenType.IDENTIFIER).value)
                    
                    self.consume(TokenType.RPAREN)  # 消费 )
                    return ImportStatement(module, items)
                else:
                    # 普通的 module.submodule 形式
                    module += "." + self.consume(TokenType.IDENTIFIER).value
            
            return ImportStatement(module)
    
    def parse_if_statement(self) -> IfStatement:
        """解析if语句"""
        self.consume(TokenType.IF)
        condition = self.parse_expression()
        
        # 支持两种语法：大括号语法和Python风格的缩进语法
        if self.match(TokenType.LBRACE):
            # 大括号语法: if condition { ... }
            then_body = self.parse_block()
        else:
            # Python风格的缩进语法: if condition: ...
            self.consume(TokenType.COLON)
            self.skip_newlines()
            
            # 解析then分支
            self.consume(TokenType.INDENT)
            then_body = []
            
            while not self.match(TokenType.DEDENT, TokenType.EOF):
                if self.match(TokenType.NEWLINE):
                    self.advance()
                    continue
                stmt = self.parse_statement()
                if stmt:
                    then_body.append(stmt)
                self.skip_newlines()
            
            if self.match(TokenType.DEDENT):
                self.advance()
        
        # 解析elif分支
        elif_clauses = []
        while self.match(TokenType.ELIF):
            self.advance()
            elif_condition = self.parse_expression()
            
            if self.match(TokenType.LBRACE):
                # 大括号语法: elif condition { ... }
                elif_body = self.parse_block()
            else:
                # Python风格的缩进语法: elif condition: ...
                self.consume(TokenType.COLON)
                self.skip_newlines()
                self.consume(TokenType.INDENT)
                
                elif_body = []
                while not self.match(TokenType.DEDENT, TokenType.EOF):
                    if self.match(TokenType.NEWLINE):
                        self.advance()
                        continue
                    stmt = self.parse_statement()
                    if stmt:
                        elif_body.append(stmt)
                    self.skip_newlines()
                
                if self.match(TokenType.DEDENT):
                    self.advance()
            
            elif_clauses.append(ElifClause(elif_condition, elif_body))
        
        # 解析else分支
        else_body = None
        if self.match(TokenType.ELSE):
            self.advance()
            
            if self.match(TokenType.LBRACE):
                # 大括号语法: else { ... }
                else_body = self.parse_block()
            else:
                # Python风格的缩进语法: else: ...
                self.consume(TokenType.COLON)
                self.skip_newlines()
                self.consume(TokenType.INDENT)
                
                else_body = []
                while not self.match(TokenType.DEDENT, TokenType.EOF):
                    if self.match(TokenType.NEWLINE):
                        self.advance()
                        continue
                    stmt = self.parse_statement()
                    if stmt:
                        else_body.append(stmt)
                    self.skip_newlines()
                
                if self.match(TokenType.DEDENT):
                    self.advance()
        
        return IfStatement(condition, then_body, elif_clauses, else_body)
    
    def parse_for_loop(self) -> ForLoop:
        """解析for循环"""
        self.consume(TokenType.FOR)
        variable = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.IN)
        iterable = self.parse_expression()
        
        # 支持两种语法：大括号语法和Python风格的缩进语法
        if self.match(TokenType.LBRACE):
            # 大括号语法: for var in iterable { ... }
            body = self.parse_block()
        else:
            # Python风格的缩进语法: for var in iterable: ...
            self.consume(TokenType.COLON)
            self.skip_newlines()
            
            # 解析循环体
            self.consume(TokenType.INDENT)
            body = []
            
            while not self.match(TokenType.DEDENT, TokenType.EOF):
                if self.match(TokenType.NEWLINE):
                    self.advance()
                    continue
                stmt = self.parse_statement()
                if stmt:
                    body.append(stmt)
                self.skip_newlines()
            
            if self.match(TokenType.DEDENT):
                self.advance()
        
        return ForLoop(variable, iterable, body)
    
    def parse_while_loop(self) -> WhileLoop:
        """解析while循环"""
        self.consume(TokenType.WHILE)
        condition = self.parse_expression()
        
        # 支持两种语法：大括号语法和Python风格的缩进语法
        if self.match(TokenType.LBRACE):
            # 大括号语法: while condition { ... }
            body = self.parse_block()
        else:
            # Python风格的缩进语法: while condition: ...
            self.consume(TokenType.COLON)
            self.skip_newlines()
            
            # 解析循环体
            self.consume(TokenType.INDENT)
            body = []
            
            while not self.match(TokenType.DEDENT, TokenType.EOF):
                if self.match(TokenType.NEWLINE):
                    self.advance()
                    continue
                stmt = self.parse_statement()
                if stmt:
                    body.append(stmt)
                self.skip_newlines()
            
            if self.match(TokenType.DEDENT):
                self.advance()
        
        return WhileLoop(condition, body)
    
    def parse_return_statement(self) -> ReturnStatement:
        """解析return语句"""
        self.consume(TokenType.RETURN)
        value = None
        
        if not self.match(TokenType.NEWLINE, TokenType.EOF):
            value = self.parse_expression()
        
        return ReturnStatement(value)
    
    def parse_expression_or_assignment(self) -> Statement:
        """解析表达式或赋值语句"""
        expr = self.parse_assignment_target()
        
        # 检查是否为赋值
        if self.match(TokenType.ASSIGN):
            self.advance()
            value = self.parse_expression()
            
            if isinstance(expr, Identifier):
                return Assignment(expr.name, value)
            elif isinstance(expr, AttributeAccess):
                return AttributeAssignment(expr.object, expr.attribute, value)
            elif isinstance(expr, IndexAccess):
                return IndexAssignment(expr.object, expr.index, value)
            else:
                raise SyntaxError("Invalid assignment target")
        
        return ExpressionStatement(expr)
    
    def parse_assignment_target(self) -> Expression:
        """解析赋值目标（可以是标识符或属性访问）"""
        expr = self.parse_postfix_expression()
        
        return expr
    
    def parse_expression(self) -> Expression:
        """解析表达式"""
        return self.parse_or_expression()
    
    def parse_or_expression(self) -> Expression:
        """解析or表达式"""
        expr = self.parse_and_expression()
        
        while self.match(TokenType.OR):
            operator = self.current_token.value
            self.advance()
            right = self.parse_and_expression()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def parse_and_expression(self) -> Expression:
        """解析and表达式"""
        expr = self.parse_equality_expression()
        
        while self.match(TokenType.AND):
            operator = self.current_token.value
            self.advance()
            right = self.parse_equality_expression()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def parse_equality_expression(self) -> Expression:
        """解析相等性表达式"""
        expr = self.parse_comparison_expression()
        
        while self.match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            operator = self.current_token.value
            self.advance()
            right = self.parse_comparison_expression()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def parse_comparison_expression(self) -> Expression:
        """解析比较表达式"""
        expr = self.parse_additive_expression()
        
        while self.match(TokenType.LESS, TokenType.GREATER, TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL, TokenType.IN):
            operator = self.current_token.value
            self.advance()
            right = self.parse_additive_expression()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def parse_additive_expression(self) -> Expression:
        """解析加减表达式"""
        expr = self.parse_multiplicative_expression()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.current_token.value
            self.advance()
            right = self.parse_multiplicative_expression()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def parse_multiplicative_expression(self) -> Expression:
        """解析乘除表达式"""
        expr = self.parse_power_expression()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            operator = self.current_token.value
            self.advance()
            right = self.parse_power_expression()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def parse_power_expression(self) -> Expression:
        """解析幂运算表达式"""
        expr = self.parse_unary_expression()
        
        if self.match(TokenType.POWER):
            operator = self.current_token.value
            self.advance()
            right = self.parse_power_expression()  # 右结合
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def parse_unary_expression(self) -> Expression:
        """解析一元表达式"""
        if self.match(TokenType.NOT, TokenType.MINUS, TokenType.PLUS):
            operator = self.current_token.value
            self.advance()
            operand = self.parse_unary_expression()
            return UnaryOperation(operator, operand)
        
        return self.parse_postfix_expression()
    
    def parse_postfix_expression(self) -> Expression:
        """解析后缀表达式（函数调用等）"""
        expr = self.parse_primary_expression()
        
        while True:
            if self.match(TokenType.LPAREN):
                # 函数调用
                self.advance()
                arguments = []
                
                if not self.match(TokenType.RPAREN):
                    arguments.append(self.parse_expression())
                    while self.match(TokenType.COMMA):
                        self.advance()
                        arguments.append(self.parse_expression())
                
                self.consume(TokenType.RPAREN)
                expr = FunctionCall(expr, arguments)
            
            # 处理属性访问
            elif self.match(TokenType.DOT):
                self.advance()
                attr_name = self.consume(TokenType.IDENTIFIER).value
                expr = AttributeAccess(expr, attr_name)
            
            # 处理索引访问
            elif self.match(TokenType.LBRACKET):
                self.advance()
                index = self.parse_expression()
                self.consume(TokenType.RBRACKET)
                expr = IndexAccess(expr, index)
            
            else:
                break
        
        return expr
    
    def parse_primary_expression(self) -> Expression:
        """解析基本表达式"""
        # Lambda表达式
        if self.match(TokenType.LAMBDA):
            return self.parse_lambda_expression()
        
        # Yield表达式
        if self.match(TokenType.YIELD):
            return self.parse_yield_expression()
        
        # Await表达式
        if self.match(TokenType.AWAIT):
            return self.parse_await_expression()
        
        if self.match(TokenType.NUMBER):
            value_str = self.current_token.value
            # 如果包含小数点，解析为浮点数，否则解析为整数
            if '.' in value_str:
                value = float(value_str)
            else:
                value = int(value_str)
            self.advance()
            return NumberLiteral(value)
        
        if self.match(TokenType.STRING):
            value = self.current_token.value
            self.advance()
            return StringLiteral(value)
        
        if self.match(TokenType.F_STRING):
            import json
            parts_json = self.current_token.value
            parts = json.loads(parts_json)
            self.advance()
            return FStringLiteral(parts)
        
        if self.match(TokenType.TRUE):
            self.advance()
            return BooleanLiteral(True)
        
        if self.match(TokenType.FALSE):
            self.advance()
            return BooleanLiteral(False)
        
        if self.match(TokenType.NONE):
            self.advance()
            return NoneLiteral()
        
        if self.match(TokenType.IDENTIFIER):
            name = self.current_token.value
            self.advance()
            return Identifier(name)
        
        if self.match(TokenType.SELF):
            name = self.current_token.value
            self.advance()
            return Identifier(name)
        
        # 类型关键字也可以作为标识符使用（如函数名）
        if self.match(TokenType.STR, TokenType.INT, TokenType.FLOAT, TokenType.BOOL):
            name = self.current_token.value
            self.advance()
            return Identifier(name)
        
        if self.match(TokenType.LPAREN):
            self.advance()
            
            # 空元组 ()
            if self.match(TokenType.RPAREN):
                self.advance()
                return TupleLiteral([])
            
            # 解析第一个表达式
            first_expr = self.parse_expression()
            
            # 检查是否是元组
            if self.match(TokenType.COMMA):
                # 这是一个元组
                elements = [first_expr]
                
                while self.match(TokenType.COMMA):
                    self.advance()
                    # 允许尾随逗号
                    if self.match(TokenType.RPAREN):
                        break
                    elements.append(self.parse_expression())
                
                self.consume(TokenType.RPAREN)
                return TupleLiteral(elements)
            else:
                # 这是一个括号表达式
                self.consume(TokenType.RPAREN)
                return first_expr
        
        if self.match(TokenType.LBRACKET):
            self.advance()
            
            # 空列表
            if self.match(TokenType.RBRACKET):
                self.advance()
                return ListLiteral([])
            
            # 解析第一个表达式
            first_expr = self.parse_expression()
            
            # 检查是否是列表推导式
            if self.match(TokenType.FOR):
                # 这是列表推导式: [expr for var in iterable]
                self.advance()  # 消费 'for'
                
                # 解析迭代变量
                variable = self.consume(TokenType.IDENTIFIER).value
                
                # 消费 'in'
                self.consume(TokenType.IN)
                
                # 解析迭代对象
                iterable = self.parse_expression()
                
                # 检查是否有条件
                condition = None
                if self.match(TokenType.IF):
                    self.advance()  # 消费 'if'
                    condition = self.parse_expression()
                
                self.consume(TokenType.RBRACKET)
                return ListComprehension(first_expr, variable, iterable, condition)
            else:
                # 这是普通列表字面量
                elements = [first_expr]
                
                while self.match(TokenType.COMMA):
                    self.advance()
                    # 允许尾随逗号
                    if self.match(TokenType.RBRACKET):
                        break
                    elements.append(self.parse_expression())
                
                self.consume(TokenType.RBRACKET)
                return ListLiteral(elements)
        
        if self.match(TokenType.LBRACE):
            self.advance()
            pairs = []
            
            if not self.match(TokenType.RBRACE):
                # 解析第一个键值对
                key = self.parse_expression()
                self.consume(TokenType.COLON)
                value = self.parse_expression()
                pairs.append((key, value))
                
                # 解析后续键值对
                while self.match(TokenType.COMMA):
                    self.advance()
                    # 允许尾随逗号
                    if self.match(TokenType.RBRACE):
                        break
                    key = self.parse_expression()
                    self.consume(TokenType.COLON)
                    value = self.parse_expression()
                    pairs.append((key, value))
            
            self.consume(TokenType.RBRACE)
            return DictLiteral(pairs)
        
        raise SyntaxError(f"Unexpected token: {self.current_token.type.value if self.current_token else 'EOF'}")
    
    def parse_try_statement(self) -> TryStatement:
        """解析try语句"""
        self.consume(TokenType.TRY)
        
        # 解析try块（支持大括号语法）
        try_body = self.parse_block()
        
        # 解析catch子句
        catch_clauses = []
        while self.match(TokenType.CATCH):
            catch_clause = self.parse_catch_clause()
            catch_clauses.append(catch_clause)
        
        # 解析可选的finally块
        finally_body = None
        if self.match(TokenType.FINALLY):
            self.advance()
            finally_body = self.parse_block()
        
        # 确保至少有一个catch或finally子句
        if not catch_clauses and not finally_body:
            raise SyntaxError("try statement must have at least one catch or finally clause")
        
        return TryStatement(try_body, catch_clauses, finally_body)
    
    def parse_catch_clause(self) -> CatchClause:
        """解析catch子句"""
        self.consume(TokenType.CATCH)
        
        exception_type = None
        exception_name = None
        
        # 解析异常类型和变量名
        if self.match(TokenType.IDENTIFIER):
            # 可能是异常类型或异常变量名
            first_identifier = self.current_token.value
            self.advance()
            
            if self.match(TokenType.AS):
                # catch ExceptionType as e
                exception_type = first_identifier
                self.advance()  # 消费 'as'
                exception_name = self.consume(TokenType.IDENTIFIER).value
            else:
                # catch e (捕获所有异常)
                exception_name = first_identifier
        
        # 解析catch块（支持大括号语法）
        body = self.parse_block()
        
        return CatchClause(exception_type, exception_name, body)
    
    def parse_throw_statement(self) -> ThrowStatement:
        """解析throw语句"""
        self.consume(TokenType.THROW)
        exception = self.parse_expression()
        return ThrowStatement(exception)
    
    def parse_decorated_function(self) -> DecoratedFunction:
        """解析装饰器函数"""
        decorators = []
        
        # 解析所有装饰器
        while self.match(TokenType.AT):
            self.advance()  # 消费 @
            decorator_name = self.consume(TokenType.IDENTIFIER).value
            
            # 检查是否有参数
            args = []
            if self.match(TokenType.LPAREN):
                self.advance()
                if not self.match(TokenType.RPAREN):
                    args.append(self.parse_expression())
                    while self.match(TokenType.COMMA):
                        self.advance()
                        args.append(self.parse_expression())
                self.consume(TokenType.RPAREN)
            
            decorators.append(Decorator(decorator_name, args))
            self.skip_newlines()
        
        # 解析被装饰的函数
        function = self.parse_function_def()
        return DecoratedFunction(decorators, function)
    
    def parse_async_function_def(self) -> AsyncFunctionDef:
        """解析异步函数定义"""
        self.consume(TokenType.ASYNC)
        self.consume(TokenType.FUNC)
        name = self.consume(TokenType.IDENTIFIER).value
        
        self.consume(TokenType.LPAREN)
        parameters = []
        
        if not self.match(TokenType.RPAREN):
            parameters.append(self.consume(TokenType.IDENTIFIER).value)
            while self.match(TokenType.COMMA):
                self.advance()
                parameters.append(self.consume(TokenType.IDENTIFIER).value)
        
        self.consume(TokenType.RPAREN)
        
        # 支持两种语法
        if self.match(TokenType.LBRACE):
            body = self.parse_block()
        else:
            self.consume(TokenType.COLON)
            self.skip_newlines()
            self.consume(TokenType.INDENT)
            body = []
            
            while not self.match(TokenType.DEDENT, TokenType.EOF):
                if self.match(TokenType.NEWLINE, TokenType.COMMENT):
                    self.advance()
                    continue
                stmt = self.parse_statement()
                if stmt:
                    body.append(stmt)
                self.skip_newlines()
            
            if self.match(TokenType.DEDENT):
                self.advance()
        
        return AsyncFunctionDef(name, parameters, body)
    
    def parse_with_statement(self) -> WithStatement:
        """解析with语句"""
        self.consume(TokenType.WITH)
        context_expr = self.parse_expression()
        
        optional_vars = None
        if self.match(TokenType.AS):
            self.advance()
            optional_vars = self.consume(TokenType.IDENTIFIER).value
        
        # 支持两种语法
        if self.match(TokenType.LBRACE):
            body = self.parse_block()
        else:
            self.consume(TokenType.COLON)
            self.skip_newlines()
            self.consume(TokenType.INDENT)
            body = []
            
            while not self.match(TokenType.DEDENT, TokenType.EOF):
                if self.match(TokenType.NEWLINE, TokenType.COMMENT):
                    self.advance()
                    continue
                stmt = self.parse_statement()
                if stmt:
                    body.append(stmt)
                self.skip_newlines()
            
            if self.match(TokenType.DEDENT):
                self.advance()
        
        return WithStatement(context_expr, optional_vars, body)
    
    def parse_global_statement(self) -> GlobalStatement:
        """解析global语句"""
        self.consume(TokenType.GLOBAL)
        names = [self.consume(TokenType.IDENTIFIER).value]
        
        while self.match(TokenType.COMMA):
            self.advance()
            names.append(self.consume(TokenType.IDENTIFIER).value)
        
        return GlobalStatement(names)
    
    def parse_nonlocal_statement(self) -> NonlocalStatement:
        """解析nonlocal语句"""
        self.consume(TokenType.NONLOCAL)
        names = [self.consume(TokenType.IDENTIFIER).value]
        
        while self.match(TokenType.COMMA):
            self.advance()
            names.append(self.consume(TokenType.IDENTIFIER).value)
        
        return NonlocalStatement(names)
    
    def parse_assert_statement(self) -> AssertStatement:
        """解析assert语句"""
        self.consume(TokenType.ASSERT)
        test = self.parse_expression()
        
        msg = None
        if self.match(TokenType.COMMA):
            self.advance()
            msg = self.parse_expression()
        
        return AssertStatement(test, msg)
    
    def parse_del_statement(self) -> DelStatement:
        """解析del语句"""
        self.consume(TokenType.DEL)
        targets = [self.parse_expression()]
        
        while self.match(TokenType.COMMA):
            self.advance()
            targets.append(self.parse_expression())
        
        return DelStatement(targets)
    
    def parse_lambda_expression(self) -> LambdaExpression:
        """解析lambda表达式"""
        self.consume(TokenType.LAMBDA)
        
        # 解析参数列表
        parameters = []
        if not self.match(TokenType.COLON):
            parameters.append(self.consume(TokenType.IDENTIFIER).value)
            while self.match(TokenType.COMMA):
                self.advance()
                parameters.append(self.consume(TokenType.IDENTIFIER).value)
        
        self.consume(TokenType.COLON)
        
        # 解析lambda体（单个表达式）
        body = self.parse_expression()
        
        return LambdaExpression(parameters, body)
    
    def parse_yield_expression(self) -> YieldExpression:
        """解析yield表达式"""
        self.consume(TokenType.YIELD)
        
        # yield可以没有值
        value = None
        if not self.match(TokenType.NEWLINE, TokenType.SEMICOLON, TokenType.RBRACE, TokenType.RPAREN, TokenType.RBRACKET, TokenType.COMMA):
            value = self.parse_expression()
        
        return YieldExpression(value)
    
    def parse_await_expression(self) -> AwaitExpression:
        """解析await表达式"""
        self.consume(TokenType.AWAIT)
        expression = self.parse_expression()
        return AwaitExpression(expression)

def main():
    # 测试语法分析器
    test_code = '''
def greet(name):
    if name:
        print("Hello, " + name + "!")
    else:
        print("Hello, World!")
    return True

result = greet("AquaScript")
'''
    
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    print("AST:")
    print(ast)

if __name__ == "__main__":
    main()