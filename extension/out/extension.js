"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
const vscode = __importStar(require("vscode"));
const node_child_process_1 = require("node:child_process");
const path = __importStar(require("node:path"));
let preview = null;
function activate(context) {
    const previewDisposable = vscode.commands.registerCommand("mesanote.preview", () => {
        openPreview(context);
    });
    context.subscriptions.push(previewDisposable);
}
function openPreview(context) {
    if (preview == null) {
        preview = vscode.window.createWebviewPanel("mesanote", "Preview", vscode.ViewColumn.Active);
        // Handle the preview being closed
        preview.onDidDispose(() => {
            preview = null;
        }, null, context.subscriptions);
        updatePreview();
        const onDidChangeTextDisposable = vscode.workspace.onDidChangeTextDocument(updatePreview);
        const onDidChangeEditorDisposable = vscode.window.onDidChangeActiveTextEditor(updatePreview);
        context.subscriptions.push(onDidChangeTextDisposable);
        context.subscriptions.push(onDidChangeEditorDisposable);
    }
    else {
        preview.reveal();
    }
}
function updatePreview() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        return;
    }
    const document = editor.document;
    if (document.languageId !== "mesanote") {
        return;
    }
    if (!preview) {
        return;
    }
    preview.title = "Preview " + path.basename(document.fileName);
    let html;
    try {
        html = (0, node_child_process_1.execSync)("mesa text", { input: document.getText() }).toString();
    }
    catch (error) {
        // const message = (error as Error).message.split("Error: ")[1];
        // vscode.window.showWarningMessage(message);
        return;
    }
    preview.webview.html = html;
}
//# sourceMappingURL=extension.js.map