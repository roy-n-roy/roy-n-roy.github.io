# Djangoアプリケーション
Djangoとは、Pythonで利用できるWebアプリケーションフレームワークです。  

この記事では、Djangoを使って開発したアプリケーションをDocker環境へデプロイした際の手順を記載します。  

## 前提
この記事では、下記を前提として書かれています。

* Djangoアプリケーションを開発し、開発環境で動作している。
* Dockerがインストールされた環境が存在している。

## 準備
### ベースイメージの選定
オリジナルのアプリケーションをDocker上で動作させるため、専用のDockerイメージを作成する必要があります。
しかし、1からイメージを作成するのはたいへんなので、ある程度利用するアプリケーションが決まっていれば、それにかなう物をベースとして利用します。

今回はPythonでDjangoアプリケーションを動かすので、`python:3.8-alpine`を選択しました。  

Pythonのバージョンは、開発でも使用している現時点で最新のものを選び、ディストリビューションはAlpine Linuxのものを選択しています。  
alpineの付かない`python:3.8`でベースとしているDebianではなく、Alpine Linuxのものを選んだのは、「イメージのサイズが小さい」という理由からです。  

また、Dockerオフィシャルイメージに、ずばり`django`というものも存在するのですが、3年以上メンテナンスされておらず、Djangoのバージョンも古いため採用は見送りました。

