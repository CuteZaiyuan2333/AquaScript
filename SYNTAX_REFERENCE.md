# AquaScript 语法规则参考

## 📖 语法概述

AquaScript 采用类似 Python 的简洁语法，同时引入了一些独特的语法特性。本文档详细描述了 AquaScript 的完整语法规则。

## 🔤 词法规则

### 标识符
- 以字母或下划线开头
- 可包含字母、数字、下划线
- 区分大小写
- 不能是保留字

```aqua
# 有效标识符
var name
var _private
var user_name
var userName
var value123

# 无效标识符
var 123name    # 不能以数字开头
var if         # 不能是保留字
```

### 保留字
```
and, or, not, if, elif, else, while, for, in, func, return, var, true, false, null
```

### 字面量

#### 数字字面量
```aqua
# 整数
var integer = 42
var negative = -123
var zero = 0

# 浮点数
var pi = 3.14159
var scientific = 1.23e-4
var negative_float = -2.5
```

#### 字符串字面量
```aqua
# 单引号字符串
var single = 'Hello World'

# 双引号字符串
var double = "Hello World"

# 转义字符
var escaped = "Hello\nWorld\t!"

# f-string 格式化
var name = "Alice"
var greeting = f"Hello, {name}!"
var calculation = f"2 + 3 = {2 + 3}"
```

#### 布尔字面量
```aqua
var is_true = true
var is_false = false
```

#### 空值字面量
```aqua
var empty = null
```

### 运算符

#### 算术运算符
```aqua
+    # 加法
-    # 减法
*    # 乘法
/    # 除法
%    # 取模
```

#### 比较运算符
```aqua
==   # 等于
!=   # 不等于
<    # 小于
>    # 大于
<=   # 小于等于
>=   # 大于等于
```

#### 逻辑运算符
```aqua
and  # 逻辑与
or   # 逻辑或
not  # 逻辑非
```

#### 赋值运算符
```aqua
=    # 赋值
```

### 分隔符
```aqua
(    # 左圆括号
)    # 右圆括号
[    # 左方括号
]    # 右方括号
{    # 左大括号
}    # 右大括号
,    # 逗号
:    # 冒号
```

### 注释
```aqua
# 单行注释，从 # 开始到行末
var x = 10  # 行末注释
```

## 🏗️ 语法结构

### 程序结构
```bnf
program ::= statement*

statement ::= simple_statement | compound_statement

simple_statement ::= expression_statement
                   | assignment_statement
                   | return_statement

compound_statement ::= function_definition
                     | if_statement
                     | while_statement
                     | for_statement
```

### 表达式语法

#### 基础表达式
```bnf
expression ::= logical_or

logical_or ::= logical_and ('or' logical_and)*

logical_and ::= equality ('and' equality)*

equality ::= comparison (('==' | '!=') comparison)*

comparison ::= term (('<' | '>' | '<=' | '>=') term)*

term ::= factor (('+' | '-') factor)*

factor ::= unary (('*' | '/' | '%') unary)*

unary ::= ('not' | '-') unary | primary

primary ::= literal
          | identifier
          | '(' expression ')'
          | list_literal
          | dict_literal
          | function_call
          | subscript
          | f_string
```

#### 字面量表达式
```bnf
literal ::= NUMBER | STRING | BOOLEAN | NULL

list_literal ::= '[' (expression (',' expression)*)? ']'

dict_literal ::= '{' (dict_pair (',' dict_pair)*)? '}'

dict_pair ::= expression ':' expression

f_string ::= 'f' STRING_WITH_EXPRESSIONS
```

### 语句语法

#### 赋值语句
```bnf
assignment_statement ::= 'var' identifier '=' expression
                       | identifier '=' expression
                       | subscript '=' expression
```

#### 函数定义
```bnf
function_definition ::= 'func' identifier '(' parameter_list? ')' block

parameter_list ::= identifier (',' identifier)*

block ::= '{' statement* '}'
```

#### 控制流语句
```bnf
if_statement ::= 'if' expression block ('elif' expression block)* ('else' block)?

while_statement ::= 'while' expression block

for_statement ::= 'for' identifier 'in' expression block

return_statement ::= 'return' expression?
```

#### 函数调用
```bnf
function_call ::= identifier '(' argument_list? ')'

argument_list ::= expression (',' expression)*
```

#### 下标访问
```bnf
subscript ::= primary '[' expression ']'
```

## 📝 语法示例

### 变量声明和赋值
```aqua
# 变量声明
var name = "AquaScript"
var version = 2.0
var features = ["简洁", "高效", "易学"]

# 变量赋值
name = "AquaScript 2.0"
version = 2.1

# 复合赋值
var person = {"name": "Alice", "age": 30}
person["age"] = 31
```

### 函数定义和调用
```aqua
# 简单函数
func greet(name) {
    return f"Hello, {name}!"
}

# 带多个参数的函数
func calculate_area(width, height) {
    return width * height
}

# 递归函数
func factorial(n) {
    if n <= 1 {
        return 1
    } else {
        return n * factorial(n - 1)
    }
}

# 函数调用
var message = greet("World")
var area = calculate_area(10, 20)
var fact = factorial(5)
```

