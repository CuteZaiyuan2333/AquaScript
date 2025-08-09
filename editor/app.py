#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AquaScript Web 编辑器后端服务
基于 Flask 和 WebSocket 的轻量级编辑器服务器
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
import threading
import time

# 添加 AquaScript 编译器路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aquascript-editor-secret'

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
AQUASCRIPT_ROOT = os.path.dirname(PROJECT_ROOT)
WORKSPACE_DIR = os.path.join(PROJECT_ROOT, 'workspace')

# 确保工作目录存在
os.makedirs(WORKSPACE_DIR, exist_ok=True)

class FileManager:
    """文件管理器"""
    
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(exist_ok=True)
    
    def get_file_tree(self):
        """获取文件树结构"""
        def build_tree(path):
            items = []
            try:
                for item in sorted(path.iterdir()):
                    if item.name.startswith('.'):
                        continue
                    
                    item_data = {
                        'name': item.name,
                        'path': str(item.relative_to(self.root_dir)),
                        'type': 'directory' if item.is_dir() else 'file'
                    }
                    
                    if item.is_dir():
                        item_data['children'] = build_tree(item)
                    else:
                        item_data['size'] = item.stat().st_size
                        item_data['extension'] = item.suffix
                    
                    items.append(item_data)
            except PermissionError:
                pass
            
            return items
        
        return build_tree(self.root_dir)
    
    def read_file(self, file_path):
        """读取文件内容"""
        try:
            full_path = self.root_dir / file_path
            if not full_path.exists():
                return None
            
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return None
    
    def write_file(self, file_path, content):
        """写入文件内容"""
        try:
            full_path = self.root_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            return False
    
    def create_file(self, file_path):
        """创建新文件"""
        try:
            full_path = self.root_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.touch()
            return True
        except Exception as e:
            return False
    
    def delete_file(self, file_path):
        """删除文件"""
        try:
            full_path = self.root_dir / file_path
            if full_path.exists():
                if full_path.is_file():
                    full_path.unlink()
                else:
                    import shutil
                    shutil.rmtree(full_path)
            return True
        except Exception as e:
            return False

class AquaScriptCompiler:
    """AquaScript 编译器接口"""
    
    def __init__(self):
        self.compiler_path = os.path.join(AQUASCRIPT_ROOT, 'compiler', 'aquac.py')
        self.vm_path = os.path.join(AQUASCRIPT_ROOT, 'vm', 'optimized_aquavm.py')
    
    def compile_file(self, source_file):
        """编译 AquaScript 文件"""
        try:
            # 切换到 AquaScript 根目录
            original_cwd = os.getcwd()
            os.chdir(AQUASCRIPT_ROOT)
            
            # 执行编译
            result = subprocess.run([
                sys.executable, self.compiler_path, source_file
            ], capture_output=True, text=True, timeout=30)
            
            os.chdir(original_cwd)
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'bytecode_file': source_file.replace('.aqua', '.acode') if result.returncode == 0 else None
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'stdout': '',
                'stderr': '编译超时'
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': f'编译错误: {str(e)}'
            }
    
    def run_bytecode(self, bytecode_file):
        """运行字节码文件"""
        try:
            original_cwd = os.getcwd()
            os.chdir(AQUASCRIPT_ROOT)
            
            result = subprocess.run([
                sys.executable, self.vm_path, bytecode_file
            ], capture_output=True, text=True, timeout=30)
            
            os.chdir(original_cwd)
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'stdout': '',
                'stderr': '运行超时'
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': f'运行错误: {str(e)}'
            }

# 全局实例
file_manager = FileManager(WORKSPACE_DIR)
compiler = AquaScriptCompiler()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/files')
def get_files():
    """获取文件树"""
    return jsonify(file_manager.get_file_tree())

@app.route('/api/file/<path:file_path>')
def get_file(file_path):
    """获取文件内容"""
    content = file_manager.read_file(file_path)
    if content is not None:
        return jsonify({'content': content})
    else:
        return jsonify({'error': '文件不存在或无法读取'}), 404

@app.route('/api/file/<path:file_path>', methods=['POST'])
def save_file(file_path):
    """保存文件内容"""
    data = request.get_json()
    content = data.get('content', '')
    
    if file_manager.write_file(file_path, content):
        return jsonify({'success': True})
    else:
        return jsonify({'error': '保存失败'}), 500

@app.route('/api/file/<path:file_path>', methods=['PUT'])
def create_file(file_path):
    """创建新文件"""
    if file_manager.create_file(file_path):
        return jsonify({'success': True})
    else:
        return jsonify({'error': '创建失败'}), 500

@app.route('/api/file/<path:file_path>', methods=['DELETE'])
def delete_file(file_path):
    """删除文件"""
    if file_manager.delete_file(file_path):
        return jsonify({'success': True})
    else:
        return jsonify({'error': '删除失败'}), 500

@app.route('/api/compile', methods=['POST'])
def compile_code():
    """编译代码"""
    data = request.get_json()
    file_path = data.get('file_path')
    
    if not file_path:
        return jsonify({'error': '未指定文件路径'}), 400
    
    # 确保文件存在于工作目录中
    full_path = os.path.join(WORKSPACE_DIR, file_path)
    if not os.path.exists(full_path):
        return jsonify({'error': '文件不存在'}), 404
    
    result = compiler.compile_file(full_path)
    return jsonify(result)

@app.route('/api/run', methods=['POST'])
def run_code():
    """运行代码"""
    data = request.get_json()
    file_path = data.get('file_path')
    
    if not file_path:
        return jsonify({'error': '未指定文件路径'}), 400
    
    # 先编译
    full_path = os.path.join(WORKSPACE_DIR, file_path)
    compile_result = compiler.compile_file(full_path)
    
    if not compile_result['success']:
        return jsonify({
            'compile_success': False,
            'compile_output': compile_result['stderr'],
            'run_success': False,
            'run_output': ''
        })
    
    # 再运行
    bytecode_file = full_path.replace('.aqua', '.acode')
    run_result = compiler.run_bytecode(bytecode_file)
    
    return jsonify({
        'compile_success': True,
        'compile_output': compile_result['stdout'],
        'run_success': run_result['success'],
        'run_output': run_result['stdout'] if run_result['success'] else run_result['stderr']
    })

if __name__ == '__main__':
    # 创建示例文件
    if not os.path.exists(os.path.join(WORKSPACE_DIR, 'hello.aqua')):
        sample_code = '''# AquaScript 示例程序
func greet(name):
    return f"Hello, {name}!"

func main():
    print("=== AquaScript 编辑器演示 ===")
    message = greet("World")
    print(message)
    
    # 简单计算
    a = 10
    b = 20
    result = a + b
    print(f"计算结果: {a} + {b} = {result}")

main()
'''
        file_manager.write_file('hello.aqua', sample_code)
    
    print("🚀 AquaScript 编辑器启动中...")
    print("📝 访问地址: http://localhost:5000")
    print("📁 工作目录:", WORKSPACE_DIR)
    
    app.run(host='0.0.0.0', port=5000, debug=True)