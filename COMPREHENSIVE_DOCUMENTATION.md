# AquaScript 综合文档

## 📋 项目概述

AquaScript 是一个功能完整的编程语言，具有以下特点：
- 类似 Python 的简洁语法
- 基于栈的虚拟机架构
- 完整的编译工具链
- 丰富的数据类型支持
- 高性能的字节码执行

## 🎯 当前开发状态

### ✅ 已完成功能

#### 核心语言特性
- **变量系统**: 支持动态类型变量声明和赋值
- **数据类型**: 整数、浮点数、字符串、布尔值、列表、字典
- **运算符**: 算术运算（+、-、*、/、%）、比较运算、逻辑运算
- **控制流**: if/elif/else 条件语句、while 循环、for 循环
- **函数**: 函数定义、调用、参数传递、返回值
- **字符串**: f-string 格式化、字符串操作
- **注释**: 单行注释支持（#）

#### 高级特性
- **字典**: 完整的字典支持，包括嵌套字典、混合数据类型
- **列表**: 列表创建、访问、修改
- **递归**: 递归函数调用支持
- **作用域**: 局部变量和全局变量管理
- **错误处理**: 运行时错误检测和报告

#### 编译器架构
- **词法分析器**: 完整的 token 识别和解析
- **语法分析器**: AST 构建和语法验证
- **代码生成器**: 字节码生成和优化
- **字节码**: 完整的指令集和虚拟机

#### 虚拟机特性
- **基于栈的执行**: 高效的栈操作
- **指令执行**: 完整的操作码支持
- **内存管理**: 自动内存管理
- **性能统计**: 执行统计和性能监控

### 🔄 最近修复的问题

#### for 循环修复 (已完成)
- **问题**: 编译器生成基于索引的循环，导致类型错误
- **解决方案**: 重构为使用 `GET_ITER` 和 `FOR_ITER` 操作码
- **验证**: 通过字节码分析和运行测试确认修复成功

## 📖 语法规则完整指南

### 1. 基础语法

#### 变量声明
```aqua
# 基础变量声明
var name = "AquaScript"
var version = 2.0
var is_ready = true

# 带类型注解（新语法）
var name: str = "AquaScript"
var version: float = 2.0
var is_ready: bool = true
```

#### 数据类型
```aqua
# 基本类型
var number = 42          # 整数
var pi = 3.14159         # 浮点数
var text = "Hello"       # 字符串
var flag = true          # 布尔值

# 复合类型
var numbers = [1, 2, 3, 4, 5]                    # 列表
var person = {"name": "Alice", "age": 30}        # 字典
```

### 2. 运算符

#### 算术运算符
```aqua
var a = 10
var b = 3

var sum = a + b          # 加法: 13
var diff = a - b         # 减法: 7
var product = a * b      # 乘法: 30
var quotient = a / b     # 除法: 3.333...
var remainder = a % b    # 取模: 1
```

#### 比较运算符
```aqua
var x = 5
var y = 10

var equal = x == y       # 等于: false
var not_equal = x != y   # 不等于: true
var less = x < y         # 小于: true
var greater = x > y      # 大于: false
var less_eq = x <= y     # 小于等于: true
var greater_eq = x >= y  # 大于等于: false
```

#### 逻辑运算符
```aqua
var a = true
var b = false

var and_result = a and b    # 逻辑与: false
var or_result = a or b      # 逻辑或: true
var not_result = not a      # 逻辑非: false
```

### 3. 控制流

#### 条件语句
```aqua
# 基础 if 语句
if condition {
    print("条件为真")
}

# if-else 语句
if score >= 60 {
    print("及格")
} else {
    print("不及格")
}

# if-elif-else 语句
if score >= 90 {
    print("优秀")
} elif score >= 80 {
    print("良好")
} elif score >= 60 {
    print("及格")
} else {
    print("不及格")
}
```

#### 循环语句
```aqua
# while 循环
var i = 0
while i < 5 {
    print(f"计数: {i}")
    i = i + 1
}

# for 循环（遍历列表）
var fruits = ["apple", "banana", "orange"]
for fruit in fruits {
    print(f"水果: {fruit}")
}

# for 循环（遍历字典）
var person = {"name": "Alice", "age": 30}
for key in person {
    print(f"{key}: {person[key]}")
}
```

### 4. 函数

