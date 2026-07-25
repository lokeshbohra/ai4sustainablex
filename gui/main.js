const { app, BrowserWindow, shell } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

let mainWindow;
let backendProcess = null;

const BACKEND_URL = 'http://localhost:8000';
const isDev = process.argv.includes('--dev');

function startBackend() {
  const pythonScript = path.join(__dirname, '..', 'main.py');
  const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';

  try {
    backendProcess = spawn(pythonCmd, [pythonScript], {
      detached: false,
      stdio: 'pipe',
      cwd: path.join(__dirname, '..'),
    });

    backendProcess.stdout.on('data', (data) => {
      console.log(`[Backend]: ${data}`);
    });

    backendProcess.stderr.on('data', (data) => {
      console.error(`[Backend Error]: ${data}`);
    });

    backendProcess.on('close', (code) => {
      console.log(`Backend exited with code ${code}`);
    });
  } catch (err) {
    console.error('Failed to start backend:', err);
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    title: 'ai4sustainablex — ESG Reporting Toolkit',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
    icon: path.join(__dirname, '..', 'assets', 'icon.png'),
  });

  mainWindow.loadURL(BACKEND_URL);

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  startBackend();
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (backendProcess) {
    backendProcess.kill();
    backendProcess = null;
  }
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  if (backendProcess) {
    backendProcess.kill();
    backendProcess = null;
  }
});