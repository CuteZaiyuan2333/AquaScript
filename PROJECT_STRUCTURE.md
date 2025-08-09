# AquaScript 项目结构

本文档描述了 AquaScript 项目的整理后的目录结构和文件组织。

## 📁 项目根目录

### 📚 文档文件
- `README.md` - 项目主要介绍和快速开始指南
- `COMPREHENSIVE_DOCUMENTATION.md` - 完整的项目文档
- `DEVELOPMENT_PLAN.md` - 开发计划和路线图
- `PROJECT_STATUS.md` - 项目状态总结
- `SYNTAX_REFERENCE.md` - 语法规则参考
- `DICT_FEATURES.md` - 字典功能详细文档
- `FEATURES_DEMO.md` - 功能演示总结
- `NEW_SYNTAX_README.md` - 新语法特性指南
- `PERFORMANCE_ROADMAP.md` - 性能优化路线图
- `PROJECT_STRUCTURE.md` - 本文档

### 🛠️ 核心组件

#### `compiler/` - 编译器
- `lexer.py` - 词法分析器
- `parser.py` - 语法分析器
- `codegen.py` - 代码生成器
- `aquac.py` - 编译器主程序

#### `vm/` - 虚拟机
- `aquavm.py` - 标准虚拟机
- `optimized_aquavm.py` - 性能优化版本
- `enhanced_aquavm.py` - 增强功能版本
- `cython_aquavm.pyx` - Cython 加速版本
- `fast_vm.c` - C 扩展模块
- `setup_cython.py` - Cython 编译脚本
- `rust_vm/` - Rust 高性能版本（开发中）

### 📝 示例程序

#### `examples/` - 官方示例
- `hello.aqua` - Hello World 示例
- `fibonacci.aqua` - 斐波那契数列
- `new_syntax_demo.aqua` - 新语法特性演示

#### 根目录示例程序
- `calculator.aqua` - 计算器程序
- `number_game.aqua` - 数字猜测游戏
- `project_manager.aqua` - 项目管理工具
- `showcase.aqua` - 功能展示程序
- `math_library.aqua` - 数学库示例

### 🧪 测试文件

#### `test_files/` - 测试套件
```
test_files/
├── README.md                    # 测试文件说明
├── basic_tests/                 # 基础功能测试
│   ├── test_simple.aqua        # 简单语法测试
│   ├── test_boolean.aqua       # 布尔值测试
│   └── test_condition_simple.aqua # 条件语句测试
├── feature_tests/               # 功能特性测试
│   ├── test_dict.aqua          # 字典功能测试
│   ├── test_lists.aqua         # 列表功能测试
│   ├── test_fstring.aqua       # 字符串格式化测试
│   ├── test_tuple.aqua         # 元组功能测试
│   ├── test_math_lib.aqua      # 数学库测试
│   ├── test_exception.aqua     # 异常处理测试
│   └── test_list_comprehension.aqua # 列表推导式测试
├── debug_tests/                 # 调试测试
│   ├── test_condition_debug.aqua # 条件调试测试
│   └── test_debug_simple.aqua   # 简单调试测试
└── performance_tests/           # 性能测试
```

#### `benchmark_tests/` - 性能基准测试
- `fibonacci.aqua` - 斐波那契性能测试
- `function_calls.aqua` - 函数调用性能测试
- `loop_test.aqua` - 循环性能测试
- `string_concat.aqua` - 字符串连接性能测试

#### `benchmarks/` - 性能测试工具
- `performance_test.py` - 性能测试套件

### 🔧 开发工具

#### `tools/` - 实用工具
- `apack.py` - 项目打包工具

#### `editor/` - 集成开发环境
- `app.py` - Web 编辑器后端
- `desktop_app.py` - 桌面版编辑器
- `static/` - 前端资源
- `templates/` - HTML 模板
- `启动AquaScript编辑器.bat` - Windows 启动脚本
- `启动AquaScript编辑器.ps1` - PowerShell 启动脚本

#### `tests/` - 单元测试
- `test_lexer.py` - 词法分析器单元测试

### 📚 标准库

#### `stdlib/` - 标准库模块
- `math.aqua` - 数学函数库

### 🏗️ 构建和配置
- `build.py` - 项目构建脚本
- `enhanced_aquac.py` - 增强编译器
- `.venv/` - Python 虚拟环境

## 🧹 清理说明

### 已删除的文件
- 调试和分析脚本：`analyze_*.py`, `debug_*.py`, `check_*.py`
- 重复的测试文件：多个版本的简单测试
- 临时文件：空文件夹、过时的测试文件
- 重复的示例：根目录中的重复 hello 文件

### 文件整理原则
1. **功能分类**：按功能将文件分类到对应目录
2. **去重**：删除重复和过时的文件
3. **标准化**：统一命名规范和目录结构
4. **文档化**：为每个目录提供说明文档

## 📊 项目统计

### 代码文件统计
- **编译器**：4 个核心文件
- **虚拟机**：6 个版本（标准、优化、增强等）
- **示例程序**：8 个完整示例
- **测试文件**：20+ 个测试用例
- **文档文件**：10 个详细文档

### 目录结构优势
- ✅ **清晰分类**：功能明确的目录结构
- ✅ **易于维护**：相关文件集中管理
- ✅ **便于扩展**：预留了扩展空间
- ✅ **文档完善**：每个组件都有说明

## 🚀 下一步计划

1. **持续整理**：定期清理临时文件和重复代码
2. **文档更新**：保持文档与代码同步
3. **测试完善**：补充缺失的测试用例
4. **工具改进**：优化开发和构建工具