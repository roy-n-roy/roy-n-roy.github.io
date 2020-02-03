# Djangoアプリケーション
Djangoとは、Pythonで利用できるWebアプリケーションフレームワークです。  

この記事では、Djangoを使って開発したアプリケーションをDocker環境へデプロイした際の手順を記載します。  

## 前提
* Djangoアプリケーションが開発環境で動作している。
* Dockerがインストールされた環境が存在している。

## 準備
### ベースイメージの選定
オリジナルのアプリケーションをDocker上で動作させるため、専用のDockerイメージを作成する必要があります。
しかし、1からイメージを作成するのはたいへんなので、ある程度利用するアプリケーションが決まっていれば、それにかなう物をベースとして利用します。
今回はPythonでDjangoアプリケーションを動かすので、`python:3.8-alpine`を選択しました。  

Pythonのバージョンは、開発でも使用している現時点で最新のものを、ディストリビューションはAlpine Linuxのものを選択しています。
alpineの付かない`python:3.8`で採用されているDebianではなく、Alpine Linuxのものを選んだのは、「イメージのサイズが小さい」という理由からです。  

なお、Dockerオフィシャルイメージに、ずばり`django`というものも存在するのですが、3年以上メンテナンスされておらず、Djangoのバージョンも古いため採用は見送りました。

### データベースの選定
Djangoアプリケーションでは、ユーザが登録したデータを保存するためにリレーショナルデータベースを使用しています。  
利用可能なデータベースはいくつかあるため、その中から使用するデータベースバックエンドを選択します。

今回の開発時にはsqlite3を利用していますが、本番用にはこちら[^1]を参考にしてPostgreSQLを選択しました。  
理由は個人的嗜好によるものです。

## コンテナ設計


## Djangoアプリケーションの設定
### Django設定ファイルの修正
Djangoアプリケーションの設定は`django-admin startproject`で作成したディレクトリ内に`settings.py`というファイルに記載されています。  
ここに設定されている値の初期値は開発向けに設定されているため、本番環境用に設定値に変更していきます。  
ただしDockerコンテナで動作させるため、コンテナ内の環境変数から設定値を取得できるようにし、コンテナ実行時に設定値を注入できるようにしています。

* セキュリティ関連  
	`SECRET_KEY`は環境変数から取得するようにして、後述のDockerファイル内にて実行時に動的に生成するようにしています。  
	ただし、この場合はデプロイ毎に`SECRET_KEY`の値が変わるため、その度にユーザーセッションなどがリセットされるため注意が必要です。  
	<script src="https://gist-it.appspot.com/https://github.com/roy-n-roy/DockerHubUpdateNotifier/blob/v1.1.1/django/config/settings.py?slice=23:36&footer=no"></script>

* データベース設定  
	<script src="https://gist-it.appspot.com/https://github.com/roy-n-roy/DockerHubUpdateNotifier/blob/v1.1.1/django/config/settings.py?slice=101:114&footer=no"></script>

* ロケール設定  
	<script src="https://gist-it.appspot.com/https://github.com/roy-n-roy/DockerHubUpdateNotifier/blob/v1.1.1/django/config/settings.py?slice=139:153&footer=no"></script>

* ログ設定  
	ログはコンテナ側で管理するため、ファイルではなく、標準出力に表示するよう設定しました。  
	<script src="https://gist-it.appspot.com/https://github.com/roy-n-roy/DockerHubUpdateNotifier/blob/v1.1.1/django/config/settings.py?slice=194:211&footer=minimal"></script>

その他に、Eメールの送信が必要な場合は、メールバックエンドの設定が必要です。

### Djangoのデプロイ時チェック
Djangoには管理コマンドでデプロイ時のチェックをする機能が備わっています。  
せっかくあるので、使用してみます。

`python manage.py check --deploy`  

いくつか警告が出たので、ドキュメント[^2]を参考にしながらsettings.pyを修正しました。  

## Dockerファイル、docker-composeファイルの作成
アプリケーション側の準備が整ったので、次はDocker側の設定ファイルを書いていきます。


<script src="https://gist-it.appspot.com/https://github.com/roy-n-roy/DockerHubUpdateNotifier/blob/v1.1.1/Dockerfile?footer=minimal"></script>

ポイントを下記に挙げます。  
* 環境変数 `SECRET_KEY` を設定するコマンドを `~/.profile` に追記しています。
* 

<script src="https://gist-it.appspot.com/https://github.com/roy-n-roy/DockerHubUpdateNotifier/blob/v1.1.1/docker-compose.yml?footer=minimal"></script>



[^1]: [データベース | Django ドキュメント](https://docs.djangoproject.com/ja/3.0/ref/databases/)
[^2]: [デプロイチェックリスト | Django ドキュメント](https://docs.djangoproject.com/ja/3.0/howto/deployment/checklist/)


https://github.com/unbit/uwsgi/blob/master/logo_uWSGI.svg
https://www.djangoproject.com/community/logos/
http://nginx.org/
https://www.python.org/community/logos/
https://www.postgresql.org/media/img/about/press/slonik_with_black_text_and_tagline.gif