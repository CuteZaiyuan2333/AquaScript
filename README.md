# AquaScript Programming Language

AquaScript是一种简洁的编程语言，采用类似Python的语法设计，通过AquaVM虚拟机运行字节码。

## 特性

- 🐍 **Python风格语法**：使用缩进而非大括号，无需分号
- 🚀 **虚拟机架构**：基于AquaVM运行.acode字节码
- 📦 **打包系统**：支持.apack格式的应用程序包
- 🔧 **简单易学**：专注于简洁性和可读性

## 项目结构

```
AquaScript/
├── compiler/          # AquaScript编译器
├── vm/               # AquaVM虚拟机
├── examples/         # 示例代码
├── test_files/       # 测试文件（按功能分类）
│   ├── basic_tests/      # 基础功能测试
│   ├── feature_tests/    # 语言特性测试
│   ├── performance_tests/ # 性能基准测试
│   └── debug_tests/      # 调试和综合测试
├── tests/           # 单元测试
├── tools/           # 开发工具
├── benchmark_tests/ # 基准测试用例
└── benchmarks/      # 性能测试脚本
```

## 📦 获取AquaScript

### GitHub仓库
- **仓库地址**: https://github.com/CuteZaiyuan2333/AquaScript
- **克隆项目**: `git clone https://github.com/CuteZaiyuan2333/AquaScript.git`

## 快速开始

### 编译AquaScript代码
```bash
python compiler/aquac.py example.aqua -o example.acode
```

### 运行字节码
```bash
python vm/aquavm.py example.acode
```

### 打包应用
```bash
python tools/apack.py example.acode -o example.apack
```

### 运行测试
```bash
# 运行基础功能测试
python vm/optimized_aquavm.py test_files/basic_tests/test_simple.acode

# 运行功能特性测试
python vm/optimized_aquavm.py test_files/feature_tests/test_oop.acode

# 运行性能测试
python vm/optimized_aquavm.py test_files/performance_tests/test_performance.acode
```

## 语法示例

```aquascript
# 变量定义
var name = "AquaScript"
var version = 1.0

# 函数定义
func greet(name):
    print("Hello, " + name + "!")
    return name

# 条件语句
if version >= 1.0:
    print("AquaScript is ready!")
else:
    print("Still in development")

# 循环
for i in range(5):
    print("Count: " + str(i))

# 调用函数
greet("World")
```

## 开发状态

### 已完成功能 ✅
- 基础语法解析（变量、函数、控制流）
- 数据类型支持（数字、字符串、布尔值、列表、**字典**）
- 运算符系统（算术、比较、逻辑）
- 函数定义和调用
- 条件语句（if/elif/else）
- 循环语句（while/for）- **已修复 for 循环实现**
- 字符串格式化（f-string）
- **字典完整支持**（嵌套字典、混合数据类型、键值对操作）
- 基础虚拟机和字节码执行
- 编译器工具链
- 错误处理和调试支持
- **性能优化版本**（optimized_aquavm.py）

### 进行中功能 🔄
- 异常处理机制（try/catch/finally）
- 模块系统（import/from）
- 元组数据类型
- Cython 和 Rust 性能优化版本

## 📚 文档

### 核心文档
- **[综合文档](COMPREHENSIVE_DOCUMENTATION.md)** - 完整的项目概述和使用指南
- **[语法规则参考](SYNTAX_REFERENCE.md)** - 详细的语法规则和示例
- **[开发计划](DEVELOPMENT_PLAN.md)** - 开发路线图和进度跟踪
- **[项目结构](PROJECT_STRUCTURE.md)** - 整理后的项目目录结构说明

### 功能文档
- **[字典功能文档](DICT_FEATURES.md)** - 字典数据类型的完整使用指南
- **[功能演示总结](FEATURES_DEMO.md)** - 所有示例程序和功能展示
- **[新语法指南](NEW_SYNTAX_README.md)** - 增强版语法特性

### 技术文档
- **[性能优化路线图](PERFORMANCE_ROADMAP.md)** - 性能优化计划和实现

### 项目管理
- **[清理总结](CLEANUP_SUMMARY.md)** - 项目整理和代码清理工作总结