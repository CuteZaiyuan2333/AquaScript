#!/usr/bin/env python3
"""
批量测试所有示例文件的编译和运行状态
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
    print(f"\n{'='*60}")
    print(f"测试文件: {file_path}")
    print(f"{'='*60}")
    
    # 编译
    compile_cmd = f"python compiler/aquac.py {file_path}"
    success, stdout, stderr = run_command(compile_cmd, base_dir)
    
    if not success:
        print(f"❌ 编译失败:")
        print(f"错误: {stderr}")
        return False, "compile_failed"
    
    print(f"✅ 编译成功")
    
    # 获取输出文件路径
    acode_path = file_path.replace('.aqua', '.acode')
    
    # 运行
    run_cmd = f"python vm/optimized_aquavm.py {acode_path}"
    success, stdout, stderr = run_command(run_cmd, base_dir)
    
    if not success:
        print(f"❌ 运行失败:")
        print(f"错误: {stderr}")
        return True, "run_failed"
    
    print(f"✅ 运行成功")
    print(f"输出:")
    print(stdout[:500] + "..." if len(stdout) > 500 else stdout)
    
    return True, "success"

def main():
    base_dir = Path(__file__).parent
    
    # 测试文件列表
    test_files = [
        # examples目录
        "examples/hello.aqua",
        "examples/fibonacci.aqua",
        
        # test_files目录
        "test_files/basic_test.aqua",
        
        # feature_tests目录
        "test_files/feature_tests/test_basic_functions.aqua",
        "test_files/feature_tests/test_dict.aqua",
        "test_files/feature_tests/test_list.aqua",
        "test_files/feature_tests/test_math.aqua",
        "test_files/feature_tests/test_string.aqua",
        "test_files/feature_tests/test_tuple.aqua",
        "test_files/feature_tests/test_boolean.aqua",
        "test_files/feature_tests/test_in_operator_comprehensive.aqua",
        
        # basic_tests目录
        "test_files/basic_tests/simple_test.aqua",
        "test_files/basic_tests/test_boolean.aqua",
        "test_files/basic_tests/test_simple.aqua",
        "test_files/basic_tests/test_simple_condition.aqua",
        "test_files/basic_tests/test_simple_list.aqua",
    ]
    
    results = {
        "success": [],
        "compile_failed": [],
        "run_failed": []
    }
    
    print("AquaScript 示例文件批量测试")
    print("="*60)
    
    for file_path in test_files:
        full_path = base_dir / file_path
        if not full_path.exists():
            print(f"⚠️  文件不存在: {file_path}")
            continue
            
        compiled, status = test_file(file_path, base_dir)
        results[status].append(file_path)
    
    # 输出总结
    print(f"\n{'='*60}")
    print("测试总结")
    print(f"{'='*60}")
    
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

if __name__ == "__main__":
    main()