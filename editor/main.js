const { app, BrowserWindow, Menu, shell, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http');

let mainWindow;
let loadingWindow;
let flaskProcess;

// 检查 Flask 服务是否运行
function checkFlaskServer(callback) {
    const req = http.request({
        hostname: 'localhost',
        port: 5000,
        path: '/',
        method: 'GET',
        timeout: 1000
    }, (res) => {
        callback(true);
    });
    
    req.on('error', () => {
        callback(false);
    });
    
    req.on('timeout', () => {
        req.destroy();
        callback(false);
    });
    
    req.end();
}

// 启动 Flask 服务
function startFlaskServer() {
    return new Promise((resolve, reject) => {
        // 首先检查服务是否已经运行
        checkFlaskServer((isRunning) => {
            if (isRunning) {
                console.log('Flask 服务已在运行');
                resolve();
                return;
            }
            
            console.log('启动 Flask 服务...');
            const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
            flaskProcess = spawn(pythonPath, ['app.py'], {
                cwd: __dirname,
                stdio: 'pipe'
            });
            
            flaskProcess.stdout.on('data', (data) => {
                console.log(`Flask: ${data}`);
                if (data.toString().includes('Running on')) {
                    setTimeout(resolve, 1000); // 给服务一点时间完全启动
                }
            });
            
            flaskProcess.stderr.on('data', (data) => {
                console.error(`Flask Error: ${data}`);
            });
            
            flaskProcess.on('close', (code) => {
                console.log(`Flask 进程退出，代码: ${code}`);
            });
            
            // 等待服务启动的超时处理
            setTimeout(() => {
                checkFlaskServer((isRunning) => {
                    if (isRunning) {
                        resolve();
                    } else {
                        reject(new Error('Flask 服务启动超时'));
                    }
                });
            }, 8000);
        });
    });
}

// 创建加载窗口
function createLoadingWindow() {
    loadingWindow = new BrowserWindow({
        width: 500,
        height: 600,
        frame: false,
        alwaysOnTop: true,
        transparent: true,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true
        },
        resizable: false,
        center: true
    });

    loadingWindow.loadFile(path.join(__dirname, 'loading.html'));
    
    loadingWindow.on('closed', () => {
        loadingWindow = null;
    });
}

function createWindow() {
    // 创建浏览器窗口
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1000,
        minHeight: 600,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            enableRemoteModule: false,
            webSecurity: false
        },
        icon: path.join(__dirname, 'assets', 'icon.png'), // 如果有图标的话
        show: false, // 先不显示，等加载完成后再显示
        titleBarStyle: 'default',
        frame: true,
        title: 'AquaScript Editor'
    });

    // 启动 Flask 服务并加载页面
    startFlaskServer()
        .then(() => {
            // 等待一下确保服务完全就绪
            setTimeout(() => {
                mainWindow.loadURL('http://localhost:5000');
                
                // 当主窗口准备好显示时
                mainWindow.once('ready-to-show', () => {
                    if (loadingWindow) {
                        loadingWindow.close();
                    }
                    mainWindow.show();
                    mainWindow.focus();
                });
            }, 1500);
        })
        .catch((error) => {
            console.error('启动失败:', error);
            if (loadingWindow) {
                loadingWindow.close();
            }
            dialog.showErrorBox('启动错误', '无法启动 AquaScript 编辑器服务。请确保 Python 已安装并且依赖包已正确安装。\n\n错误详情: ' + error.message);
            app.quit();
        });

    // 当窗口关闭时触发
    mainWindow.on('closed', () => {
        mainWindow = null;
    });

    // 处理外部链接
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        shell.openExternal(url);
        return { action: 'deny' };
    });
}

