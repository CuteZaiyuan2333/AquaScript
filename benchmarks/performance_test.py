#!/usr/bin/env python3
"""
AquaVM 性能基准测试

比较不同版本虚拟机的性能：
1. 原始Python版本
2. 优化Python版本
3. Cython版本
4. Rust版本（通过Python绑定）
"""

import time
import sys
import os
import subprocess
import statistics
from typing import List, Dict, Any

# 添加VM路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'vm'))

class BenchmarkSuite:
    """性能测试套件"""
    
    def __init__(self):
        self.results = {}
        self.test_files = [
            'test_simple_vm.acode',
            'test_string.acode',
            'test_global.acode',
        ]
    
    def run_benchmark(self, vm_name: str, vm_runner: callable, iterations: int = 10) -> Dict[str, Any]:
        """运行基准测试"""
        print(f"\n=== 测试 {vm_name} ===")
        
        results = {
            'vm_name': vm_name,
            'iterations': iterations,
            'tests': {}
        }
        
        for test_file in self.test_files:
            if not os.path.exists(test_file):
                print(f"跳过 {test_file} (文件不存在)")
                continue
            
            print(f"测试 {test_file}...")
            times = []
            
            for i in range(iterations):
                try:
                    start_time = time.perf_counter()
                    vm_runner(test_file)
                    end_time = time.perf_counter()
                    
                    execution_time = (end_time - start_time) * 1000  # 转换为毫秒
                    times.append(execution_time)
                    
                except Exception as e:
                    print(f"  错误 (第{i+1}次): {e}")
                    continue
            
            if times:
                results['tests'][test_file] = {
                    'times': times,
                    'avg': statistics.mean(times),
                    'min': min(times),
                    'max': max(times),
                    'std': statistics.stdev(times) if len(times) > 1 else 0,
                }
                
                print(f"  平均: {results['tests'][test_file]['avg']:.2f}ms")
                print(f"  最小: {results['tests'][test_file]['min']:.2f}ms")
                print(f"  最大: {results['tests'][test_file]['max']:.2f}ms")
                print(f"  标准差: {results['tests'][test_file]['std']:.2f}ms")
        
        return results
    
    def run_original_vm(self, test_file: str):
        """运行原始Python虚拟机"""
        try:
            from aquavm import AquaVM
            
            vm = AquaVM()
            with open(test_file, 'rb') as f:
                bytecode = f.read()
            vm.load_bytecode(bytecode)
            
            # 重定向输出避免影响性能测试
            import io
            import contextlib
            
            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                vm.run()
            
        except ImportError:
            raise Exception("原始AquaVM不可用")
    
    def run_optimized_vm(self, test_file: str):
        """运行优化Python虚拟机"""
        try:
            from optimized_aquavm import OptimizedAquaVM
            
            vm = OptimizedAquaVM()
            with open(test_file, 'rb') as f:
                bytecode = f.read()
            vm.load_bytecode(bytecode)
            
            import io
            import contextlib
            
            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                vm.run()
            
        except ImportError:
            raise Exception("优化AquaVM不可用")
    
    def run_cython_vm(self, test_file: str):
        """运行Cython虚拟机"""
        try:
            from cython_aquavm import CythonAquaVM
            
            vm = CythonAquaVM()
            with open(test_file, 'rb') as f:
                bytecode = f.read()
            vm.load_bytecode(bytecode)
            
            import io
            import contextlib
            
            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                vm.run()
            
        except ImportError:
            raise Exception("Cython AquaVM不可用 (需要编译)")
    
    def run_rust_vm(self, test_file: str):
        """运行Rust虚拟机"""
        try:
            # 通过命令行调用Rust虚拟机
            result = subprocess.run(
                ['cargo', 'run', '--release', '--', test_file],
                cwd='rust_vm',
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                raise Exception(f"Rust VM错误: {result.stderr}")
            
        except FileNotFoundError:
            raise Exception("Rust VM不可用 (需要安装Cargo)")
        except subprocess.TimeoutExpired:
            raise Exception("Rust VM超时")
    
    def run_all_benchmarks(self):
        """运行所有基准测试"""
        print("AquaVM 性能基准测试")
        print("=" * 50)
        
        # 测试原始VM
        try:
            results = self.run_benchmark("原始Python VM", self.run_original_vm)
            self.results['original'] = results
        except Exception as e:
            print(f"原始VM测试失败: {e}")
        
        # 测试优化VM
        try:
            results = self.run_benchmark("优化Python VM", self.run_optimized_vm)
            self.results['optimized'] = results
        except Exception as e:
            print(f"优化VM测试失败: {e}")
        
        # 测试Cython VM
        try:
            results = self.run_benchmark("Cython VM", self.run_cython_vm)
            self.results['cython'] = results
        except Exception as e:
            print(f"Cython VM测试失败: {e}")
        
        # 测试Rust VM
        try:
            results = self.run_benchmark("Rust VM", self.run_rust_vm)
            self.results['rust'] = results
        except Exception as e:
            print(f"Rust VM测试失败: {e}")
        
        # 生成对比报告
        self.generate_comparison_report()
    
    def generate_comparison_report(self):
        """生成性能对比报告"""
        print("\n" + "=" * 60)
        print("性能对比报告")
        print("=" * 60)
        
        if not self.results:
            print("没有可用的测试结果")
            return
        
        # 获取所有测试文件
        all_tests = set()
        for result in self.results.values():
            all_tests.update(result.get('tests', {}).keys())
        
        for test_file in sorted(all_tests):
            print(f"\n📊 {test_file}")
            print("-" * 40)
            
            baseline_time = None
            vm_times = []
            
            for vm_name, result in self.results.items():
                if test_file in result.get('tests', {}):
                    avg_time = result['tests'][test_file]['avg']
                    vm_times.append((vm_name, avg_time))
                    
                    if vm_name == 'original':
                        baseline_time = avg_time
            
            # 按性能排序
            vm_times.sort(key=lambda x: x[1])
            
            for i, (vm_name, avg_time) in enumerate(vm_times):
                speedup = ""
                if baseline_time and baseline_time > 0:
                    ratio = baseline_time / avg_time
                    if ratio > 1:
                        speedup = f" (🚀 {ratio:.1f}x 更快)"
                    elif ratio < 1:
                        speedup = f" (🐌 {1/ratio:.1f}x 更慢)"
                
                rank_emoji = ["🥇", "🥈", "🥉"][i] if i < 3 else "📍"
                print(f"  {rank_emoji} {vm_name:15s}: {avg_time:8.2f}ms{speedup}")
        
        # 总体性能排名
        print(f"\n🏆 总体性能排名")
        print("-" * 40)
        
        vm_avg_times = {}
        for vm_name, result in self.results.items():
            times = []
            for test_data in result.get('tests', {}).values():
                times.append(test_data['avg'])
            
            if times:
                vm_avg_times[vm_name] = statistics.mean(times)
        
        sorted_vms = sorted(vm_avg_times.items(), key=lambda x: x[1])
        
        for i, (vm_name, avg_time) in enumerate(sorted_vms):
            rank_emoji = ["🥇", "🥈", "🥉"][i] if i < 3 else "📍"
            print(f"  {rank_emoji} {vm_name:15s}: {avg_time:8.2f}ms (平均)")

def main():
    """主函数"""
    # 切换到正确的目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    benchmark = BenchmarkSuite()
    benchmark.run_all_benchmarks()

if __name__ == "__main__":
    main()