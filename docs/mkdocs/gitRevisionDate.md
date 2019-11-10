# git-revision-dateプラグイン
> [zhaoterryy/mkdocs-git-revision-date-plugin - GitHub](https://github.com/zhaoterryy/mkdocs-git-revision-date-plugin)  
> MkDocs plugin for setting revision date from git per markdown file.  

git-revision-dateプラグインを使用すると、Git上で管理しているMarkdownファイルの更新日時をページ上に表示することができます。

## インストール
下記のコマンドを実行します。  
```
pip install mkdocs-git-revision-date-plugin
```

続いて、`mkdocs.yml`ファイルに下記を追記します。  
```
plugins:
  - search
  - git-revision-date
```

プラグインをまだ1つも設定していない場合は、デフォルトでsearchプラグインが有効になっているため、searchプラグインも明示的に記載しておきます。

## Markdownファイル毎に表示を設定
Markdownファイル内に下記のように記入することで、最終更新日が表示されます。

&#x7b;&#x7b; git_revision_date &#x7d;&#x7d; => {{ git_revision_date }}

ただし、この方法の場合、日付を表示したいファイル全てに設定が必要になります。

## テンプレートファイルに埋め込む

Mkdocsのテンプレートファイルに下記のように記入することで、全てのページに最終更新日が表示されます。  

&#x7b;&#x7b; page.meta.revision_date &#x7d;&#x7d; => {{ git_revision_date }}

### テンプレートをカスタマイズする

このサイトの場合は、materialテーマを使用しているので、materialのテンプレートファイルを元にテンプレートを編集します。
pipでインストールしている場合は `pip show mkdocs-material` コマンドでインストール先を確認できます。

```
> pip show mkdocs-material
Name: mkdocs-material
Version: 4.4.3
Summary: A Material Design theme for MkDocs
Home-page: https://squidfunk.github.io/mkdocs-material/
Author: Martin Donath
Author-email: martin.donath@squidfunk.com
License: MIT
Location: c:\users\XXXX\appdata\local\packages\pythonsoftwarefoundation.python.3.7_qbz5n2kfra8p0\localcache\local-packages\python37\site-packages
Requires: mkdocs, mkdocs-minify-plugin, Pygments, pymdown-extensions
Required-by:
```

上記のフォルダから `base.html` ファイルをコピーしてきましたので、それを編集します。  
今回は、メインコンテンツの上部に表示したかったので、下記のコードを 	<code>&#x7b;% block content %&#x7d;</code>の前に挿入しました。  

!!! Example "base.html"
	<div class="codehilite"><span class="nv">
	&#x3c;article class="md-content__inner md-typeset"&#x3e;  
	&emsp;&#x7b;% if page and page.meta and page.meta.revision_date and not page.meta.is_index and not page.is_homepage %&#x7d;  
	&emsp;&emsp;&#x3c;div class="git_revision_date"&#x3e;  
	&emsp;&emsp;最終更新日: &#x7b;&#x7b; page.meta.revision_date &#x7d;&#x7d;  
	&emsp;&emsp;&#x3c;/div&#x3e;  
	&emsp;&#x7b;% endif %&#x7d;  
	&emsp;&#x7b;% block content %&#x7d;  
	</span></div>

なお、git-revision-dateプラグインのREADMEでは、 <code>&#x7b;% if page.meta.revision_date &#x7d;</code> と書かれているのですが、
これだけだとビルドエラーが発生するため、 <code>&emsp;&#x7b;% if page and page.meta and page.meta.revision_date ...</code> としています。  

### 特定のページで最終更新日を表示しない
トップページでは更新日時を表示したくない場合は、テンプレートのif文の部分を下記のようにすると、トップページでは表示されないようになります。  
<div class="codehilite"><span class="nv">
&#x7b;% if page and page.meta ... <span class="mi">and not page.is_homepage</span> %&#x7d;  
</span></div>