#### 函数定义
```aqua
# 基础函数
func greet(name) {
    return f"Hello, {name}!"
}

# 带类型注解的函数（新语法）
func add(a: int, b: int) -> int {
    return a + b
}

# 无返回值函数
func print_info(name, age) {
    print(f"姓名: {name}")
    print(f"年龄: {age}")
}
```

#### 函数调用
```aqua
# 调用函数
var message = greet("World")
var sum = add(5, 3)
print_info("Alice", 25)

# 递归函数
func factorial(n) {
    if n <= 1 {
        return 1
    } else {
        return n * factorial(n - 1)
    }
}

var result = factorial(5)  # 120
```

### 5. 数据结构

#### 列表操作
```aqua
# 创建列表
var numbers = [1, 2, 3, 4, 5]
var mixed = [1, "hello", true, 3.14]

# 访问元素
var first = numbers[0]      # 1
var last = numbers[4]       # 5

# 修改元素
numbers[0] = 10            # [10, 2, 3, 4, 5]

# 嵌套列表
var matrix = [[1, 2], [3, 4], [5, 6]]
var element = matrix[1][0]  # 3
```

#### 字典操作
```aqua
# 创建字典
var person = {"name": "Alice", "age": 30, "city": "Beijing"}
var empty_dict = {}

# 访问元素
var name = person["name"]   # "Alice"
var age = person["age"]     # 30

# 修改和添加元素
person["age"] = 31          # 修改现有键
person["job"] = "Engineer"  # 添加新键

# 嵌套字典
var config = {
    "database": {
        "host": "localhost",
        "port": 5432
    },
    "app": {
        "name": "MyApp",
        "version": "1.0"
    }
}

var host = config["database"]["host"]  # "localhost"
```

### 6. 字符串操作

#### 字符串格式化
```aqua
# f-string 格式化
var name = "Alice"
var age = 30
var message = f"我是 {name}，今年 {age} 岁"

# 表达式在 f-string 中
var a = 5
var b = 3
var result = f"{a} + {b} = {a + b}"

# 复杂格式化
var person = {"name": "Bob", "score": 95}
var info = f"学生 {person['name']} 的成绩是 {person['score']} 分"
```

#### 字符串连接
```aqua
var first = "Hello"
var second = "World"
var combined = first + ", " + second + "!"  # "Hello, World!"
```

### 7. 注释
```aqua
# 这是单行注释

var x = 10  # 行末注释

# 多行注释需要每行都用 #
# 这是第一行注释
# 这是第二行注释
```

## 🏗️ 项目架构

### 目录结构
```
AquaScript/
├── compiler/           # 编译器模块
│   ├── lexer.py       # 词法分析器
│   ├── parser.py      # 语法分析器
│   ├── codegen.py     # 代码生成器
│   └── aquac.py       # 编译器主程序
├── vm/                # 虚拟机模块
│   ├── aquavm.py      # 标准虚拟机
│   ├── optimized_aquavm.py  # 优化虚拟机
│   └── cython_aquavm.pyx    # Cython 加速版本
├── examples/          # 示例程序
├── test_files/        # 测试文件
├── tools/             # 工具程序
├── stdlib/            # 标准库
└── editor/            # 集成开发环境
```

### 编译流程
1. **词法分析**: 源代码 → Token 流
2. **语法分析**: Token 流 → AST（抽象语法树）
3. **代码生成**: AST → 字节码
4. **虚拟机执行**: 字节码 → 程序运行

### 字节码指令集
- **栈操作**: LOAD_CONST, STORE_LOCAL, LOAD_LOCAL
- **算术运算**: ADD, SUB, MUL, DIV, MOD
- **比较运算**: EQ, NE, LT, GT, LE, GE
- **逻辑运算**: AND, OR, NOT
- **控制流**: JUMP, JUMP_IF_FALSE, JUMP_IF_TRUE
- **函数调用**: CALL_FUNCTION, RETURN
- **数据结构**: BUILD_LIST, BUILD_DICT, GET_ITEM, SET_ITEM
- **迭代器**: GET_ITER, FOR_ITER

## 🚀 开发路线图

### 第一阶段：核心语言特性完善 (已完成 80%)
- ✅ 异常处理基础框架
- ✅ 字典功能完全实现
- ⏳ 元组数据类型
- ⏳ 模块系统

