"""
AquaScript打包工具
将.acode字节码文件打包为.apack应用程序包
"""

import sys
import os
import zipfile
import json
import argparse
from typing import List, Dict, Any

class AquaPacker:
    def __init__(self):
        self.manifest = {
            'name': '',
            'version': '1.0.0',
            'main': 'main.acode',
            'description': '',
            'author': '',
            'dependencies': [],
            'aqua_version': '1.0'
        }
    
    def create_package(self, main_file: str, output_file: str, manifest_data: Dict[str, Any] = None):
        """创建.apack包"""
        
        if not os.path.exists(main_file):
            print(f"Error: Main file '{main_file}' not found")
            return False
        
        # 更新manifest
        if manifest_data:
            self.manifest.update(manifest_data)
        
        # 如果没有指定名称，使用文件名
        if not self.manifest['name']:
            self.manifest['name'] = os.path.splitext(os.path.basename(main_file))[0]
        
        # 确定输出文件名
        if not output_file.endswith('.apack'):
            output_file += '.apack'
        
        try:
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
                # 添加manifest文件
                manifest_json = json.dumps(self.manifest, indent=2)
                zf.writestr('manifest.json', manifest_json)
                
                # 添加主程序文件
                zf.write(main_file, 'main.acode')
                
                # 添加其他依赖文件（如果有的话）
                main_dir = os.path.dirname(main_file)
                if main_dir:
                    for root, dirs, files in os.walk(main_dir):
                        for file in files:
                            if file.endswith('.acode') and file != os.path.basename(main_file):
                                file_path = os.path.join(root, file)
                                arc_path = os.path.relpath(file_path, main_dir)
                                zf.write(file_path, arc_path)
                
                print(f"Package created: {output_file}")
                print(f"Main file: {main_file}")
                print(f"Package name: {self.manifest['name']}")
                print(f"Version: {self.manifest['version']}")
                
            return True
            
        except Exception as e:
            print(f"Packaging Error: {e}")
            return False
    
    def extract_package(self, package_file: str, output_dir: str = None):
        """解压.apack包"""
        
        if not os.path.exists(package_file):
            print(f"Error: Package file '{package_file}' not found")
            return False
        
        if output_dir is None:
            output_dir = os.path.splitext(package_file)[0]
        
        try:
            with zipfile.ZipFile(package_file, 'r') as zf:
                # 读取manifest
                manifest_data = zf.read('manifest.json').decode('utf-8')
                manifest = json.loads(manifest_data)
                
                print(f"Extracting package: {manifest['name']} v{manifest['version']}")
                
                # 解压所有文件
                zf.extractall(output_dir)
                
                print(f"Extracted to: {output_dir}")
                
            return True
            
        except Exception as e:
            print(f"Extraction Error: {e}")
            return False
    
    def run_package(self, package_file: str):
        """运行.apack包"""
        
        if not os.path.exists(package_file):
            print(f"Error: Package file '{package_file}' not found")
            return False
        
        try:
            import tempfile
            import subprocess
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # 解压包到临时目录
                with zipfile.ZipFile(package_file, 'r') as zf:
                    zf.extractall(temp_dir)
                
                # 读取manifest
                manifest_path = os.path.join(temp_dir, 'manifest.json')
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                
                # 运行主程序
                main_file = os.path.join(temp_dir, manifest['main'])
                vm_path = os.path.join(os.path.dirname(__file__), '..', 'vm', 'aquavm.py')
                
                cmd = [sys.executable, vm_path, main_file]
                result = subprocess.run(cmd, capture_output=False)
                
                return result.returncode == 0
                
        except Exception as e:
            print(f"Runtime Error: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='AquaScript Package Manager')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # pack命令
    pack_parser = subparsers.add_parser('pack', help='Create a package')
    pack_parser.add_argument('main', help='Main .acode file')
    pack_parser.add_argument('-o', '--output', help='Output .apack file')
    pack_parser.add_argument('-n', '--name', help='Package name')
    pack_parser.add_argument('-v', '--version', help='Package version')
    pack_parser.add_argument('-d', '--description', help='Package description')
    pack_parser.add_argument('-a', '--author', help='Package author')
    
    # extract命令
    extract_parser = subparsers.add_parser('extract', help='Extract a package')
    extract_parser.add_argument('package', help='Package .apack file')
    extract_parser.add_argument('-o', '--output', help='Output directory')
    
    # run命令
    run_parser = subparsers.add_parser('run', help='Run a package')
    run_parser.add_argument('package', help='Package .apack file')
    
    # 如果没有参数，显示帮助
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    args = parser.parse_args()
    
    packer = AquaPacker()
    
    if args.command == 'pack':
        manifest_data = {}
        if args.name:
            manifest_data['name'] = args.name
        if args.version:
            manifest_data['version'] = args.version
        if args.description:
            manifest_data['description'] = args.description
        if args.author:
            manifest_data['author'] = args.author
        
        output_file = args.output or (os.path.splitext(args.main)[0] + '.apack')
        success = packer.create_package(args.main, output_file, manifest_data)
        
    elif args.command == 'extract':
        success = packer.extract_package(args.package, args.output)
        
    elif args.command == 'run':
        success = packer.run_package(args.package)
        
    else:
        parser.print_help()
        success = False
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()