### 控制流结构
```aqua
# if-elif-else 语句
func grade_to_letter(score) {
    if score >= 90 {
        return "A"
    } elif score >= 80 {
        return "B"
    } elif score >= 70 {
        return "C"
    } elif score >= 60 {
        return "D"
    } else {
        return "F"
    }
}

# while 循环
func count_down(n) {
    while n > 0 {
        print(f"倒计时: {n}")
        n = n - 1
    }
    print("时间到!")
}

# for 循环
func print_list(items) {
    for item in items {
        print(f"项目: {item}")
    }
}

func print_dict(data) {
    for key in data {
        print(f"{key}: {data[key]}")
    }
}
```

### 数据结构操作
```aqua
# 列表操作
var numbers = [1, 2, 3, 4, 5]
var first = numbers[0]
var last = numbers[4]
numbers[0] = 10

# 嵌套列表
var matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]
var center = matrix[1][1]  # 5

# 字典操作
var person = {
    "name": "Alice",
    "age": 30,
    "hobbies": ["reading", "coding", "music"]
}

var name = person["name"]
person["age"] = 31
person["city"] = "Beijing"

# 嵌套字典
var config = {
    "database": {
        "host": "localhost",
        "port": 5432,
        "credentials": {
            "username": "admin",
            "password": "secret"
        }
    },
    "app": {
        "name": "MyApp",
        "version": "1.0"
    }
}

var db_host = config["database"]["host"]
var username = config["database"]["credentials"]["username"]
```

### 字符串格式化
```aqua
# 基础 f-string
var name = "Alice"
var age = 30
var intro = f"我是 {name}，今年 {age} 岁"

# 表达式计算
var a = 10
var b = 20
var result = f"{a} + {b} = {a + b}"

# 复杂格式化
var person = {"name": "Bob", "score": 95}
var report = f"学生 {person['name']} 的成绩是 {person['score']} 分"

# 函数调用在 f-string 中
func get_grade(score) {
    if score >= 90 {
        return "优秀"
    } elif score >= 80 {
        return "良好"
    } else {
        return "及格"
    }
}

var score = 92
var evaluation = f"成绩 {score} 分，评级：{get_grade(score)}"
```

## 🔍 语法特性

### 作用域规则
- **全局作用域**: 在函数外定义的变量
- **局部作用域**: 在函数内定义的变量
- **变量查找**: 先查找局部作用域，再查找全局作用域

```aqua
var global_var = "全局变量"

func test_scope() {
    var local_var = "局部变量"
    print(global_var)  # 可以访问全局变量
    print(local_var)   # 访问局部变量
}

# print(local_var)  # 错误：无法访问局部变量
```

### 类型系统
- **动态类型**: 变量类型在运行时确定
- **强类型**: 不允许隐式类型转换
- **类型检查**: 运行时进行类型检查

```aqua
var x = 10        # 整数类型
x = "hello"       # 可以改变类型
# var y = x + 5   # 错误：字符串不能与数字相加
```

### 表达式求值
- **短路求值**: 逻辑运算符支持短路求值
- **运算符优先级**: 遵循数学运算优先级
- **结合性**: 大部分运算符左结合

```aqua
# 短路求值
var result = false and expensive_function()  # expensive_function() 不会被调用

# 运算符优先级
var x = 2 + 3 * 4    # 结果是 14，不是 20
var y = (2 + 3) * 4  # 结果是 20
```

### 错误处理
- **语法错误**: 编译时检测
- **运行时错误**: 执行时检测和报告
- **类型错误**: 运行时类型检查

```aqua
# 语法错误示例（编译时检测）
# if condition {  # 缺少条件表达式

# 运行时错误示例
var list = [1, 2, 3]
# var item = list[10]  # 索引超出范围

# 类型错误示例
var x = "hello"
# var y = x + 5  # 字符串不能与数字相加
```

## 📋 语法约定

### 代码风格建议
1. **缩进**: 使用 4 个空格缩进
2. **命名**: 使用 snake_case 命名变量和函数
3. **空格**: 运算符前后加空格
4. **注释**: 适当添加注释说明

```aqua
# 推荐的代码风格
func calculate_total_price(items, tax_rate) {
    var subtotal = 0
    
    # 计算小计
    for item in items {
        subtotal = subtotal + item["price"]
    }
    
    # 计算总价（含税）
    var total = subtotal * (1 + tax_rate)
    return total
}
```

### 最佳实践
1. **函数设计**: 保持函数简洁，单一职责
2. **变量命名**: 使用有意义的变量名
3. **错误处理**: 适当处理可能的错误情况
4. **代码组织**: 合理组织代码结构

```aqua
# 良好的函数设计示例
func is_prime(number) {
    if number < 2 {
        return false
    }
    
    var i = 2
    while i * i <= number {
        if number % i == 0 {
            return false
        }
        i = i + 1
    }
    
    return true
}

func find_primes_in_range(start, end) {
    var primes = []
    var current = start
    
    while current <= end {
        if is_prime(current) {
            # 这里应该有添加到列表的操作
            # primes.append(current)  # 待实现
        }
        current = current + 1
    }
    
    return primes
}
```

## 🚀 语法扩展

### 计划中的语法特性
1. **元组支持**: `(1, 2, 3)`
2. **列表推导式**: `[x * 2 for x in numbers]`
3. **异常处理**: `try/catch/finally`
4. **模块导入**: `import module`
5. **类定义**: `class MyClass`

### 实验性语法
1. **类型注解**: `var name: str = "Alice"`
2. **装饰器**: `@decorator`
3. **生成器**: `yield` 关键字
4. **异步支持**: `async/await`

这些特性正在开发中，将在未来版本中逐步实现。