### データベースの選定
Djangoアプリケーションでは、ユーザが登録したデータを保存するためにリレーショナルデータベースを使用しています。  
利用可能なデータベースは[いくつか](https://docs.djangoproject.com/ja/3.0/ref/databases/)[^1]あるため、その中から使用するデータベースバックエンドを選択します。

今回は、PostgreSQLを選択しました。理由は個人的嗜好によるものです。

### コンテナ設計
下記のような感じにしたいと思います。[^2]

<figure style="text-align: center;">
<a href="/imgs/docker_django_arch.png" data-lightbox="docker_django_arch"><img style="float: left;" src="/imgs/docker_django_arch.png" width=100% /></a>  
<figcaption>図 1. コンテナ構成図</figcaption>
</figure>

* 外部に公開するネットワークポートはnginxが後悔するHTTP(80)/HTTPS(443)のみとします。
* nginxでHTTP over SSL/TLS(HTTPS)に対応させます。  
	証明書はLet's Encryptで取得します。
* 画像などの静的コンテンツは共有Volumeに置き、Webアプリを介さずにnginxから直接配信します。
* Djangoアプリは、Webアプリと定期バッチアプリがあります。  
	これらは同じイメージを使用するが、コンテナは別々に2つ起動します。
* nginxとWebアプリの接続には、uWSGIを使用します。
* 各コンテナ間の通信には、Docker内部ネットワークを使用します。

## Djangoアプリケーションの設定
### Djangoのデプロイ時チェック
Djangoには管理コマンドに、デプロイ時のチェックをする機能が備わっています。  
せっかくあるので、実行してみます。

``` bash hl_lines="1"
$ python manage.py check --deploy

System check identified some issues:

WARNINGS:
?: (security.W004) You have not set a value for the SECURE_HSTS_SECONDS setting.
If your entire site is served only over SSL, you may want to consider setting a
value and enabling HTTP Strict Transport Security. Be sure to read the
documentation first; enabling HSTS carelessly can cause serious, irreversible
problems.
?: (security.W006) Your SECURE_CONTENT_TYPE_NOSNIFF setting is not set to True,
so your pages will not be served with an 'x-content-type-options: nosniff' header.
You should consider enabling this header to prevent the browser from identifying
content types incorrectly.
?: (security.W007) Your SECURE_BROWSER_XSS_FILTER setting is not set to True,
so your pages will not be served with an 'x-xss-protection: 1; mode=block' header.
You should consider enabling this header to activate the browser\'s XSS filtering
and help prevent XSS attacks.
?: (security.W008) Your SECURE_SSL_REDIRECT setting is not set to True.
Unless your site should be available over both SSL and non-SSL connections,
you may want to either set this setting True or configure a load balancer or
reverse-proxy server to redirect all connections to HTTPS.
?: (security.W012) SESSION_COOKIE_SECURE is not set to True. Using a secure-only
session cookie makes it more difficult for network traffic sniffers to hijack user
sessions.
?: (security.W016) You have 'django.middleware.csrf.CsrfViewMiddleware' in your
MIDDLEWARE, but you have not set CSRF_COOKIE_SECURE to True. Using a secure-only
CSRF cookie makes it more difficult for network traffic sniffers to steal the CSRF
token.
?: (security.W017) You have 'django.middleware.csrf.CsrfViewMiddleware' in your
MIDDLEWARE, but you have not set CSRF_COOKIE_HTTPONLY to True. Using an HttpOnly
CSRF cookie makes it more difficult for cross-site scripting attacks to steal the
CSRF token.
?: (security.W019) You have 'django.middleware.clickjacking.XFrameOptionsMiddleware'
in your MIDDLEWARE, but X_FRAME_OPTIONS is not set to 'DENY'. The default is
'SAMEORIGIN', but unless there is a good reason for your site to serve other parts
of itself in a frame, you should change it to 'DENY'.
```

警告が表示されたので、ドキュメント[^3]を参考にしながらsettings.pyを修正しました。  

### Django設定ファイルの修正
Djangoアプリケーションの設定は`django-admin startproject`で作成したディレクトリ内に`settings.py`というファイルに記載されています。  
ここに設定されている値の初期値は開発向けに設定されているため、本番環境用に設定値に変更していきます。  
ただしDockerコンテナで動作させるため、コンテナ内の環境変数から設定値を取得できるようにし、コンテナ実行時に設定値を注入できるようにしています。

* セキュリティ関連  
	[公式ドキュメント](https://docs.djangoproject.com/en/3.0/topics/security/)を参照しながら設定しています。
	また、`SECRET_KEY`などは環境変数から取得するようにし、コンテナ起動時に指定するようにしています。  
	<script src="https://gist-it.appspot.com/https://github.com/roy-n-roy/DockerHubUpdateNotifier/blob/v1.1.1/django/config/settings.py?slice=23:36&footer=no"></script>

* データベース設定  
	<script src="https://gist-it.appspot.com/https://github.com/roy-n-roy/DockerHubUpdateNotifier/blob/v1.1.1/django/config/settings.py?slice=101:114&footer=no"></script>

* ロケール/多言語対応設定  
	これも[公式ドキュメント](https://docs.djangoproject.com/ja/3.0/topics/i18n/)を参考にして設定します。
	<script src="https://gist-it.appspot.com/https://github.com/roy-n-roy/DockerHubUpdateNotifier/blob/v1.1.1/django/config/settings.py?slice=139:153&footer=no"></script>

* ログ設定  
	ログはコンテナ側で管理するため、ファイルではなく、標準出力に表示するよう設定しました。  
	<script src="https://gist-it.appspot.com/https://github.com/roy-n-roy/DockerHubUpdateNotifier/blob/v1.1.1/django/config/settings.py?slice=194:211&footer=minimal"></script>

その他に、Eメールの送信が必要な場合は、メールバックエンドの設定が必要です。

## uWSGI設定ファイルの作成
Djangoのドキュメントには[uWSGI上で動かす方法](https://docs.djangoproject.com/ja/3.0/howto/deployment/wsgi/uwsgi/)[^4]まで載っているので、これを見ながら設定します。
<script src="https://gist.github.com/roy-n-roy/333106710978f7609b66fd69be3ab8bb.js?file=uwsgi.ini"></script>



## Dockerファイルの作成
アプリケーション側の準備が整ったので、次はDocker側の設定ファイルを書いていきます。

<script src="https://gist.github.com/roy-n-roy/333106710978f7609b66fd69be3ab8bb.js?file=Dockerfile"></script>

ポイントを下記に挙げます。

* 環境変数 `SECRET_KEY` を動的に設定するため、`ENV` コマンドではなく `~/.profile` 読み込み時に生成するようにしています。
	しかし、これはベストプラクティスではなく、本来は `docker secret` などを用いるのが良いのではないかと思います。
* `apk`コマンドに`--no-cache` オプションを付けることで、ローカルキャッシュを使用せず、ダウンロードしたパッケージファイルも実行後に削除してくれます。
* Dockerイメージのビルドでは、各行の実行結果がレイヤとして保存されます。  
	そのため、実行に不要なパッケージをインストールした状態でレイヤを保存させないよう、  
	Pythonパッケージのビルドに必要な `gcc`, `linux-headers`, `musl-dev`, `postgresql-dev`  
	といったパッケージ群は、同一行内で追加・ビルド・削除するようにしています。
* ライブラリパッケージのインストールを先に、アプリケーションのコピーを後に書くことで、アプリのみの更新の場合には以前のレイヤキャッシュを使用できるようにしています。
* `python manage.py migrate`コマンドは、DBへテーブル作成・カラムの変更などを反映するコマンドです。
	そのため、ビルド時ではなくコンテナ起動時に実行します。
* `python manage.py collectstatic`コマンドは、画像などの静的コンテンツファイルを1箇所に集めるコマンドです。
	これも、nginxと共有するボリュームへコピーしたいため、コンテナ起動時に実行しています。


[^1]: [データベース | Django ドキュメント](https://docs.djangoproject.com/ja/3.0/ref/databases/)
[^2]: 各ロゴはこちらで配布されているものを使用しています。[Docker](https://www.docker.com/company/newsroom/media-resources), 
[uWSGI](https://github.com/unbit/uwsgi/blob/master/logo_uWSGI.svg), 
[Django](https://www.djangoproject.com/community/logos/), 
[NGINX](http://nginx.org/), 
[Python](https://www.python.org/community/logos/), 
[PostgreSQL](https://www.postgresql.org/media/img/about/press/slonik_with_black_text_and_tagline.gif)
[^3]: [デプロイチェックリスト | Django ドキュメント](https://docs.djangoproject.com/ja/3.0/howto/deployment/checklist/)
[^4]: [Django を uWSGI とともに使うには？ | Django ドキュメント](https://docs.djangoproject.com/ja/3.0/howto/deployment/wsgi/uwsgi/)