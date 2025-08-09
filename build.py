"""
AquaScript构建脚本
用于编译示例程序和运行测试
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def compile_examples():
    """编译示例程序"""
    print("Compiling example programs...")
    
    examples_dir = Path("examples")
    compiler_path = Path("compiler/aquac.py")
    
    if not compiler_path.exists():
        print("Error: Compiler not found")
        return False
    
    success = True
    for aqua_file in examples_dir.glob("*.aqua"):
        print(f"  Compiling {aqua_file.name}...")
        
        cmd = f"python {compiler_path} {aqua_file}"
        ok, stdout, stderr = run_command(cmd)
        
        if ok:
            print(f"    ✓ {aqua_file.name} compiled successfully")
        else:
            print(f"    ✗ Failed to compile {aqua_file.name}")
            print(f"    Error: {stderr}")
            success = False
    
    return success

def run_tests():
    """运行测试"""
    print("Running tests...")
    
    tests_dir = Path("tests")
    success = True
    
    for test_file in tests_dir.glob("test_*.py"):
        print(f"  Running {test_file.name}...")
        
        cmd = f"python {test_file}"
        ok, stdout, stderr = run_command(cmd)
        
        if ok:
            print(f"    ✓ {test_file.name} passed")
        else:
            print(f"    ✗ {test_file.name} failed")
            print(f"    Output: {stdout}")
            print(f"    Error: {stderr}")
            success = False
    
    return success

def create_packages():
    """创建示例程序包"""
    print("Creating packages...")
    
    examples_dir = Path("examples")
    packer_path = Path("tools/apack.py")
    
    if not packer_path.exists():
        print("Error: Packer not found")
        return False
    
    success = True
    for acode_file in examples_dir.glob("*.acode"):
        package_name = acode_file.stem + ".apack"
        print(f"  Creating {package_name}...")
        
        cmd = f"python {packer_path} pack {acode_file} -o examples/{package_name}"
        ok, stdout, stderr = run_command(cmd)
        
        if ok:
            print(f"    ✓ {package_name} created successfully")
        else:
            print(f"    ✗ Failed to create {package_name}")
            print(f"    Error: {stderr}")
            success = False
    
    return success

def run_examples():
    """运行示例程序"""
    print("Running example programs...")
    
    examples_dir = Path("examples")
    vm_path = Path("vm/aquavm.py")
    
    if not vm_path.exists():
        print("Error: Virtual machine not found")
        return False
    
    success = True
    for acode_file in examples_dir.glob("*.acode"):
        print(f"  Running {acode_file.name}...")
        print("  " + "=" * 40)
        
        cmd = f"python {vm_path} {acode_file}"
        ok, stdout, stderr = run_command(cmd)
        
        if ok:
            print(stdout)
            print("  " + "=" * 40)
            print(f"    ✓ {acode_file.name} executed successfully")
        else:
            print(f"    ✗ Failed to run {acode_file.name}")
            print(f"    Error: {stderr}")
            success = False
        
        print()
    
    return success

def clean():
    """清理生成的文件"""
    print("Cleaning generated files...")
    
    # 删除.acode文件
    for acode_file in Path("examples").glob("*.acode"):
        acode_file.unlink()
        print(f"  Removed {acode_file}")
    
    # 删除.apack文件
    for apack_file in Path("examples").glob("*.apack"):
        apack_file.unlink()
        print(f"  Removed {apack_file}")
    
    print("Clean completed")

def main():
    if len(sys.argv) < 2:
        print("AquaScript Build Tool")
        print("Usage: python build.py <command>")
        print("Commands:")
        print("  test      - Run tests")
        print("  compile   - Compile examples")
        print("  package   - Create packages")
        print("  run       - Run examples")
        print("  all       - Do everything")
        print("  clean     - Clean generated files")
        return
    
    command = sys.argv[1]
    
    if command == "test":
        success = run_tests()
    elif command == "compile":
        success = compile_examples()
    elif command == "package":
        success = create_packages()
    elif command == "run":
        success = run_examples()
    elif command == "all":
        success = (run_tests() and 
                  compile_examples() and 
                  create_packages() and 
                  run_examples())
    elif command == "clean":
        clean()
        success = True
    else:
        print(f"Unknown command: {command}")
        success = False
    
    if not success:
        print("Build failed!")
        sys.exit(1)
    else:
        print("Build completed successfully!")

if __name__ == "__main__":
    main()