# Google Analyticsの設定
mkdocsのmaterialテーマにはGoogle Analyticsのタグを設定することができます。  

[Getting started -  Material for MkDocs](https://squidfunk.github.io/mkdocs-material/getting-started/#usage)を参考に、`mkdocs.yml`に追記することで設定できます。

## デバッグ用ブラウザプロファイルの作成と設定
Google Analyticsを利用しているのですが、デバッグ時のアクセスは解析対象にしたくありません。  
そこで、デバッグ用のブラウザプロファイルを作成し、そこに[Google アナリティクス オプトアウト アドオン](https://tools.google.com/dlpage/gaoptout)をインストールします。  

ここでは、Firefoxでの手順を記載します。  

### Firefoxプロファイルの作成

Mozillaのリファレンス[^1]を参考にして、Firefoxのユーザープロファイルの作成とアドオンの追加をしていきます。  
別のPCでもgitで同期して共通の設定を利用したいため、プロファイルはgitリポジトリの中の`.vscode`フォルダー内に作成することにします。  

作業はPowershellで進めていきます。  

```
cd [gitフォルダー]\.vscode
mkdir firefox_debug_profile
& 'C:\Program Files\Mozilla Firefox\firefox.exe' -new-instance -CreateProfile "debug $PWD\firefox_debug_profile"
```

これで、プロファイルの作成が完了しました。

### オプトアウトアドオンの追加
続いて、作成したプロファイルに、[Google アナリティクス オプトアウト アドオン](https://tools.google.com/dlpage/gaoptout)を追加します。

今回は上記のリンク先から、アドオンのファイル「gaoptoutaddon_1.0.8.xpi」をダウンロードしました。

次に、作成したプロファイルでFirefoxを起動します。  

```
cd [gitフォルダー]\.vscode
& 'C:\Program Files\Mozilla Firefox\firefox.exe' -new-instance -Profile "debug $PWD\firefox_debug_profile"
```

そして、起動したFirefoxのURL欄に`about:addons`と入力し、アドオンマネージャー画面を開きます。

アドオンマネージャー画面が開いたら、画面右上の歯車ボタンをクリック後、「ファイルからアドオンをインストール」を選択し、先ほどダウンロードした「gaoptoutaddon_1.0.8.xpi」を開きます。  
<a href="/imgs/mkdocs_vscode_firefox_plugin_install1.png" data-lightbox="image">
<img src="/imgs/mkdocs_vscode_firefox_plugin_install1.png" width="80%" /></a>

アドオンのインストールが完了後に画面左ペインで「拡張機能」をクリックすると拡張機能の管理画面が表示され、Google Analytics オプトアウト アドオンがインストールされていることが確認できます。  
<a href="/imgs/mkdocs_vscode_firefox_plugin_install2.png" data-lightbox="image">
<img src="/imgs/mkdocs_vscode_firefox_plugin_install2.png" width="80%" /></a>

### アドオンのプライベートウィンドウでの実行許可
デバッグ時はプライベートモードとしてFirefoxが起動するため、デバッグ時にアドオンを有効化するためには、プライベートウィンドウでの実行許可を与える必要があります。  

これは、インストール完了時のポップアップ画面で設定することもできますが、インストール後に設定が可能です。  

作業は引き続き、Firefoxの画面で行います。  

アドオンマネージャー画面内の拡張機能の管理を表示後、「Google Analytics オプトアウト アドオン」の右に表示されている「・・・」ボタンをクリックし「管理」を選択すると、下記のような画面が表示されます。  

<a href="/imgs/mkdocs_vscode_firefox_plugin_install3.png" data-lightbox="image">
<img src="/imgs/mkdocs_vscode_firefox_plugin_install3.png" width="80%" /></a>

ここで、「プライベートウィンドウでの実行」の項目で「許可」を選択すると、デバッグ時にもアドオンが有効になります。  

### デバッグ時のプロファイル読み込み設定
`.vscode/launch.json`を開き、デバッグ設定に下記のようにプロファイル指定の1行を追加します。  

!!! example ".vscode/launch.json"

	``` json hl_lines="9"
	{
		"version": "0.2.0",
		"configurations": [
			{
				"name": "mkdocs",
				"type": "firefox",
				"request": "launch",
				"reAttach": true,
				"profileDir": "${workspaceFolder}\\.vscode\\firefox_debug_profile",
				"url": "http://localhost:8000/",
				"webRoot": "${workspaceFolder}/site",
				"preLaunchTask": "mkdocs-serve",
				"postDebugTask": "mkdocs-stop"
			}
		]
	}
	```

設定を追加後、デバッグ実行してみてFirefox上でプラグインが読み込まれていることを確認しておきましょう。  

[^1]: [コマンドラインオプション - Mozilla | MDN](https://developer.mozilla.org/ja/docs/Mozilla/Command_Line_Options#User_Profile)