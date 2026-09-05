import * as vscode from "vscode";
import { execSync } from "node:child_process";
import * as path from "node:path";

let preview: vscode.WebviewPanel | null = null;

export function activate(context: vscode.ExtensionContext): void {
  const previewDisposable = vscode.commands.registerCommand("mesanote.preview", () => {
    openPreview(context);
  });

  context.subscriptions.push(previewDisposable);
}

function openPreview(context: vscode.ExtensionContext): void {
  if (preview == null) {
    preview = vscode.window.createWebviewPanel(
      "mesanote",
      "Preview",
      vscode.ViewColumn.Active
    );

    // Handle the preview being closed
    preview.onDidDispose(
      () => {
        preview = null;
      },
      null,
      context.subscriptions
    );

    updatePreview();

    const onDidChangeTextDisposable = vscode.workspace.onDidChangeTextDocument(updatePreview);
    const onDidChangeEditorDisposable = vscode.window.onDidChangeActiveTextEditor(updatePreview);

    context.subscriptions.push(onDidChangeTextDisposable);
    context.subscriptions.push(onDidChangeEditorDisposable);
  } else {
    preview.reveal();
  }
}

function updatePreview(): void {
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

  let html: string;
  try {
    html = execSync("mesa text", { input: document.getText() }).toString();
  } catch (error) {
    // const message = (error as Error).message.split("Error: ")[1];
    // vscode.window.showWarningMessage(message);
    return;
  }

  preview.webview.html = html;
}