// 加载应用
async function loadApp() {
    try {
        // 检查 Flask 服务器是否已经运行
        const isRunning = await checkFlaskServer();
        
        if (!isRunning) {
            // 显示加载页面
            mainWindow.loadFile(path.join(__dirname, 'loading.html'));
            
            // 启动 Flask 服务器
            await startFlaskServer();
            
            // 等待服务器完全启动
            let retries = 0;
            while (retries < 30) {
                const serverReady = await checkFlaskServer();
                if (serverReady) break;
                await new Promise(resolve => setTimeout(resolve, 1000));
                retries++;
            }
        }
        
        // 加载主应用
        mainWindow.loadURL(`http://localhost:${FLASK_PORT}`);
        
    } catch (error) {
        console.error('启动应用失败:', error);
        
        // 显示错误页面
        const errorHtml = `
            <!DOCTYPE html>
            <html>
            <head>
                <title>启动失败</title>
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        text-align: center; 
                        padding: 50px;
                        background: #f5f5f5;
                    }
                    .error { 
                        background: white; 
                        padding: 30px; 
                        border-radius: 8px; 
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        max-width: 500px;
                        margin: 0 auto;
                    }
                    h1 { color: #e74c3c; }
                    button {
                        background: #3498db;
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 4px;
                        cursor: pointer;
                        margin: 10px;
                    }
                </style>
            </head>
            <body>
                <div class="error">
                    <h1>启动失败</h1>
                    <p>无法启动 AquaScript 编辑器后端服务</p>
                    <p>请确保已安装 Python 和 Flask</p>
                    <button onclick="location.reload()">重试</button>
                </div>
            </body>
            </html>
        `;
        
        mainWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(errorHtml)}`);
    }
}

// 创建菜单
function createMenu() {
    const template = [
        {
            label: '文件',
            submenu: [
                {
                    label: '新建文件',
                    accelerator: 'CmdOrCtrl+N',
                    click: () => {
                        mainWindow.webContents.executeJavaScript('window.editor && window.editor.newFile()');
                    }
                },
                {
                    label: '打开文件',
                    accelerator: 'CmdOrCtrl+O',
                    click: async () => {
                        const result = await dialog.showOpenDialog(mainWindow, {
                            properties: ['openFile'],
                            filters: [
                                { name: 'AquaScript 文件', extensions: ['aqua'] },
                                { name: '字节码文件', extensions: ['acode'] },
                                { name: '所有文件', extensions: ['*'] }
                            ]
                        });
                        
                        if (!result.canceled && result.filePaths.length > 0) {
                            const filePath = result.filePaths[0];
                            const content = fs.readFileSync(filePath, 'utf8');
                            const fileName = path.basename(filePath);
                            
                            mainWindow.webContents.executeJavaScript(`
                                window.editor && window.editor.openFileInEditor('${fileName}', \`${content.replace(/`/g, '\\`')}\`)
                            `);
                        }
                    }
                },
                {
                    label: '保存',
                    accelerator: 'CmdOrCtrl+S',
                    click: () => {
                        mainWindow.webContents.executeJavaScript('window.editor && window.editor.saveFile()');
                    }
                },
                { type: 'separator' },
                {
                    label: '退出',
                    accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
                    click: () => {
                        app.quit();
                    }
                }
            ]
        },
        {
            label: '编辑',
            submenu: [
                { label: '撤销', accelerator: 'CmdOrCtrl+Z', role: 'undo' },
                { label: '重做', accelerator: 'Shift+CmdOrCtrl+Z', role: 'redo' },
                { type: 'separator' },
                { label: '剪切', accelerator: 'CmdOrCtrl+X', role: 'cut' },
                { label: '复制', accelerator: 'CmdOrCtrl+C', role: 'copy' },
                { label: '粘贴', accelerator: 'CmdOrCtrl+V', role: 'paste' },
                { label: '全选', accelerator: 'CmdOrCtrl+A', role: 'selectall' }
            ]
        },
        {
            label: '编译',
            submenu: [
                {
                    label: '编译',
                    accelerator: 'F9',
                    click: () => {
                        mainWindow.webContents.executeJavaScript('window.editor && window.editor.compileFile()');
                    }
                },
                {
                    label: '运行',
                    accelerator: 'F5',
                    click: () => {
                        mainWindow.webContents.executeJavaScript('window.editor && window.editor.runFile()');
                    }
                }
            ]
        },
        {
            label: '视图',
            submenu: [
                {
                    label: '切换主题',
                    accelerator: 'CmdOrCtrl+T',
                    click: () => {
                        mainWindow.webContents.executeJavaScript('window.editor && window.editor.toggleTheme()');
                    }
                },
                { type: 'separator' },
                { label: '重新加载', accelerator: 'CmdOrCtrl+R', role: 'reload' },
                { label: '强制重新加载', accelerator: 'CmdOrCtrl+Shift+R', role: 'forceReload' },
                { label: '开发者工具', accelerator: 'F12', role: 'toggleDevTools' },
                { type: 'separator' },
                { label: '实际大小', accelerator: 'CmdOrCtrl+0', role: 'resetZoom' },
                { label: '放大', accelerator: 'CmdOrCtrl+Plus', role: 'zoomIn' },
                { label: '缩小', accelerator: 'CmdOrCtrl+-', role: 'zoomOut' },
                { type: 'separator' },
                { label: '全屏', accelerator: 'F11', role: 'togglefullscreen' }
            ]
        },
        {
            label: '帮助',
            submenu: [
                {
                    label: '关于 AquaScript Editor',
                    click: () => {
                        mainWindow.webContents.executeJavaScript('window.editor && window.editor.showAbout()');
                    }
                },
                {
                    label: '访问项目主页',
                    click: () => {
                        shell.openExternal('https://github.com/aquascript/editor');
                    }
                }
            ]
        }
    ];

    // macOS 特殊处理
    if (process.platform === 'darwin') {
        template.unshift({
            label: app.getName(),
            submenu: [
                { label: '关于 ' + app.getName(), role: 'about' },
                { type: 'separator' },
                { label: '服务', role: 'services', submenu: [] },
                { type: 'separator' },
                { label: '隐藏 ' + app.getName(), accelerator: 'Command+H', role: 'hide' },
                { label: '隐藏其他', accelerator: 'Command+Shift+H', role: 'hideothers' },
                { label: '显示全部', role: 'unhide' },
                { type: 'separator' },
                { label: '退出', accelerator: 'Command+Q', click: () => app.quit() }
            ]
        });
    }

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
}

// 应用准备就绪时创建窗口
app.whenReady().then(() => {
    createLoadingWindow();
    createWindow();
    createMenu();

    app.on('activate', () => {
        // 在 macOS 上，当点击 dock 图标并且没有其他窗口打开时，
        // 通常会重新创建一个窗口
        if (BrowserWindow.getAllWindows().length === 0) {
            createLoadingWindow();
            createWindow();
        }
    });
});

// 当所有窗口都关闭时退出应用
app.on('window-all-closed', () => {
    // 在 macOS 上，应用通常会保持活动状态，即使没有窗口打开
    // 直到用户明确使用 Cmd + Q 退出
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// 应用退出前清理
app.on('before-quit', () => {
    if (flaskProcess) {
        console.log('关闭 Flask 服务器...');
        flaskProcess.kill();
    }
});

// 忽略证书错误（仅用于开发）
app.on('certificate-error', (event, webContents, url, error, certificate, callback) => {
    event.preventDefault();
    callback(true);
});