# Djangoコンテナのデータ移行

Dockerをホストしているサーバを移行するため、Djangoアプリケーションのコンテナを別のサーバへ移行しました。
とは言っても、コンテナイメージはDocker Hubにアップロードされているため、DBデータの移行がメインです。  

Djangoには、DBデータのダンプ作成/ロード機能が標準で用意されている[^1]ため、それを利用します。
ダンプ作成時にフォーマットを指定できるのですが、デフォルトのJSONでエクスポートした場合、
タイムスタンプ型のデータが小数点以下3桁で切り捨てられていたため、今回はフォーマットオプションにXMLを指定しています。  

## データバックアップ
ダンプデータを取得します。

!!! note "ダンプデータ取得コマンド"
	```
	docker-compose exec webapp \
		sh -lc "python manage.py dumpdata --format xml 2> /dev/null" > data.xml
	```

この後、新しいサーバへdata.xmlを転送します。

## データリストア
前項で取得したダンプデータを、DBへロードします。  
データロード前にDBマイグレーションとクリアを実行しています。

!!! note "ダンプデータロードコマンド"
	```
	docker-compose run --rm -v $(pwd)/data.xml:/tmp/data.xml:ro webapp \
		sh -lc "python manage.py migrate && \
			python manage.py flush && \
			python manage.py loaddata /tmp/data.xml"
	```

この後、`docker-compose up -d` でアプリを立ち上げて、データが読み込めていたら完了です。  

[^1]: [django-admin と manage.py | Djangoドキュメント](https://docs.djangoproject.com/ja/3.0/ref/django-admin/#dumpdata)
