import * as vscode from "vscode";
import { basename } from "node:path";
import { execFile } from "node:child_process";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

let parseAbortController: AbortController | null = null;
let parse_result: string | null;
let statusBarMessage: vscode.Disposable | null = null;

let preview: vscode.WebviewPanel | null = null;

export function activate(context: vscode.ExtensionContext): void {
    const onDidChangeTextDisposable = vscode.workspace.onDidChangeTextDocument(parse);
    const onDidChangeEditorDisposable = vscode.window.onDidChangeActiveTextEditor(parse);

    const previewDisposable = vscode.commands.registerCommand("mesanote.preview", () => {
        openPreview(context);
    });

    context.subscriptions.push(onDidChangeTextDisposable);
    context.subscriptions.push(onDidChangeEditorDisposable);
    context.subscriptions.push(previewDisposable);

    parse();
}

async function parse(): Promise<void> {
    // Ensure there is an open text editor and its language is mesanote
    const editor = vscode.window.activeTextEditor;
    if (!editor || editor.document.languageId !== "mesanote") {
        statusBarMessage?.dispose();
        statusBarMessage = null;
        return;
    }

    // Abort ongoing parse 
    parseAbortController?.abort();
    parseAbortController = new AbortController();

    // Asynchronously parse via the CLI
    try {
        parse_result = (await execFileAsync(
            "mesa", ["text", editor.document.getText()],
            { signal: parseAbortController.signal }
        )).stdout;
    } catch (error) {
        if (!(error instanceof Error) || error.name !== "AbortError") {
            const errorMessage = getMesaErrorText(error as Error);

            statusBarMessage?.dispose();
            statusBarMessage = vscode.window.setStatusBarMessage(`$(warning) ${errorMessage}`);
        }

        return;
    }

    statusBarMessage?.dispose();
    statusBarMessage = null;

    updatePreview();
}

function getMesaErrorText(error: Error): string {
    if (error.message.includes("Error: ")) {
        return error.message.split("Error: ", 2)[1]?.trim() || error.message;
    }

    return "Unknown error occurred";
}

async function openPreview(context: vscode.ExtensionContext): Promise<void> {
    if (preview == null) {
        preview = vscode.window.createWebviewPanel(
            "mesanote",
            "Preview",
            vscode.ViewColumn.Active,
            {
                retainContextWhenHidden: true
            }
        );

        // Set up the handler for the preview being closed
        preview.onDidDispose(
            () => {
                preview = null;
                statusBarMessage?.dispose();
                statusBarMessage = null;
            },
            null,
            context.subscriptions
        );

        // Make sure parse has run at least once before previewing
        if (parse_result == null) {
            await parse(); 
        }

        updatePreview();
    } else {
        preview.reveal();
    }
}

function updatePreview(): void {
    if (preview == null) {
        return;
    }

    const editor = vscode.window.activeTextEditor;
    if (!editor || editor.document.languageId !== "mesanote") {
        return;
    }

    preview.title = "Preview " + basename(editor.document.fileName);
    preview.webview.html = parse_result || "";
}