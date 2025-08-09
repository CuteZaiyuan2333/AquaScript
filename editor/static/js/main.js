// AquaScript 编辑器主要 JavaScript 文件

class AquaScriptEditor {
    constructor() {
        this.editor = null;
        this.currentFile = null;
        this.openFiles = new Map();
        this.fileTree = null;
        this.socket = null;
        this.theme = localStorage.getItem('theme') || 'light';
        
        this.init();
    }

    async init() {
        this.setupTheme();
        this.setupEventListeners();
        this.setupWebSocket();
        await this.loadFileTree();
        this.setupMonacoEditor();
        this.showWelcomeScreen();
    }

    setupTheme() {
        document.documentElement.setAttribute('data-theme', this.theme);
        const themeBtn = document.getElementById('theme-toggle');
        if (themeBtn) {
            themeBtn.innerHTML = this.theme === 'dark' ? 
                '<i class="fas fa-sun"></i> 浅色' : 
                '<i class="fas fa-moon"></i> 深色';
        }
    }

    toggleTheme() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        localStorage.setItem('theme', this.theme);
        this.setupTheme();
        
        // 更新 Monaco 编辑器主题
        if (this.editor) {
            monaco.editor.setTheme(this.theme === 'dark' ? 'vs-dark' : 'vs');
        }
    }

    setupEventListeners() {
        // 菜单事件
        document.addEventListener('click', (e) => {
            // 关闭所有下拉菜单
            if (!e.target.closest('.menu-item')) {
                document.querySelectorAll('.dropdown-menu').forEach(menu => {
                    menu.classList.remove('show');
                });
            }
        });

        // 菜单项点击
        document.querySelectorAll('.menu-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                const dropdown = item.querySelector('.dropdown-menu');
                if (dropdown) {
                    // 关闭其他菜单
                    document.querySelectorAll('.dropdown-menu').forEach(menu => {
                        if (menu !== dropdown) menu.classList.remove('show');
                    });
                    dropdown.classList.toggle('show');
                }
            });
        });

        // 菜单选项点击
        document.addEventListener('click', (e) => {
            if (e.target.closest('.menu-option')) {
                const action = e.target.closest('.menu-option').dataset.action;
                this.handleMenuAction(action);
                // 关闭菜单
                document.querySelectorAll('.dropdown-menu').forEach(menu => {
                    menu.classList.remove('show');
                });
            }
        });

        // 工具栏按钮
        document.getElementById('compile-btn')?.addEventListener('click', () => this.compileFile());
        document.getElementById('run-btn')?.addEventListener('click', () => this.runFile());
        document.getElementById('theme-toggle')?.addEventListener('click', () => this.toggleTheme());

        // 控制台切换
        document.getElementById('console-toggle')?.addEventListener('click', () => this.toggleConsole());
        document.getElementById('console-clear')?.addEventListener('click', () => this.clearConsole());

        // 模态框关闭
        document.querySelectorAll('.modal-close, .modal-overlay').forEach(el => {
            el.addEventListener('click', (e) => {
                if (e.target === el) {
                    this.closeModal();
                }
            });
        });

        // 键盘快捷键
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 's':
                        e.preventDefault();
                        this.saveFile();
                        break;
                    case 'o':
                        e.preventDefault();
                        this.openFile();
                        break;
                    case 'n':
                        e.preventDefault();
                        this.newFile();
                        break;
                    case 'F5':
                        e.preventDefault();
                        this.runFile();
                        break;
                    case 'F9':
                        e.preventDefault();
                        this.compileFile();
                        break;
                }
            }
        });
    }

    setupWebSocket() {
        // 简化版本，不使用 WebSocket
        this.log('编辑器已就绪', 'success');
    }

    async setupMonacoEditor() {
        // 等待 Monaco Editor 加载
        if (typeof monaco === 'undefined') {
            await new Promise(resolve => {
                const script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs/loader.js';
                script.onload = () => {
                    require.config({ paths: { vs: 'https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs' } });
                    require(['vs/editor/editor.main'], resolve);
                };
                document.head.appendChild(script);
            });
        }

        // 注册 AquaScript 语言
        monaco.languages.register({ id: 'aquascript' });

        // 设置语法高亮
        monaco.languages.setMonarchTokensProvider('aquascript', {
            tokenizer: {
                root: [
                    [/\b(let|const|if|else|while|for|function|return|true|false|null)\b/, 'keyword'],
                    [/\b\d+(\.\d+)?\b/, 'number'],
                    [/"([^"\\]|\\.)*"/, 'string'],
                    [/'([^'\\]|\\.)*'/, 'string'],
                    [/\/\/.*$/, 'comment'],
                    [/\/\*[\s\S]*?\*\//, 'comment'],
                    [/[{}()\[\]]/, 'bracket'],
                    [/[;,.]/, 'delimiter'],
                    [/[+\-*/%=<>!&|]/, 'operator'],
                ]
            }
        });

        // 设置代码补全
        monaco.languages.registerCompletionItemProvider('aquascript', {
            provideCompletionItems: () => ({
                suggestions: [
                    {
                        label: 'function',
                        kind: monaco.languages.CompletionItemKind.Keyword,
                        insertText: 'function ${1:name}(${2:params}) {\n\t${3}\n}',
                        insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet
                    },
                    {
                        label: 'if',
                        kind: monaco.languages.CompletionItemKind.Keyword,
                        insertText: 'if (${1:condition}) {\n\t${2}\n}',
                        insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet
                    },
                    {
                        label: 'while',
                        kind: monaco.languages.CompletionItemKind.Keyword,
                        insertText: 'while (${1:condition}) {\n\t${2}\n}',
                        insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet
                    },
                    {
                        label: 'for',
                        kind: monaco.languages.CompletionItemKind.Keyword,
                        insertText: 'for (${1:init}; ${2:condition}; ${3:increment}) {\n\t${4}\n}',
                        insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet
                    }
                ]
            })
        });

        this.createEditor();
    }

    createEditor() {
        const container = document.getElementById('monaco-editor');
        if (!container) return;

        this.editor = monaco.editor.create(container, {
            value: '',
            language: 'aquascript',
            theme: this.theme === 'dark' ? 'vs-dark' : 'vs',
            automaticLayout: true,
            fontSize: 14,
            lineNumbers: 'on',
            roundedSelection: false,
            scrollBeyondLastLine: false,
            minimap: { enabled: true },
            folding: true,
            wordWrap: 'on',
            tabSize: 4,
            insertSpaces: true
        });

        // 监听内容变化
        this.editor.onDidChangeModelContent(() => {
            if (this.currentFile) {
                this.markFileAsModified(this.currentFile);
            }
        });
    }

    async loadFileTree() {
        try {
            const response = await fetch('/api/files');
            const data = await response.json();
            this.fileTree = data.files;
            this.renderFileTree();
        } catch (error) {
            console.error('加载文件树失败:', error);
            this.log('加载文件树失败', 'error');
        }
    }

    renderFileTree() {
        const container = document.getElementById('file-tree');
        if (!container) return;

        container.innerHTML = '';
        this.renderFileNode(this.fileTree, container);
    }

    renderFileNode(node, container, level = 0) {
        const item = document.createElement('div');
        item.className = 'file-item';
        item.style.paddingLeft = `${level * 16 + 8}px`;
        
        if (node.type === 'directory') {
            item.classList.add('directory');
            item.innerHTML = `
                <i class="fas fa-folder"></i>
                <span>${node.name}</span>
            `;
            
            item.addEventListener('click', () => {
                // 切换文件夹展开/折叠
                const children = item.nextElementSibling;
                if (children && children.classList.contains('file-children')) {
                    children.style.display = children.style.display === 'none' ? 'block' : 'none';
                    const icon = item.querySelector('i');
                    icon.className = children.style.display === 'none' ? 'fas fa-folder' : 'fas fa-folder-open';
                }
            });
        } else {
            const icon = this.getFileIcon(node.name);
            item.innerHTML = `
                <i class="${icon}"></i>
                <span>${node.name}</span>
            `;
            
            item.addEventListener('click', () => {
                this.openFileFromTree(node.path);
            });
        }

        container.appendChild(item);

        if (node.children && node.children.length > 0) {
            const childrenContainer = document.createElement('div');
            childrenContainer.className = 'file-children';
            container.appendChild(childrenContainer);

            node.children.forEach(child => {
                this.renderFileNode(child, childrenContainer, level + 1);
            });
        }
    }

    getFileIcon(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        switch (ext) {
            case 'aqua':
                return 'fas fa-code';
            case 'acode':
                return 'fas fa-file-code';
            case 'md':
                return 'fab fa-markdown';
            case 'txt':
                return 'fas fa-file-alt';
            case 'json':
                return 'fas fa-file-code';
            default:
                return 'fas fa-file';
        }
    }

    async openFileFromTree(filePath) {
        try {
            const response = await fetch(`/api/files/read?path=${encodeURIComponent(filePath)}`);
            const data = await response.json();
            
            if (data.success) {
                this.openFileInEditor(filePath, data.content);
            } else {
                this.log(`打开文件失败: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('读取文件失败:', error);
            this.log('读取文件失败', 'error');
        }
    }

    openFileInEditor(filePath, content) {
        // 隐藏欢迎屏幕
        this.hideWelcomeScreen();

        // 如果文件已经打开，切换到该标签
        if (this.openFiles.has(filePath)) {
            this.switchToFile(filePath);
            return;
        }

        // 添加到打开文件列表
        this.openFiles.set(filePath, {
            content: content,
            modified: false,
            originalContent: content
        });

        // 创建标签
        this.createTab(filePath);

        // 切换到新文件
        this.switchToFile(filePath);
    }

    createTab(filePath) {
        const tabBar = document.querySelector('.tab-bar');
        if (!tabBar) return;

        const fileName = filePath.split('/').pop();
        const tab = document.createElement('div');
        tab.className = 'tab';
        tab.dataset.file = filePath;
        
        tab.innerHTML = `
            <div class="tab-title">
                <i class="${this.getFileIcon(fileName)}"></i>
                <span>${fileName}</span>
            </div>
            <button class="tab-close" title="关闭">
                <i class="fas fa-times"></i>
            </button>
        `;

        // 标签点击事件
        tab.addEventListener('click', (e) => {
            if (!e.target.closest('.tab-close')) {
                this.switchToFile(filePath);
            }
        });

        // 关闭按钮事件
        tab.querySelector('.tab-close').addEventListener('click', (e) => {
            e.stopPropagation();
            this.closeFile(filePath);
        });

        tabBar.appendChild(tab);
    }

    switchToFile(filePath) {
        this.currentFile = filePath;
        const fileData = this.openFiles.get(filePath);
        
        if (this.editor && fileData) {
            this.editor.setValue(fileData.content);
            
            // 设置语言模式
            const ext = filePath.split('.').pop().toLowerCase();
            const language = ext === 'aqua' ? 'aquascript' : 'plaintext';
            monaco.editor.setModelLanguage(this.editor.getModel(), language);
        }

        // 更新标签状态
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.remove('active');
            if (tab.dataset.file === filePath) {
                tab.classList.add('active');
            }
        });

        // 更新文件树选中状态
        document.querySelectorAll('.file-item').forEach(item => {
            item.classList.remove('active');
        });
    }

    closeFile(filePath) {
        const fileData = this.openFiles.get(filePath);
        
        // 检查是否有未保存的更改
        if (fileData && fileData.modified) {
            if (!confirm('文件有未保存的更改，确定要关闭吗？')) {
                return;
            }
        }

        // 移除标签
        const tab = document.querySelector(`.tab[data-file="${filePath}"]`);
        if (tab) {
            tab.remove();
        }

        // 从打开文件列表中移除
        this.openFiles.delete(filePath);

        // 如果关闭的是当前文件，切换到其他文件或显示欢迎屏幕
        if (this.currentFile === filePath) {
            const remainingFiles = Array.from(this.openFiles.keys());
            if (remainingFiles.length > 0) {
                this.switchToFile(remainingFiles[0]);
            } else {
                this.currentFile = null;
                this.showWelcomeScreen();
            }
        }
    }

    markFileAsModified(filePath) {
        const fileData = this.openFiles.get(filePath);
        if (fileData && this.editor) {
            const currentContent = this.editor.getValue();
            fileData.content = currentContent;
            fileData.modified = currentContent !== fileData.originalContent;

            // 更新标签显示
            const tab = document.querySelector(`.tab[data-file="${filePath}"]`);
            if (tab) {
                const title = tab.querySelector('.tab-title span');
                if (fileData.modified && !title.textContent.endsWith('*')) {
                    title.textContent += '*';
                } else if (!fileData.modified && title.textContent.endsWith('*')) {
                    title.textContent = title.textContent.slice(0, -1);
                }
            }
        }
    }

    async saveFile() {
        if (!this.currentFile || !this.editor) {
            this.log('没有打开的文件', 'warning');
            return;
        }

        const content = this.editor.getValue();
        
        try {
            const response = await fetch('/api/files/write', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    path: this.currentFile,
                    content: content
                })
            });

            const data = await response.json();
            
            if (data.success) {
                // 更新文件状态
                const fileData = this.openFiles.get(this.currentFile);
                if (fileData) {
                    fileData.originalContent = content;
                    fileData.modified = false;
                }

                // 更新标签显示
                const tab = document.querySelector(`.tab[data-file="${this.currentFile}"]`);
                if (tab) {
                    const title = tab.querySelector('.tab-title span');
                    if (title.textContent.endsWith('*')) {
                        title.textContent = title.textContent.slice(0, -1);
                    }
                }

                this.log(`文件已保存: ${this.currentFile}`, 'success');
            } else {
                this.log(`保存失败: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('保存文件失败:', error);
            this.log('保存文件失败', 'error');
        }
    }

    async compileFile() {
        if (!this.currentFile) {
            this.log('没有打开的文件', 'warning');
            return;
        }

        if (!this.currentFile.endsWith('.aqua')) {
            this.log('只能编译 .aqua 文件', 'warning');
            return;
        }

        // 先保存文件
        await this.saveFile();

        this.log(`正在编译: ${this.currentFile}`, 'info');

        try {
            const response = await fetch('/api/compile', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    file_path: this.currentFile
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.log(`编译成功: ${data.message}`, 'success');
            } else {
                this.log(`编译失败: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('编译失败:', error);
            this.log('编译请求失败', 'error');
        }
    }

    async runFile() {
        if (!this.currentFile) {
            this.log('没有打开的文件', 'warning');
            return;
        }

        let filePath = this.currentFile;
        
        // 如果是 .aqua 文件，先编译
        if (filePath.endsWith('.aqua')) {
            await this.compileFile();
            filePath = filePath.replace('.aqua', '.acode');
        } else if (!filePath.endsWith('.acode')) {
            this.log('只能运行 .aqua 或 .acode 文件', 'warning');
            return;
        }

        this.log(`正在运行: ${filePath}`, 'info');

        try {
            const response = await fetch('/api/run', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    file_path: filePath
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.log('程序运行完成', 'success');
                if (data.output) {
                    this.log(data.output, 'info');
                }
            } else {
                this.log(`运行失败: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('运行失败:', error);
            this.log('运行请求失败', 'error');
        }
    }

    handleMenuAction(action) {
        switch (action) {
            case 'new-file':
                this.newFile();
                break;
            case 'open-file':
                this.openFile();
                break;
            case 'save-file':
                this.saveFile();
                break;
            case 'save-as':
                this.saveAsFile();
                break;
            case 'close-file':
                if (this.currentFile) {
                    this.closeFile(this.currentFile);
                }
                break;
            case 'undo':
                if (this.editor) this.editor.trigger('keyboard', 'undo');
                break;
            case 'redo':
                if (this.editor) this.editor.trigger('keyboard', 'redo');
                break;
            case 'cut':
                if (this.editor) this.editor.trigger('keyboard', 'cut');
                break;
            case 'copy':
                if (this.editor) this.editor.trigger('keyboard', 'copy');
                break;
            case 'paste':
                if (this.editor) this.editor.trigger('keyboard', 'paste');
                break;
            case 'find':
                if (this.editor) this.editor.trigger('keyboard', 'find');
                break;
            case 'replace':
                if (this.editor) this.editor.trigger('keyboard', 'replace');
                break;
            case 'compile':
                this.compileFile();
                break;
            case 'run':
                this.runFile();
                break;
            case 'about':
                this.showAbout();
                break;
        }
    }

    newFile() {
        const fileName = prompt('请输入文件名:', 'untitled.aqua');
        if (!fileName) return;

        const filePath = fileName;
        this.openFileInEditor(filePath, '// 新建 AquaScript 文件\n\n');
    }

    openFile() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.aqua,.acode,.txt';
        input.onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    this.openFileInEditor(file.name, e.target.result);
                };
                reader.readAsText(file);
            }
        };
        input.click();
    }

    saveAsFile() {
        if (!this.editor) {
            this.log('没有打开的编辑器', 'warning');
            return;
        }

        const content = this.editor.getValue();
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = this.currentFile ? this.currentFile.split('/').pop() : 'untitled.aqua';
        a.click();
        
        URL.revokeObjectURL(url);
    }

    showAbout() {
        const modal = document.getElementById('modal');
        const title = document.getElementById('modal-title');
        const body = document.getElementById('modal-body');
        
        title.textContent = '关于 AquaScript 编辑器';
        body.innerHTML = `
            <div style="text-align: center;">
                <h2 style="color: var(--accent-color); margin-bottom: 16px;">AquaScript 编辑器</h2>
                <p style="margin-bottom: 16px;">版本 1.0.0</p>
                <p style="margin-bottom: 16px;">一个现代化的 AquaScript 语言集成开发环境</p>
                
                <div style="text-align: left; margin-top: 24px;">
                    <h3 style="margin-bottom: 12px;">功能特性:</h3>
                    <ul style="list-style: none; padding: 0;">
                        <li style="margin-bottom: 8px;"><i class="fas fa-check" style="color: var(--success-color); margin-right: 8px;"></i>语法高亮</li>
                        <li style="margin-bottom: 8px;"><i class="fas fa-check" style="color: var(--success-color); margin-right: 8px;"></i>代码补全</li>
                        <li style="margin-bottom: 8px;"><i class="fas fa-check" style="color: var(--success-color); margin-right: 8px;"></i>文件管理</li>
                        <li style="margin-bottom: 8px;"><i class="fas fa-check" style="color: var(--success-color); margin-right: 8px;"></i>编译运行</li>
                        <li style="margin-bottom: 8px;"><i class="fas fa-check" style="color: var(--success-color); margin-right: 8px;"></i>主题切换</li>
                        <li style="margin-bottom: 8px;"><i class="fas fa-check" style="color: var(--success-color); margin-right: 8px;"></i>实时控制台</li>
                    </ul>
                </div>
                
                <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--border-color);">
                    <p style="color: var(--text-secondary); font-size: 14px;">
                        基于 Monaco Editor 构建<br>
                        © 2024 AquaScript 项目
                    </p>
                </div>
            </div>
        `;
        
        this.showModal();
    }

    showModal() {
        const overlay = document.getElementById('modal-overlay');
        overlay.classList.add('show');
    }

    closeModal() {
        const overlay = document.getElementById('modal-overlay');
        overlay.classList.remove('show');
    }

    showWelcomeScreen() {
        const welcome = document.getElementById('welcome-screen');
        const editor = document.getElementById('monaco-editor');
        
        if (welcome) welcome.style.display = 'flex';
        if (editor) editor.style.display = 'none';
    }

    hideWelcomeScreen() {
        const welcome = document.getElementById('welcome-screen');
        const editor = document.getElementById('monaco-editor');
        
        if (welcome) welcome.style.display = 'none';
        if (editor) editor.style.display = 'block';
    }

    toggleConsole() {
        const console = document.getElementById('console');
        const btn = document.getElementById('console-toggle');
        
        console.classList.toggle('collapsed');
        
        if (console.classList.contains('collapsed')) {
            btn.innerHTML = '<i class="fas fa-chevron-up"></i>';
        } else {
            btn.innerHTML = '<i class="fas fa-chevron-down"></i>';
        }
    }

    clearConsole() {
        const content = document.getElementById('console-content');
        if (content) {
            content.innerHTML = '';
        }
    }

    log(message, type = 'info') {
        const content = document.getElementById('console-content');
        if (!content) return;

        const line = document.createElement('div');
        line.className = `console-line ${type}`;
        
        const timestamp = new Date().toLocaleTimeString();
        line.innerHTML = `
            <span class="timestamp">[${timestamp}]</span>
            <span class="message">${message}</span>
        `;

        content.appendChild(line);
        content.scrollTop = content.scrollHeight;
    }
}

// 初始化编辑器
document.addEventListener('DOMContentLoaded', () => {
    window.editor = new AquaScriptEditor();
});