### 第二阶段：高级语言特性 (计划中)
- 🔄 类和对象系统
- 🔄 继承和多态
- 🔄 装饰器
- 🔄 生成器和迭代器

### 第三阶段：标准库建设 (计划中)
- 🔄 文件操作模块
- 🔄 网络通信模块
- 🔄 日期时间模块
- 🔄 正则表达式模块

### 第四阶段：性能优化 (进行中)
- ✅ Python 优化版本
- 🔄 Cython 加速版本
- 🔄 Rust 高性能版本
- 🔄 JIT 编译器

### 第五阶段：开发工具与生态 (计划中)
- 🔄 包管理器
- 🔄 调试器
- 🔄 性能分析器
- 🔄 IDE 插件

## 📊 性能指标

### 当前性能
- **编译速度**: 快速编译，支持大型项目
- **执行速度**: 300,000 - 700,000 指令/秒
- **内存使用**: 高效的内存管理
- **启动时间**: 快速启动，低延迟

### 性能优化目标
- **阶段一**: 2-5x 性能提升（Python 优化）
- **阶段二**: 10-20x 性能提升（Cython）
- **阶段三**: 50-100x 性能提升（Rust）

## 🧪 测试覆盖

### 功能测试
- ✅ 基础语法测试
- ✅ 数据类型测试
- ✅ 控制流测试
- ✅ 函数调用测试
- ✅ 字典操作测试
- ✅ 字符串格式化测试

### 性能测试
- ✅ 基准测试套件
- ✅ 内存使用测试
- ✅ 执行速度测试
- ✅ 编译速度测试

### 集成测试
- ✅ 端到端测试
- ✅ 复杂程序测试
- ✅ 错误处理测试

## 🔧 开发工具

### 编译器工具
- `aquac.py`: 主编译器
- `enhanced_aquac.py`: 增强编译器
- `build.py`: 构建工具

### 虚拟机工具
- `aquavm.py`: 标准虚拟机
- `debug_vm.py`: 调试虚拟机
- `debug_bytecode.py`: 字节码分析器

### 开发辅助工具
- `apack.py`: 打包工具
- `performance_test.py`: 性能测试
- 集成开发环境（Web 版和桌面版）

## 📚 示例程序

### 基础示例
- `hello.aqua`: 基础语法演示
- `test_math_simple.aqua`: 数学运算
- `test_lists_simple.aqua`: 列表操作

### 高级示例
- `calculator.aqua`: 科学计算器
- `number_game.aqua`: 数字猜谜游戏
- `project_manager.aqua`: 项目管理系统

### 功能演示
- `showcase.aqua`: 综合功能展示
- `math_library.aqua`: 数学函数库
- `dict_comprehensive_test.aqua`: 字典功能测试

## 🎯 使用指南

### 快速开始
1. **编译程序**:
   ```bash
   python compiler/aquac.py your_program.aqua
   ```

2. **运行程序**:
   ```bash
   python vm/aquavm.py your_program.acode
   ```

3. **一键编译运行**:
   ```bash
   python build.py your_program.aqua
   ```

### 开发环境
- **Web 编辑器**: 启动 `editor/app.py`
- **桌面编辑器**: 运行 `editor/desktop_app.py`
- **命令行工具**: 使用编译器和虚拟机工具

## 📈 项目统计

### 代码规模
- **总代码行数**: 约 15,000 行
- **核心编译器**: 约 3,000 行
- **虚拟机**: 约 2,000 行
- **测试代码**: 约 5,000 行
- **示例程序**: 约 3,000 行
- **文档**: 约 2,000 行

### 功能完成度
- **核心语言特性**: 95% 完成
- **标准库**: 20% 完成
- **开发工具**: 70% 完成
- **性能优化**: 40% 完成
- **文档**: 85% 完成

## 🔮 未来展望

AquaScript 正在成为一个功能完整、性能优异的编程语言。我们的目标是：

1. **完善语言特性**: 实现所有现代编程语言的核心功能
2. **提升性能**: 达到接近 Java/C# 的执行性能
3. **丰富生态**: 建设完整的标准库和第三方包生态
4. **优化体验**: 提供优秀的开发工具和调试体验
5. **扩展应用**: 支持 Web 开发、系统编程、数据科学等多个领域

AquaScript 将继续发展，成为一个实用、高效、易学的现代编程语言。