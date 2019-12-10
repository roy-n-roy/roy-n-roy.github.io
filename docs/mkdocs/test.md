# リンク切れのテスト
MarkdownでWebサイトのページを作成してしばらくすると、記事をカテゴリ別に分類したり、カテゴリを統合したりしたくなる場合があります。  
そうなると現状、カテゴリ分類はフォルダで行っているので、記事のURLが変わってしまい、リンク切れを起こすことがありました。  

きちんとテストしたい場合は、W3CのValidatorを利用するのが良いかと思います。  
[The W3C Markup Validation Service](https://validator.w3.org)

ですが、今回はローカルで簡単にチェックしたかったため、リンク切れ有無をチェックするテストコードを書くことにしました。  

## テストツールのセットアップ
mkdocsはPython製のツールなので、すでにPythonがインストールされています。  
なので、今回はPython製のテストフレームワークであるpytestを利用することにしました。  

まずはpytestをpipコマンドでインストールします。

```
pip install pytest
```

続いて、スクレイピング、HTMLパース用にbeautifulsoap4,  requests, lxmlを、  
また、テスト対象のページは複数あるため、並列化してテストするためにaiohttpもインストールします。

```
pip install bs4 requests lxml aiohttp[speedups]
```

続いて、pytestの設定ファイルを作成します。
`pytest.ini`というファイルをワークスペースフォルダ(`mkdocs.yml`と同じ階層のフォルダ)に作成して、下記のように編集します。

```
[pytest]
testpaths = ./tests
python_files = test_*.py
python_classes = Test
python_functions = test_
```

これで、pytestコマンドを実行すると、`${ワークスペースフォルダ}/tests/test_*.py`にマッチするPythonスクリプト内の`test_～`から始まる関数が、テスト対象としてテストが実行されるようになります。  

## Visual Studio Codeのテストタスク設定
Visual Studio Code(VSCode)でテストタスクとして実行できるように設定してます。  

まず、VSCodeからpytestを呼び出す際の設定を`.vscode/settings.json`に追記します。ファイルがない場合は、ファイルを作成してください。  

```
{
	"python.testing.pytestArgs": [],
	"python.testing.unittestEnabled": false,
	"python.testing.nosetestsEnabled": false,
	"python.testing.pytestEnabled": true
}
```

続いて、`.vscode/settings.json`に下記を追記します。

```
{
	"tasks": [
		{
			"label": "mkdocs-test",
			"type": "shell",
			"command": "py.test",
			"group": {
				"kind": "test",
				"isDefault": true
			}
		}
	]
}
```

以上で、VSCodeで対象のワークスペースを開いた状態で、`Ctrl+Shift+P`から「テスト タスクの実行」を呼び出すとpytestが実行されるようになりました。  

## テストコードの作成
ここまでで、テスト環境は整いましたので、ここからはテストの内容を作成していきます。  
今回は、リンク切れのテストのため、下記のようなテストスクリプトを作成しました。

注意したポイント:

* テストエラーを出力する`assert`文はasync関数内で出力しても  
	pytestがキャッチできないため、エラーの場合はコールバック関数で戻す。
* aiohttpでローカルのmkdocs serveに並列アクセスする場合、いくらローカルとは言え並列数を制限しないとファイルディスクリプタが不足するため、セマフォを利用して並列数を制限する。


<script src="https://gist-it.appspot.com/https://github.com/roy-n-roy/roy-n-roy.github.io/blob/docs/tests/test_url_link.py"></script>

## 実行結果
スクリプト作成後、27ページ 約10,000のリンクを対象として実行してみました。  
リンク切れを起こした場合には、テスト結果でエラーと対象のリンクが表示されています。  

処理時間は下記表の通りです。「コア数×周波数に影響してリニアに」とは行きませんでしたが、概ね並列化の恩恵が得られていそうです。

| 環境           | CPU                         | メモリ | 処理時間 |
| -------------- | --------------------------- | ------ | -------- |
| Surface GO     | Pentium 4415Y@1.60GHz 2Core | 8GB    | 23.6秒   |
| デスクトップPC | Ryzen 3600X@3.8GHz 6Core    | 32GB   | 7.3秒    |

<figure style="text-align: center;">
<a href="/imgs/mkdocs_test_result_success.png" data-lightbox="mkdocs_test_result"><img src="/imgs/mkdocs_test_result_success.png" width=48% /></a>
<a href="/imgs/mkdocs_test_result_error.png" data-lightbox="mkdocs_test_result"><img src="/imgs/mkdocs_test_result_error.png" width=48% /></a>
<figcaption>図. VSCodeでのテスト成功時とテストエラー時</figcaption></figure>

