"""
增强版AquaVM虚拟机
支持Python生态系统集成
"""

import struct
import json
import sys
import os
import importlib
import types
from typing import List, Dict, Any, Optional, Callable, Union
from enum import Enum

# 导入原始虚拟机
from .aquavm import AquaVM, OpCode, AquaFunction, CallFrame

class PythonBridge:
    """Python生态系统桥接器"""
    
    def __init__(self):
        self.imported_modules = {}
        self.python_objects = {}
    
    def import_module(self, module_name: str, items: Optional[List[str]] = None):
        """导入Python模块"""
        try:
            if module_name not in self.imported_modules:
                # 导入模块
                module = importlib.import_module(module_name)
                self.imported_modules[module_name] = module
            
            module = self.imported_modules[module_name]
            
            if items is None:
                # 导入整个模块
                return module
            else:
                # 导入指定项目
                result = {}
                for item in items:
                    if hasattr(module, item):
                        result[item] = getattr(module, item)
                    else:
                        raise AttributeError(f"Module '{module_name}' has no attribute '{item}'")
                return result
        
        except ImportError as e:
            raise ImportError(f"Cannot import module '{module_name}': {e}")
    
    def call_python_function(self, func, args):
        """调用Python函数"""
        try:
            # 转换AquaScript参数为Python参数
            python_args = [self.aqua_to_python(arg) for arg in args]
            result = func(*python_args)
            # 转换Python结果为AquaScript值
            return self.python_to_aqua(result)
        except Exception as e:
            raise RuntimeError(f"Error calling Python function: {e}")
    
    def aqua_to_python(self, value):
        """将AquaScript值转换为Python值"""
        if isinstance(value, (int, float, str, bool)) or value is None:
            return value
        elif isinstance(value, list):
            return [self.aqua_to_python(item) for item in value]
        elif isinstance(value, dict):
            return {k: self.aqua_to_python(v) for k, v in value.items()}
        else:
            return value
    
    def python_to_aqua(self, value):
        """将Python值转换为AquaScript值"""
        if isinstance(value, (int, float, str, bool)) or value is None:
            return value
        elif isinstance(value, (list, tuple)):
            return [self.python_to_aqua(item) for item in value]
        elif isinstance(value, dict):
            return {k: self.python_to_aqua(v) for k, v in value.items()}
        elif callable(value):
            # 包装Python函数
            return PythonFunctionWrapper(value, self)
        else:
            # 包装Python对象
            return PythonObjectWrapper(value, self)

class PythonFunctionWrapper:
    """Python函数包装器"""
    
    def __init__(self, func, bridge: PythonBridge):
        self.func = func
        self.bridge = bridge
    
    def __call__(self, *args):
        return self.bridge.call_python_function(self.func, args)

class PythonObjectWrapper:
    """Python对象包装器"""
    
    def __init__(self, obj, bridge: PythonBridge):
        self.obj = obj
        self.bridge = bridge
    
    def get_attribute(self, name):
        """获取属性"""
        if hasattr(self.obj, name):
            attr = getattr(self.obj, name)
            return self.bridge.python_to_aqua(attr)
        else:
            raise AttributeError(f"Object has no attribute '{name}'")
    
    def set_attribute(self, name, value):
        """设置属性"""
        python_value = self.bridge.aqua_to_python(value)
        setattr(self.obj, name, python_value)

