# DjangoアプリをDockerで運用する
Djangoとは、Pythonで利用できるWebアプリケーションフレームワークです。  
この記事では、Djangoを使って開発したアプリケーションをDocker環境へデプロイした際の手順を記載します。  

## 準備
### ベースイメージの選定
オリジナルのアプリケーションをDocker上で動作させるため、Dockerイメージを自前でビルドします。
今回はPythonでDjangoアプリケーションを動かすので、`python:3.8-alpine`を選択しました。[^1]  

### コンテナ設計
<figure style="text-align: center;">
<a href="/imgs/docker_django_arch.png" data-lightbox="docker_django_arch"><img style="float: left;" src="/imgs/docker_django_arch.png" width=100% /></a>  
<figcaption>図 1. コンテナ構成図[^2]</figcaption>
</figure>

上記図のような感じにしたいと思います。

* アプリサーバ
	* Djangoアプリは、Webアプリと定期バッチアプリがあります。  
		これらは同じイメージを使用するが、コンテナは別々に2つ起動します。
	* nginxとWebアプリの接続には、uWSGIを使用します。
* httpサーバ
	* 外部に公開するネットワークポートはnginxのHTTP(80)/HTTPS(443)のみとします。
	* nginxでHTTP over SSL/TLS(HTTPS)に対応させます。  
		証明書はLet's Encryptで取得します。
	* 画像などの静的コンテンツは共有Volumeに置き、Webアプリを介さずにnginxから直接配信します。
	* コンテナイメージは [steveltn/https-portal](https://hub.docker.com/r/steveltn/https-portal) を使用します。
* データベースサーバ
	* Djangoアプリケーションではデータを保存するためにRDBを使用するため、今回はPostgreSQLを選択しています。
	* コンテナイメージは [PostgreSQLのDocker公式イメージ](https://hub.docker.com/_/postgres) を使用します。

* 各コンテナ間の通信には、Docker内部ネットワークを使用します。

## 前提
以降の作業では、下記を前提として書かれています。

* Djangoアプリケーションを開発し、開発環境で動作している。
* Dockerがインストールされた環境が存在している。

## Djangoアプリケーションの設定
### Djangoのデプロイ時チェック
Djangoには管理コマンドに、デプロイ時のチェックをする機能が備わっています。  
実行すると、デプロイする場合の設定エラーや警告が表示されます。

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

なんだか、たくさん警告が表示されたので、[ドキュメント](https://docs.djangoproject.com/ja/3.0/howto/deployment/checklist/)[^3]を参考にしながらsettings.pyを修正しました。  

### settings.pyファイルの修正
Djangoアプリケーションの設定は`django-admin startproject`で作成したディレクトリ内に`settings.py`というファイルに記載されています。  
ここに設定されている値の初期値は開発向けに設定されているため、本番環境用に設定値に変更していきます。  

ただし、Dockerコンテナで動作させるため、コンテナ内の環境変数から設定値を取得できるようにし、コンテナ実行時に設定値を注入できるようにしています。
また、ログはコンテナ側で管理するため、ファイル出力ではなく標準出力に表示するように設定しています。  

設定にあたっては、Django公式ドキュメントを参考にしました。[^4][^5][^6][^7][^8][^9]

??? info "settings.py を表示"
	<script src="https://gist.github.com/roy-n-roy/333106710978f7609b66fd69be3ab8bb.js?file=settings.py"></script>


## Dockerファイルの作成
次は、アプリケーションのDockerイメージをビルドするため、Dockerfileを作ります。

<script src="https://gist.github.com/roy-n-roy/333106710978f7609b66fd69be3ab8bb.js?file=Dockerfile"></script>

ポイントを下記に挙げます。

* `apk`コマンドに`--no-cache` オプションを付けることで、ローカルキャッシュを使用せず、ダウンロードしたパッケージファイルも実行後に削除されます。
* Dockerイメージのビルドでは、各行の実行結果がレイヤとして保存されるため、ビルドのみに必要な
	`gcc`, `linux-headers`, `musl-dev`, `postgresql-dev` といったパッケージ群は、同一行内で追加・ビルド・削除することで、
	アプリ実行に不要なパッケージをインストールした状態でレイヤを保存させないようにしています。
* ライブラリパッケージのインストールを先に、アプリケーションのコピーを後に書くことで、アプリのみの更新の場合には以前のレイヤキャッシュを使用できるようにしています。
* uWSGIの起動の前に以下のコマンドを実行しています。
	* `python manage.py migrate`:  
		DBへテーブル作成・カラムの変更などを反映するコマンドです。
		DBインスタンスが起動しているタイミングで実行する必要があります。
	* `python manage.py collectstatic`:  
		画像などの静的コンテンツファイルを1箇所に集めるコマンドです。
		nginxと共有するボリュームへコピーしたいため、コンテナ起動時に実行しています。
* 環境変数 `SECRET_KEY` を動的に設定するために、 `~/.profile` 読み込み時に生成するようにしています。
	しかし、これはベストプラクティスではなく、本来は `.env`ファイルや `docker secret` などを用いるのが良いのではないかと思います。

## uWSGI設定ファイルの作成
Djangoのドキュメントには[uWSGI上で動かす方法](https://docs.djangoproject.com/ja/3.0/howto/deployment/wsgi/uwsgi/)[^10]も載っているので、これを見ながら設定します。
<script src="https://gist.github.com/roy-n-roy/333106710978f7609b66fd69be3ab8bb.js?file=uwsgi.ini"></script>


## Nginxの設定
httpサーバのNginxのイメージは、前述の通り [steveltn/https-portal](https://hub.docker.com/r/steveltn/https-portal) を使用します。  
このイメージは、自動でLet's Encryptの証明書取得・更新してくれるため、証明書の期限切れを気にする必要がない上、cronなどの追加設定が不要なものです。  
Nginxの設定ファイルはeRubyファイルになっており、`/var/lib/nginx-conf/[ドメイン名].ssl.conf.erb`というファイルを配置すると、対応したドメイン名でのアクセスに適用されます。

設定ファイルはuWSGIのドキュメント[^11]を見つつ、作成しました。

??? info "nginx_uwsgi.ssl.conf.erb を表示"
	<script src="https://gist.github.com/roy-n-roy/333106710978f7609b66fd69be3ab8bb.js?file=nginx_uwsgi.ssl.conf.erb"></script>

## docker-compose.ymlファイル
最後に、前述のコンテナを起動するためのdocker-composeファイルです。

??? info "docker-compose.yml を表示"
	<script src="https://gist.github.com/roy-n-roy/333106710978f7609b66fd69be3ab8bb.js?file=docker-compose.yml"></script>


## 最後に
### この他にやるべきこと

* (言及すべくもないが、)gitなどでソース管理をする。
* DBの定期バックアップ
	* こういうもの [Django Database Backup -- django-dbbackup 3.0.2 documentation](https://django-dbbackup.readthedocs.io/en/stable/index.html) もある。
* ユーザーアップロードコンテンツがあるアプリの場合は、それも定期バックアップが必要。
* きちんと製品として運用するのであれば、[k8s](https://kubernetes.io/ja/)などに載せる。

### 感想
アプリケーションを作り始めるところからデプロイまで、Djangoの公式ドキュメントが充実しており、いたせり尽くせりといった感じでした。  

ドキュメントの日本語翻訳もしっかりされていること、作り始める時の手軽さ、Pythonのエコシステムが活かせることもあり、初心者にもオススメできるものだと思います。  


[^1]: Dockerオフィシャルイメージに`django`というものも存在するのですが、2020年2月時点で3年以上メンテナンスされておらず、Djangoのバージョンも古いため採用は見送りました。
[^2]: 各ロゴはこれらのWebサイトで配布されているものを使用しています。[Docker](https://www.docker.com/company/newsroom/media-resources), 
[uWSGI](https://github.com/unbit/uwsgi/blob/master/logo_uWSGI.svg), 
[Django](https://www.djangoproject.com/community/logos/), 
[NGINX](http://nginx.org/), 
[Python](https://www.python.org/community/logos/), 
[PostgreSQL](https://www.postgresql.org/media/img/about/press/slonik_with_black_text_and_tagline.gif)
[^3]: [デプロイチェックリスト | Django ドキュメント](https://docs.djangoproject.com/ja/3.0/howto/deployment/checklist/)
[^4]: [Django におけるセキュリティ | Django ドキュメント](https://docs.djangoproject.com/ja/3.0/topics/security/)
[^5]: [データベース | Django ドキュメント](https://docs.djangoproject.com/ja/3.0/ref/databases/)
[^6]: [国際化とローカル化 | Django ドキュメント](https://docs.djangoproject.com/ja/3.0/topics/i18n/)
[^7]: [静的ファイル (画像、JavaScript、CSS など) を管理する | Django ドキュメント](https://docs.djangoproject.com/ja/3.0/howto/static-files/)
[^8]: [メールを送信する | Django ドキュメント](https://docs.djangoproject.com/ja/3.0/topics/email/)
[^9]: [ロギング | Django ドキュメント](https://docs.djangoproject.com/ja/3.0/topics/logging/)
[^10]: [Django を uWSGI とともに使うには？ | Django ドキュメント](https://docs.djangoproject.com/ja/3.0/howto/deployment/wsgi/uwsgi/)
[^11]: [Setting up Django and your web server with uWSGI and nginx -- uWSGI 2.0 documentation](https://uwsgi-docs.readthedocs.io/en/latest/tutorials/Django_and_nginx.html)