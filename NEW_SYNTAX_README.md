# AquaScript 增强版语法指南

## 概述

AquaScript 增强版引入了全新的语法设计，使其更具独特性，同时支持Python生态系统集成。新语法保持简洁易读，但与Python有明显区别。

## 新语法特性

### 1. 函数定义

使用 `func` 关键字定义函数，支持类型注解：

```aqua
func greet(name: str) -> str:
    return "Hello, " + name + "!"

func add(a: int, b: int) -> int:
    return a + b
```

### 2. 变量声明

使用 `var` 关键字声明变量，支持类型注解：

```aqua
var name: str = "AquaScript"
var age: int = 25
var height: float = 1.75
var is_student: bool = true
var numbers: list = [1, 2, 3, 4, 5]
```

### 3. 类定义

使用 `class` 关键字定义类：

```aqua
class Person:
    func __init__(self, name: str, age: int):
        self.name = name
        self.age = age
    
    func introduce(self) -> str:
        return "I'm " + self.name + ", " + str(self.age) + " years old"
```

### 4. repeat循环

新增 `repeat` 循环（do-while风格）：

```aqua
var count: int = 0
repeat:
    print("Count: " + str(count))
    count = count + 1
while count < 5
```

### 5. switch语句

支持 `switch` 语句：

```aqua
func describe_grade(grade: str):
    switch grade:
        case "A":
            print("Excellent!")
        case "B":
            print("Good!")
        case "C":
            print("Average")
        default:
            print("Need improvement")
```

### 6. 增强的for循环

支持更灵活的for循环：

```aqua
var items: list = ["apple", "banana", "orange"]

for item in items:
    print("Fruit: " + item)

for i in range(1, 6):
    print("Number: " + str(i))
```

## Python生态系统集成

### 模块导入

可以直接导入Python标准库：

```aqua
import math
import random
from datetime import datetime

var pi_value: float = math.pi
var random_num: int = random.randint(1, 100)
var now: datetime = datetime.now()
```

### 常用模块快捷访问

内置了常用Python模块的快捷访问：

```aqua
# 数学函数
var sin_value: float = math_sin(1.57)
var sqrt_value: float = math_sqrt(16)

# 随机数
var rand_int: int = random_randint(1, 10)
var rand_choice: str = random_choice(["a", "b", "c"])

# JSON处理
var json_str: str = json_dumps({"name": "Alice", "age": 30})
var data: dict = json_loads('{"x": 10, "y": 20}')
```

### 类型系统

支持强类型检查和自动类型转换：

```aqua
var x: int = 42
var y: float = float(x)  # 类型转换
var z: str = str(x)      # 转换为字符串

# 类型检查
if isinstance(x, int):
    print("x is an integer")
```

## 与Python的区别

| 特性 | Python | AquaScript |
|------|--------|------------|
| 函数定义 | `def func():` | `func name():` |
| 变量声明 | `x = 10` | `var x: int = 10` |
| 循环 | `while condition:` | `repeat: ... while condition` |
| 条件分支 | `if/elif/else` | `switch/case/default` |
| 类型注解 | 可选 | 推荐使用 |

## 编译和运行

### 使用增强版编译器

```bash
# 编译并运行
python enhanced_aquac.py example.aqua

# 只编译
python enhanced_aquac.py -c example.aqua

# 运行字节码
python enhanced_aquac.py -r example.acode

# 交互式模式
python enhanced_aquac.py -i
```

### 示例程序

查看 `examples/new_syntax_demo.aqua` 了解完整的语法示例。

## 技术实现

### 虚拟机增强

- **PythonBridge**: 负责Python模块导入和函数调用
- **TypeSystem**: 提供类型检查和转换
- **EnhancedAquaVM**: 集成Python生态系统的虚拟机

### 编译器更新

- **词法分析器**: 新增关键字和token类型
- **语法分析器**: 支持新的AST节点类型
- **代码生成器**: 生成支持新特性的字节码

## 兼容性

- **Python版本**: 支持Python 3.6+
- **模块导入**: 支持所有Python标准库
- **第三方库**: 支持通过pip安装的包

## 未来计划

1. **包管理系统**: 类似npm/pip的包管理
2. **更多语法糖**: 简化常用操作
3. **性能优化**: JIT编译支持
4. **IDE集成**: 语法高亮和智能提示
5. **调试工具**: 断点调试和性能分析

## 贡献

欢迎提交Issue和Pull Request来改进AquaScript！

---

*AquaScript - 简洁、强大、Python兼容的编程语言*