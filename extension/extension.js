const vscode = require("vscode");
const { execSync } = require("node:child_process");
const path = require("path")

let preview = null;

function activate(context) {
	const previewDisposable = context.subscriptions.push(
		vscode.commands.registerCommand("mesanote.preview", () => { openPreview(context); })
	);

	context.subscriptions.push(previewDisposable);
}

function openPreview(context) {
	if (preview == null) {
		const document = vscode.window.activeTextEditor.document
		preview = vscode.window.createWebviewPanel(
			"mesanote",
			null,
			vscode.ViewColumn.Active
		);

		updatePreview();

		const onDidChangeTextDisposable = vscode.workspace.onDidChangeTextDocument(updatePreview)
		const onDidChangeEditorDisposable = vscode.window.onDidChangeActiveTextEditor(updatePreview)

		context.subscriptions.push(onDidChangeTextDisposable);
		context.subscriptions.push(onDidChangeEditorDisposable);
	} else {
		preview.reveal()
	}
}

function updatePreview() { 
	let document = vscode.window.activeTextEditor.document;
	if (document.languageId != "mesanote") {
		return;
	}

	preview.title = "Preview " + path.basename(document.fileName);

	let html;
	try {
		html = execSync("mesa text", { input: document.getText() }).toString();
	} catch (error) {
		return;
	}

	preview.webview.html = html;
}

module.exports = { activate }	