class EnhancedAquaVM(AquaVM):
    """增强版AquaScript虚拟机"""
    
    def __init__(self):
        super().__init__()
        self.python_bridge = PythonBridge()
        self.type_system = TypeSystem()
        
        # 扩展内置函数
        self.builtins.update({
            'type': self._builtin_type,
            'isinstance': self._builtin_isinstance,
            'hasattr': self._builtin_hasattr,
            'getattr': self._builtin_getattr,
            'setattr': self._builtin_setattr,
        })
        
        # 添加常用Python模块的快捷访问
        self._setup_common_modules()
    
    def _setup_common_modules(self):
        """设置常用Python模块"""
        common_modules = {
            'math': ['sin', 'cos', 'tan', 'sqrt', 'pi', 'e'],
            'random': ['random', 'randint', 'choice', 'shuffle'],
            'datetime': ['datetime', 'date', 'time'],
            'json': ['loads', 'dumps'],
            'os': ['path', 'listdir', 'getcwd'],
            'sys': ['argv', 'exit', 'version'],
        }
        
        for module_name, items in common_modules.items():
            try:
                imported = self.python_bridge.import_module(module_name, items)
                for item_name, item_value in imported.items():
                    self.builtins[f"{module_name}_{item_name}"] = item_value
            except ImportError:
                # 模块不可用，跳过
                pass
    
    def execute_import(self, module_name: str, items: Optional[List[str]] = None):
        """执行import语句"""
        try:
            imported = self.python_bridge.import_module(module_name, items)
            
            if items is None:
                # import module
                if self.call_stack:
                    # 在函数中
                    frame = self.call_stack[-1]
                    if module_name in frame.function.local_vars:
                        var_index = frame.function.local_vars[module_name]
                        frame.locals[var_index] = imported
                else:
                    # 在全局作用域
                    if module_name in self.global_vars:
                        var_index = self.global_vars[module_name]
                        self.globals[var_index] = imported
            else:
                # from module import items
                for item_name, item_value in imported.items():
                    if self.call_stack:
                        frame = self.call_stack[-1]
                        if item_name in frame.function.local_vars:
                            var_index = frame.function.local_vars[item_name]
                            frame.locals[var_index] = item_value
                    else:
                        if item_name in self.global_vars:
                            var_index = self.global_vars[item_name]
                            self.globals[var_index] = item_value
        
        except Exception as e:
            raise RuntimeError(f"Import error: {e}")
    
    def execute_var_declaration(self, name: str, value: Any, type_hint: Optional[str] = None):
        """执行变量声明"""
        # 类型检查
        if type_hint:
            if not self.type_system.check_type(value, type_hint):
                raise TypeError(f"Value {value} is not of type {type_hint}")
        
        # 存储变量
        if self.call_stack:
            frame = self.call_stack[-1]
            if name in frame.function.local_vars:
                var_index = frame.function.local_vars[name]
                frame.locals[var_index] = value
        else:
            if name in self.global_vars:
                var_index = self.global_vars[name]
                self.globals[var_index] = value
    
    def _builtin_type(self, obj):
        """获取对象类型"""
        return type(obj).__name__
    
    def _builtin_isinstance(self, obj, type_name):
        """检查对象类型"""
        return self.type_system.check_type(obj, type_name)
    
    def _builtin_hasattr(self, obj, name):
        """检查对象是否有属性"""
        if isinstance(obj, PythonObjectWrapper):
            return hasattr(obj.obj, name)
        return hasattr(obj, name)
    
    def _builtin_getattr(self, obj, name):
        """获取对象属性"""
        if isinstance(obj, PythonObjectWrapper):
            return obj.get_attribute(name)
        return getattr(obj, name)
    
    def _builtin_setattr(self, obj, name, value):
        """设置对象属性"""
        if isinstance(obj, PythonObjectWrapper):
            obj.set_attribute(name, value)
        else:
            setattr(obj, name, value)

class TypeSystem:
    """类型系统"""
    
    def __init__(self):
        self.type_map = {
            'int': int,
            'float': float,
            'str': str,
            'bool': bool,
            'list': list,
            'dict': dict,
        }
    
    def check_type(self, value, type_name: str) -> bool:
        """检查值是否符合指定类型"""
        if type_name in self.type_map:
            expected_type = self.type_map[type_name]
            return isinstance(value, expected_type)
        return False
    
    def convert_type(self, value, type_name: str):
        """类型转换"""
        if type_name in self.type_map:
            target_type = self.type_map[type_name]
            try:
                return target_type(value)
            except (ValueError, TypeError) as e:
                raise TypeError(f"Cannot convert {value} to {type_name}: {e}")
        raise TypeError(f"Unknown type: {type_name}")

def main():
    """测试增强版虚拟机"""
    vm = EnhancedAquaVM()
    
    # 测试Python模块导入
    try:
        math_module = vm.python_bridge.import_module('math', ['sin', 'pi'])
        print("Math module imported:", math_module)
        
        # 测试函数调用
        sin_func = math_module['sin']
        result = vm.python_bridge.call_python_function(sin_func, [3.14159/2])
        print("sin(π/2) =", result)
        
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()