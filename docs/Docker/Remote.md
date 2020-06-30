# リモートホストのDockerに接続する

非力なPCで「Dockerが使いたい」と思ったとき、強力なリモートマシン上のDockerエンジンへ接続し、利用することができます。  

## Dockerのコンテキスト
Docker 19.03から「コンテキスト」という概念が追加されました。  
ここでのコンテキストは、いわゆるビルドコンテキストではなく、Docker Engineのエンドポイントを指します。  

デフォルトの「コンテキスト」は、環境変数 `DOCKER_HOST` の値を使用するように設定されています。

!!! info "デフォルトのコンテキストを確認"
	``` bash
	# Windowsの場合
	> docker context ls
	NAME                DESCRIPTION                               DOCKER ENDPOINT                  KUBERNETES ENDPOINT   ORCHESTRATOR
	default *           Current DOCKER_HOST based configuration   npipe:////./pipe/docker_engine                         swarm
	
	# Linuxの場合
	> docker context ls
	NAME                DESCRIPTION                               DOCKER ENDPOINT               KUBERNETES ENDPOINT   ORCHESTRATOR
	default *           Current DOCKER_HOST based configuration   unix:///var/run/docker.sock                         swarm
	```

環境変数 `DOCKER_HOST` が設定されていない場合は、Docker Desktop for Windowsでは名前付きパイプ、
LinuxではUnixドメインソケットへのURLが初期値として使用されます。  

## リモートのDockerを使用

リモートホストのDocker Engineへ接続するには、SSH接続やTCP接続(HTTP Restful API)を経由して、Docker Engine APIを使用します。

TCP接続では、認証を通さない接続を利用することもできますが、
誰もがroot権限で動作するDockerに接続出来てしまうことになり、セキュリティの観点から好ましくありません。

そのため、公開鍵/秘密鍵を使用した認証でのSSH接続かTCP接続を使用することになりますが、
ここでは設定の容易さから、SSH接続を採用します。

## SSH接続のセットアップ
SSH

* OpenSSHサーバのインストール/デーモン起動
* 公開鍵/秘密鍵のセットアップ
* ユーザをdockerグループに追加
* SSH接続を使用したリモートのコンテキストを追加

Docker Desktopが動作するWindows 10でも、OS標準オプションであるOpenSSHサーバをインストールすることで、
SSH経由でのDockerエンジンへの接続を利用することが出来ます。

