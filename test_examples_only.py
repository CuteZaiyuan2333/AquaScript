#!/usr/bin/env python3
"""
专门测试examples目录中所有脚本文件的编译和运行状态
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=cwd,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)

def test_file(file_path, base_dir):
    """测试单个文件的编译和运行"""
    print(f"\n{'='*80}")
    print(f"测试文件: {file_path}")
    print(f"{'='*80}")
    
    # 编译
    compile_cmd = f"python compiler/aquac.py {file_path}"
    success, stdout, stderr = run_command(compile_cmd, base_dir)
    
    if not success:
        print(f"❌ 编译失败:")
        print(f"错误信息: {stderr}")
        if stdout:
            print(f"输出信息: {stdout}")
        return False, "compile_failed"
    
    print(f"✅ 编译成功")
    print(f"编译信息: {stdout}")
    
    # 获取输出文件路径
    acode_path = file_path.replace('.aqua', '.acode')
    
    # 运行
    run_cmd = f"python vm/optimized_aquavm.py {acode_path}"
    success, stdout, stderr = run_command(run_cmd, base_dir)
    
    if not success:
        print(f"❌ 运行失败:")
        print(f"错误信息: {stderr}")
        if stdout:
            print(f"输出信息: {stdout}")
        return True, "run_failed"
    
    print(f"✅ 运行成功")
    print(f"运行输出:")
    print("-" * 40)
    print(stdout)
    print("-" * 40)
    
    return True, "success"

def main():
    base_dir = Path(__file__).parent
    
    # examples目录中的所有文件
    examples_dir = base_dir / "examples"
    example_files = []
    
    if examples_dir.exists():
        for file in examples_dir.glob("*.aqua"):
            example_files.append(f"examples/{file.name}")
    
    example_files.sort()  # 按字母顺序排序
    
    results = {
        "success": [],
        "compile_failed": [],
        "run_failed": []
    }
    
    print("AquaScript Examples 目录脚本测试")
    print("="*80)
    print(f"找到 {len(example_files)} 个示例文件")
    
    for file_path in example_files:
        full_path = base_dir / file_path
        if not full_path.exists():
            print(f"⚠️  文件不存在: {file_path}")
            continue
            
        compiled, status = test_file(file_path, base_dir)
        results[status].append(file_path)
    
    # 输出总结
    print(f"\n{'='*80}")
    print("Examples 目录测试总结")
    print(f"{'='*80}")
    
    print(f"✅ 成功运行: {len(results['success'])} 个文件")
    for file in results['success']:
        print(f"   - {file}")
    
    print(f"\n❌ 编译失败: {len(results['compile_failed'])} 个文件")
    for file in results['compile_failed']:
        print(f"   - {file}")
    
    print(f"\n⚠️  运行失败: {len(results['run_failed'])} 个文件")
    for file in results['run_failed']:
        print(f"   - {file}")
    
    total_tested = len(results['success']) + len(results['compile_failed']) + len(results['run_failed'])
    success_rate = len(results['success']) / total_tested * 100 if total_tested > 0 else 0
    
    print(f"\n总计测试: {total_tested} 个文件")
    print(f"成功率: {success_rate:.1f}%")
    
    # 详细分析编译失败的原因
    if results['compile_failed']:
        print(f"\n{'='*80}")
        print("编译失败原因分析")
        print(f"{'='*80}")
        print("这些文件可能使用了尚未实现的高级语法特性，如：")
        print("- 装饰器 (@decorator)")
        print("- 异步编程 (async/await)")
        print("- 模式匹配 (match/case)")
        print("- 泛型类型系统")
        print("- 高级字符串操作")
        print("- 复杂的面向对象特性")

if __name__ == "__main__":
    main()