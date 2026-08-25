const vscode = require('vscode');
const http = require('http');

let server;
let statusBarItem;

function activate(context) {
    console.log('NJ IDE Copier is active');

    // Status bar
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = "$(cloud-download) NJ IDE Copier";
    statusBarItem.command = 'nj-ide-copier.startServer';
    statusBarItem.show();

    // Register commands
    let startServer = vscode.commands.registerCommand('nj-ide-copier.startServer', startServerCommand);
    let insertCode = vscode.commands.registerCommand('nj-ide-copier.insertCode', insertCodeAtCursor);

    context.subscriptions.push(startServer, insertCode, statusBarItem);
    startServerCommand();
}

function startServerCommand() {
    const config = vscode.workspace.getConfiguration('nj-ide-copier');
    const port = config.get('serverPort', 8765);

    if (server) {
        vscode.window.showInformationMessage('NJ IDE Copier server already running');
        return;
    }

    server = http.createServer((req, res) => {
        if (req.method === 'POST' && req.url === '/code/update') {
            let body = '';
            req.on('data', chunk => body += chunk);
            req.on('end', () => {
                try {
                    const data = JSON.parse(body);
                    insertCode(data.code, data.language);
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ status: 'success' }));
                } catch (error) {
                    res.writeHead(500, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ status: 'error', message: error.message }));
                }
            });
        } else {
            res.writeHead(404);
            res.end();
        }
    });

    server.listen(port, () => {
        statusBarItem.text = `$(check) NJ IDE Copier:${port}`;
        vscode.window.showInformationMessage(`NJ IDE Copier server started on port ${port}`);
    });
}

function insertCodeAtCursor() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showWarningMessage('No active editor');
        return;
    }

    // Insert from clipboard
    const clipboard = vscode.env.clipboard;
    clipboard.readText().then(text => {
        editor.edit(editBuilder => {
            const position = editor.selection.active;
            editBuilder.insert(position, text);
        });
    });
}

function insertCode(code, language) {
    const editor = vscode.window.activeTextEditor;
    if (!editor) return;

    editor.edit(editBuilder => {
        const position = editor.selection.active;
        editBuilder.insert(position, code);
    });
}

function deactivate() {
    if (server) server.close();
}

module.exports = { activate, deactivate };
