# AquaScript 测试文件组织结构

本文件夹包含了 AquaScript 项目的所有测试文件，按功能分类组织。

## 📁 文件夹结构

### `basic_tests/` - 基础功能测试
包含最基本的语言功能测试：
- `test_simple.*` - 基础语法测试
- `test_boolean.*` - 布尔值测试
- `test_condition_simple.*` - 条件语句测试
- `test_simple_vm.*` - 虚拟机基础测试
- `simple_test.aqua` - 简单测试用例
- `basic_test.*` - 基础字节码测试

### `feature_tests/` - 功能特性测试
包含高级语言功能测试：
- `test_dict.*` - 字典功能测试
- `test_lists.*` - 列表高级操作测试
- `test_fstring.*` - 字符串格式化测试
- `test_tuple.*` - 元组功能测试
- `test_math_lib.*` - 数学库测试
- `test_exception.*` - 异常处理测试
- `test_list_comprehension.*` - 列表推导式测试
- `advanced_dict_test.*` - 高级字典测试
- `nested_dict_test.*` - 嵌套字典测试
- `test_math.*` - 数学运算测试

### `performance_tests/` - 性能测试
包含性能基准测试和优化验证：
- `test_performance.*` - 综合性能测试
- `test_benchmark.*` - 基准测试

### `debug_tests/` - 调试和错误测试
包含调试工具和错误处理测试：
- `test_condition_debug.*` - 条件判断调试测试
- `test_debug_simple.*` - 简单调试测试
- `test_errors.*` - 错误处理测试
- `test_negative.*` - 负面测试用例
- `debug_*.py` - 调试脚本
- `test_indent_issue.py` - 缩进问题调试

## 🚀 运行测试

### 编译测试文件
```bash
# 编译单个测试文件
python compiler/aquac.py test_files/basic_tests/test_simple.aqua

# 批量编译某个分类的测试
python compiler/aquac.py test_files/feature_tests/*.aqua
```

### 运行测试
```bash
# 运行编译后的测试
python vm/optimized_aquavm.py test_files/basic_tests/test_simple.acode

# 运行性能测试
python vm/optimized_aquavm.py test_files/performance_tests/test_performance.acode
```

### 调试测试
```bash
# 使用调试脚本
python test_files/debug_tests/debug_bytecode.py test_files/basic_tests/test_simple.acode
python test_files/debug_tests/debug_parse.py test_files/basic_tests/test_simple.aqua
```

## 📝 测试文件命名规范

- `.aqua` 文件：AquaScript 源代码
- `.acode` 文件：编译后的字节码
- `test_*.py` 文件：Python 调试脚本
- `debug_*.py` 文件：调试工具脚本

## 🔧 添加新测试

1. 根据测试类型选择合适的文件夹
2. 遵循现有的命名规范
3. 同时提供 `.aqua` 源文件和编译后的 `.acode` 文件
4. 在相应的文件夹中添加测试说明

## 📊 测试覆盖范围

- ✅ 基础语法和数据类型
- ✅ 函数定义和调用
- ✅ 面向对象编程
- ✅ 控制流（条件、循环）
- ✅ 变量作用域
- ✅ 列表和字符串操作
- ✅ 错误处理
- ✅ 性能基准测试