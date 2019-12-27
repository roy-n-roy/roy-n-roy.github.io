# Visual Studio Codeでの編集環境構築

## Debug Extensionのインストール
どちらかお好みで  
[Debugger for Firefox - Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=firefox-devtools.vscode-firefox-debug)  
[Debugger for Chrome - Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=msjsdiag.debugger-for-chrome)  

## Pythonインストール
Windows10: [Get Python 3.7 - Microsoft Store](https://www.microsoft.com/store/productId/9NJ46SX7X90P)  
Ubuntu: `sudo apt install python3 python3-pip`  

## mkdocsの設定ファイルを作成
[Getting started -  Material for MkDocs](https://squidfunk.github.io/mkdocs-material/getting-started/#usage)を参考に、`mkdocs.yml`ファイルを作成します。  

## launch.jsonとtasks.jsonの設定
下記を設定する  

その後、まだMkDocsをインストールしていない場合は、  
`Ctrl+Shift+P`から`task`と入力し、`タスクの実行`を選択後、Task: `mkdocs-new` を実行

!!! example ".vscode/launch.json"
	<script src="https://gist.github.com/roy-n-roy/e5034b2725f694e659b8c4b30579a69b.js?file=launch.json"></script>

!!! example ".vscode/tasks.json"
	<script src="https://gist.github.com/roy-n-roy/e5034b2725f694e659b8c4b30579a69b.js?file=tasks.json"></script>
