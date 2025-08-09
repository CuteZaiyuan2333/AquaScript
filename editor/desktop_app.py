#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AquaScript Editor Desktop Application
基于 tkinter 和 webview 的桌面版编辑器
"""

import tkinter as tk
from tkinter import messagebox
import threading
import time
import subprocess
import sys
import os
import webbrowser
from pathlib import Path

try:
    import webview
    WEBVIEW_AVAILABLE = True
except ImportError:
    WEBVIEW_AVAILABLE = False

class AquaScriptDesktopApp:
    def __init__(self):
        self.flask_process = None
        self.server_running = False
        self.app_dir = Path(__file__).parent
        
    def check_flask_server(self):
        """检查 Flask 服务器是否运行"""
        try:
            import requests
            response = requests.get('http://localhost:5000', timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def start_flask_server(self):
        """启动 Flask 服务器"""
        try:
            # 启动 Flask 应用
            self.flask_process = subprocess.Popen(
                [sys.executable, 'app.py'],
                cwd=self.app_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # 等待服务器启动
            for _ in range(30):  # 最多等待30秒
                if self.check_flask_server():
                    self.server_running = True
                    return True
                time.sleep(1)
            
            return False
        except Exception as e:
            print(f"启动 Flask 服务器失败: {e}")
            return False
    
    def stop_flask_server(self):
        """停止 Flask 服务器"""
        if self.flask_process:
            self.flask_process.terminate()
            self.flask_process = None
            self.server_running = False
    
    def create_webview_window(self):
        """使用 webview 创建桌面窗口"""
        if not WEBVIEW_AVAILABLE:
            messagebox.showerror("错误", "webview 库未安装。请运行: pip install pywebview")
            return False
        
        # 启动 Flask 服务器
        if not self.start_flask_server():
            messagebox.showerror("错误", "无法启动 AquaScript 编辑器服务")
            return False
        
        try:
            # 创建 webview 窗口
            webview.create_window(
                'AquaScript Editor',
                'http://localhost:5000',
                width=1400,
                height=900,
                min_size=(1000, 600),
                resizable=True,
                fullscreen=False,
                minimized=False,
                on_top=False,
                shadow=True,
                focus=True
            )
            
            # 启动 webview
            webview.start(debug=False)
            
        except Exception as e:
            messagebox.showerror("错误", f"启动编辑器窗口失败: {e}")
        finally:
            self.stop_flask_server()
        
        return True
    
    def create_tkinter_launcher(self):
        """创建 tkinter 启动器窗口"""
        root = tk.Tk()
        root.title("AquaScript Editor Launcher")
        root.geometry("500x400")
        root.resizable(False, False)
        
        # 设置窗口居中
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (500 // 2)
        y = (root.winfo_screenheight() // 2) - (400 // 2)
        root.geometry(f"500x400+{x}+{y}")
        
        # 创建主框架
        main_frame = tk.Frame(root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = tk.Label(
            main_frame, 
            text="🌊 AquaScript Editor", 
            font=("Arial", 24, "bold"),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        title_label.pack(pady=(0, 10))
        
        # 副标题
        subtitle_label = tk.Label(
            main_frame,
            text="现代化的 AquaScript 集成开发环境",
            font=("Arial", 12),
            bg='#f0f0f0',
            fg='#7f8c8d'
        )
        subtitle_label.pack(pady=(0, 30))
        
        # 状态标签
        self.status_label = tk.Label(
            main_frame,
            text="准备启动...",
            font=("Arial", 10),
            bg='#f0f0f0',
            fg='#27ae60'
        )
        self.status_label.pack(pady=(0, 20))
        
        # 按钮框架
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        # 启动按钮
        if WEBVIEW_AVAILABLE:
            start_btn = tk.Button(
                button_frame,
                text="启动编辑器 (独立窗口)",
                font=("Arial", 12, "bold"),
                bg='#3498db',
                fg='white',
                padx=20,
                pady=10,
                command=self.launch_webview_threaded,
                cursor='hand2'
            )
            start_btn.pack(pady=5)
        
        # 浏览器启动按钮
        browser_btn = tk.Button(
            button_frame,
            text="在浏览器中打开",
            font=("Arial", 12),
            bg='#2ecc71',
            fg='white',
            padx=20,
            pady=10,
            command=self.launch_browser_threaded,
            cursor='hand2'
        )
        browser_btn.pack(pady=5)
        
        # 退出按钮
        exit_btn = tk.Button(
            button_frame,
            text="退出",
            font=("Arial", 12),
            bg='#e74c3c',
            fg='white',
            padx=20,
            pady=10,
            command=self.quit_app,
            cursor='hand2'
        )
        exit_btn.pack(pady=5)
        
        # 功能特性
        features_frame = tk.Frame(main_frame, bg='#f0f0f0')
        features_frame.pack(pady=(30, 0))
        
        features_label = tk.Label(
            features_frame,
            text="功能特性:",
            font=("Arial", 11, "bold"),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        features_label.pack()
        
        features_text = """
• 智能语法高亮和代码补全
• 一键编译和运行 AquaScript 代码
• 集成文件管理器和项目浏览器
• 实时错误提示和调试支持
• 现代化的用户界面
• 支持主题切换
        """
        
        features_content = tk.Label(
            features_frame,
            text=features_text.strip(),
            font=("Arial", 9),
            bg='#f0f0f0',
            fg='#7f8c8d',
            justify=tk.LEFT
        )
        features_content.pack()
        
        # 设置关闭事件
        root.protocol("WM_DELETE_WINDOW", self.quit_app)
        
        self.root = root
        return root
    
    def launch_webview_threaded(self):
        """在线程中启动 webview"""
        self.status_label.config(text="正在启动编辑器...", fg='#f39c12')
        self.root.update()
        
        def launch():
            success = self.create_webview_window()
            if success:
                self.root.quit()
        
        thread = threading.Thread(target=launch, daemon=True)
        thread.start()
    
    def launch_browser_threaded(self):
        """在线程中启动浏览器版本"""
        self.status_label.config(text="正在启动服务器...", fg='#f39c12')
        self.root.update()
        
        def launch():
            if self.start_flask_server():
                self.status_label.config(text="服务器已启动，正在打开浏览器...", fg='#27ae60')
                self.root.update()
                webbrowser.open('http://localhost:5000')
                self.status_label.config(text="编辑器已在浏览器中打开", fg='#27ae60')
            else:
                self.status_label.config(text="启动失败", fg='#e74c3c')
                messagebox.showerror("错误", "无法启动 AquaScript 编辑器服务")
        
        thread = threading.Thread(target=launch, daemon=True)
        thread.start()
    
    def quit_app(self):
        """退出应用"""
        self.stop_flask_server()
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """运行应用"""
        root = self.create_tkinter_launcher()
        root.mainloop()

def main():
    """主函数"""
    print("启动 AquaScript Editor Desktop Application...")
    
    # 检查依赖
    missing_deps = []
    
    try:
        import flask
    except ImportError:
        missing_deps.append("flask")
    
    try:
        import requests
    except ImportError:
        missing_deps.append("requests")
    
    if missing_deps:
        print(f"缺少依赖: {', '.join(missing_deps)}")
        print(f"请运行: pip install {' '.join(missing_deps)}")
        input("按回车键退出...")
        return
    
    if not WEBVIEW_AVAILABLE:
        print("注意: webview 库未安装，将只能在浏览器中打开编辑器")
        print("要启用独立窗口模式，请运行: pip install pywebview")
    
    # 启动应用
    app = AquaScriptDesktopApp()
    app.run()

if __name__ == "__main__":
    main()