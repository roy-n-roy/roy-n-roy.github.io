# BuildKitでイメージをビルドする

Dockerでコンテナイメージをビルドするときに、下記のようなことを考えていました。

1. ビルド時間を短くしたい
1. Raspberry Piでも動くコンテナイメージを作りたい

そこでBuildKitを使って、マルチプラットフォーム(multi-platform)のイメージを  
マルチステージ(multi-stage)ビルドをすることにしました。

BuildKitについての説明をスキップしてビルド方法を知りたい場合は、  
[BuildKitとdocker-buildxプラグイン](#buildkitdocker-buildx) の章から読んでください。

## BuildKitとは
[BuildKit][1][^1] とは、コンテナをビルドするためのツールキットであり、  
`buildkitd`というデーモンと`buildctl`コマンドで構成されています。

Dockerの標準のビルドと比べて、BuildKitでビルドした場合には以下のようなメリットがあります。

* マルチステージDockerfileの各ステージを並列ビルドできる
* ビルドキャッシュをDockerHubなどに外部保存/再利用ができる
* マルチプラットフォーム対応のイメージをビルドできる (2020年6月時点ではLinuxのみ)
* Dockerfile内のビルド時に実行するRUNコマンドで、新たな実験的機能を使用できる  
	* SSH接続でリモートのファイルを取得
	* 秘密鍵などのファイルをイメージ内に残さないようにマウント など[^5]

また、BuildKitの一部機能はDocker 18.06以降のDocker Engineに統合されており、  
Docker単体でもBuildKitの一部機能を利用することができます。

<figure style="text-align: center;">
<a href="/imgs/docker_buildkit_buildkit.png" data-lightbox="docker_buildkit"><img src="/imgs/docker_buildkit_buildkit.png" width=80% /></a><br>
<figcaption>図: Docker Engine統合のBuildKitでのビルドと、<br>buildkitd, buildctl を使用したビルド</figcaption>
</figure>

## BuildKitとdocker-buildxプラグイン
BuildKitを使用してビルドをするには、`buildkitd`デーモンを起動して`buildctl`コマンドからビルドを実行できます。  
しかし、既にDockerを使用しているのであれば、[docker-buildx][2][^2] プラグインを利用することで、
下記の様なメリットがあります。

* ビルド時に、自動で `buildkitd`, `buildctl` を含むコンテナを起動
* dockerコマンドと同じようなUIでビルドができる

<figure style="text-align: center;">
<a href="/imgs/docker_buildkit_buildx.png" data-lightbox="docker_buildkit"><img src="/imgs/docker_buildkit_buildx.png" width=80% /></a>  
<figcaption>図: docker-buildxプラグインを使用したビルド</figcaption>
</figure>

### docker-buildxプラグインをインストール
[docker-buildx][2][^2] プラグインを利用するには下記の3点が必要です。

* **Docker CLIの実験的機能の有効化**  
	docker-buildxは2020年6月時点では、まだ実験的機能と位置づけられているため、
	docker CLIの設定で実験的機能を有効化する必要があります。  

* **docker-buildxプラグインのインストール** (Docker for Linuxの場合)  
	Docker for Linuxを使用している場合は、[GitHubのdocker/buildx][2] のリリースページからバイナリをダウンロード、インストールします。  
	Docker Desktopの場合は、あらかじめインストールされています。

* **qemu-user-staticのインストール** (Docker for Linuxの場合)  
	マルチプラットフォームイメージをビルドする場合は、対応するアーキテクチャの実行環境が必要です。  
	今回は qemu-user-static をインストール[^6]し、エミュレーション環境を用意します。  
	こちらもDocker Desktopの場合は、あらかじめインストールされています。

=== "Docker Desktop for Windows/Mac の場合"
	Docker DesktopのSettings画面で画面中央の「CLI Experimental」のトグルスイッチを有効にしてから
	右下の「Apply & Restart」ボタンをクリックして反映します。  
	<p><img src="/imgs/docker_buildkit_enable_cli_experimental_on_desktop.png" /></p>  
	docker-buildx プラグインと qemu-user-static は、Docker Desktopに同梱されているため、インストール不要です。
=== "Docker for Linux の場合"
	!!! tip "実験的機能の有効化とdocker-buildxのインストール"
		``` bash
		# 実験的機能の有効化 (方法1: ~/.docker/config.jsonの編集)
		cp -p ~/.docker/config.json{,.bk} && \
		cat ~/.docker/config.json.bk | docker run -i --rm alpine:latest sh -c \
		"apk add --no-cache jq > /dev/null \
		&& jq '. |= .+{\"experimental\": \"enabled\"}'" > ~/.docker/config.json

		# もしくは、
		# 実験的機能の有効化 (方法2: 環境変数'DOCKER_CLI_EXPERIMENTAL'を設定)
		export DOCKER_CLI_EXPERIMENTAL=enabled

		# docker-buildxのインストール
		mkdir -p  ~/.docker/cli-plugins && \
		docker run --rm alpine:latest sh -c \
		"apk add --no-cache curl jq > /dev/null \
		&& curl -sS https://api.github.com/repos/docker/buildx/releases/latest | \
		    jq -r '.assets[].browser_download_url' | grep linux-amd64 | xargs curl -sSL" \
		            > ~/.docker/cli-plugins/docker-buildx \
		&& chmod a+x ~/.docker/cli-plugins/docker-buildx

		# buildxのバージョン表示確認
		docker buildx version

		# qemu-user-staticのインストール (Ubuntu/Debian の場合)
		sudo apt install qemu-user-static

		# qemu-user-staticのインストール (Fedora の場合)
		sudo dnf install qemu-user-static

		# もしくは、
		# qemu-user-staticのインストール (Dockerイメージを使う場合)
		docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
		```

### ビルダーインスタンスの選択
docker-buildxプラグインでビルドする際には「ビルダーインスタンス」と呼ばれるものを使用します。  

デフォルトではDocker Engine内のBuildKitを使用する'docker'ドライバのビルダーインスタンスを使用する設定になっています。  
フル機能のBuildKitを利用する場合には、'docker-container' ドライバか 'kubernetes' ドライバのビルダーインスタンスを作成して使用します。

!!! info "参考: ビルダーインスタンスのドライバの種類"
	| ドライバ         | ビルド実行方法                                                                    |
	| ---------------- | --------------------------------------------------------------------------------- |
	| docker           | Docker Engineに統合されているBuildKitを使用してでビルド                           |
	| docker-container | `buildkitd`, `buildctl`がインストールされたDockerコンテナを作成/起動してビルド     |
	| kubernetes       | `buildkitd`, `buildctl`がインストールされたKubernetesのポッドを作成/起動してビルド |

!!! tip "Dockerコンテナのビルダーインスタンスでビルド実行"
	``` bash
	# コンテナドライバのビルダーインスタンスを作成、現在のインスタンスを切り替える
	docker buildx create --driver docker-container --name container-builder --use
	# ビルダーインスタンスを確認 (container-builder の右に '*' が付いている)
	docker buildx ls
	  NAME/NODE            DRIVER/ENDPOINT                STATUS   PLATFORMS
	  container-builder *  docker-container
	    container-builder0 npipe:////./pipe/docker_engine inactive
	  default              docker
	    default            default                        running  linux/amd64, linux/arm64, linux/riscv64, linux/ppc64le, linux/s390x, linux/386, linux/arm/v7, linux/arm/v6

	# ビルダーインスタンスのコンテナを停止する
	docker buildx stop
	```

### docker-buildxでビルド
Docker Hubなどのレジストリに/から、ビルドキャッシュをインポート/エクスポートするには、
`--cache-from`, `cache-to`オプションを使用します。

!!! tip "buildxで外部キャッシュ使用してビルドしてpush"
	``` bash
	# レジストリからビルドキャッシュインポートしてビルドし、
	# その後にレジストリへコンテナイメージとビルドキャッシュを別々に保存
	docker buildx build \
	    --cache-from "type=registry,ref=username/repo_name:cache_tag_name" \
	    --cache-to "type=registry,ref=username/repo_name:cache_tag_name" \
	    --push --tag username/repo_name:tag_name .
	```

また、マルチプラットフォームイメージをビルドする場合は、`--platform`オプションを使用します。

!!! tip "buildxでマルチプラットフォームイメージをビルドしてpush"
	``` bash
	# x86,x64,armv6,armv7,aarch64で利用できるイメージをビルドしてpush
	docker buildx build \
	    --platform linux/386,linux/amd64,linux/arm/v6,linux/arm/v7,linux/arm64/v8 \
	    --push --tag username/repo_name:tag_name .
	```

!!! info "参考: キャッシュタイプの一覧 (2020年6月時点)"
	| キャッシュタイプ | 説明                                                                              |
	| ---------------- | --------------------------------------------------------------------------------- |
	| inlineタイプ     | コンテナイメージにビルドキャッシュを埋め込んで、イメージと一緒にDockerHubなどのレジストリに保存します。 |
	| registryタイプ   | コンテナイメージとビルドキャッシュを別々にして、DockerHubなどのレジストリに保存します。<br>イメージとキャッシュ保存先でリポジトリ名:タグ名が、同じ場合/異なる場合のどちらでもエクスポート/インポートが可能です。 |
	| localタイプ      | ビルドを実行するローカルホスト上のファイルシステムにビルドキャッシュを保存します。<br>CIツールを使用してビルドキャッシュを保存する場合などに便利です。 |

	最新の情報については、[docker/buildxのドキュメンテーション](https://github.com/docker/buildx#documentation) を参照して下さい。  

!!! info "参考: プラットフォームの一覧 (2020年6月時点)"
	| プラットフォーム名 |                                                            |
	| ------------------ | ---------------------------------------------------------- |
	| linux/386          | Linux / Intel x86(32bit) アーキテクチャ                    |
	| linux/amd64        | Linux / Intel x86_64(64bit) アーキテクチャ                 |
	| linux/arm/v6       | Linux / ARM v6(32bit) アーキテクチャ                       |
	| linux/arm/v7       | Linux / ARM v6(32bit) アーキテクチャ                       |
	| linux/arm64/v8     | Linux / ARM v8(64bit) アーキテクチャ                       |
	| linux/mips64le     | Linux / MIPS64 Little Endian(64bit) アーキテクチャ         |
	| linux/ppc64le      | Linux / 64-bit PowerPC Little Endian(64bit) アーキテクチャ |
	| linux/s390x        | Linux / IBM S/390(64bit) アーキテクチャ                    |
	| windows/amd64      | Microsoft Windows / Intel x86_64(64bit) アーキテクチャ     |

## その他のBuildKitの利用方法
以降の章ではdocker-buildxプラグインを利用しないBuildKitでのビルド方法を説明します。  

### Dockerを使用せず、buildkitdとbuildctlでビルドする
Dockerを使用せずにビルドするには、BuildKitのインストールが必要です。
以下の手順でインストールし、デーモンを起動します。

!!! tip "BuildKitをインストールし、buildkitdデーモンを起動"
	``` bash
	# BuildKitをインストール
	docker run --rm alpine:latest sh -c \
	"apk add --no-cache curl jq > /dev/null \
	&& curl -sS https://api.github.com/repos/moby/buildkit/releases | \
	    jq -r '.[].assets[].browser_download_url' | \
	    grep linux-amd64 | head -n 1 | xargs curl -sSL" | \
	sudo tar zxf - -C /usr/local/

	# buildkitdデーモンを起動
	sudo buildkitd
	```

!!! tip "buildctlコマンドでビルド"
	``` bash
	# buildctlコマンドでビルド実行
	sudo buildctl build --frontend=dockerfile.v0 --local context=. --local dockerfile=.
	```

### Docker EngineのBuildKitでビルド
BuildKitやdocker-buildxプラグインをインストールせず、
Docker 18.06以降のDocker Engineに統合されているBuildKitでビルドします。

!!! tip "BuildKitの有効化"
	``` bash
	# Docker統合のBuildKit有効化 (方法1: 設定ファイルに追記し、Docker Engineを再起動)
	(test -f /etc/docker/daemon.json && cat /etc/docker/daemon.json || echo "{}") | \
	    jq '. |= .+{"features": {"buildkit": true}}' | sudo tee /etc/docker/daemon.json

	sudo systemctl restart docker.servie

	# または、
	# Docker統合のBuildKit有効化 (方法2: 環境変数'DOCKER_BUILDKIT'を設定)
	export DOCKER_BUILDKIT=1

	# ビルド実行
	docker build .
	```

	1つめの方法では、`/etc`配下の設定ファイルの編集とデーモンの再起動を行うため、root権限が必要になります。  
	root権限が取得できない場合や、一時的にBuildKitを利用する場合は、環境変数での設定を試してください。

#### Docker EngineのBuildKitで利用できる機能
2020年6月時点で、Docker 18.06以降のDocker Engineに統合されているBuildKitでは  
利用できない機能がいくつかあります。

それぞれで利用できる機能の差については、下記の表を参照してください。

| 機能 | Docker Engine<br>統合版 | `buildkitd`<br>デーモン版 | 説明 |
| --------------- | :---------------------: | :---------------------: | ---- |
| マルチステージビルドの並列実行                       | ✅ | ✅ | マルチステージDockerfileの各ステージのビルドを可能な限り並列で実行します。 |
| マルチプラットフォーム対応のイメージビルド           | -- | ✅ | Intel(一般的なPC/サーバ)やArm(Raspberry Piなど)の複数のアーキテクチャで利用できるDockerイメージをビルドします。 |
| ビルドキャッシュの出力<br>&emsp;&emsp;inlineタイプ   | ✅ | ✅ | ビルドキャッシュをイメージに埋め込み、DockerHubなどのレジストリに保存します。<br>マルチステージビルドの場合は、最終的にコマンドが実行されるステージのキャッシュのみが保存されます。 |
| &emsp;&emsp;registryタイプ                           | -- | ✅ | ビルドキャッシュとイメージを分けて、DockerHubなどのレジストリに保存します。<br>マルチステージビルドの場合、全てのステージのキャッシュを保存できます。 |
| &emsp;&emsp;localタイプ                              | -- | ✅ | OCIイメージフォーマットに準拠した形式で、ローカルディレクトリにビルドキャッシュを保存します。<br>マルチステージビルドの場合、全てのステージのキャッシュを保存できます。 |
| ビルドキャッシュの使用<br>&emsp;&emsp;registryタイプ | ✅ | ✅ | DockerHubなどのレジストリから、inline形式/egistry形式のビルドキャッシュを取得します。 |
| &emsp;&emsp;localタイプ                              | -- | ✅ | ローカルディレクトリから、local形式のビルドキャッシュを取得します。 |
| Composeファイルでのビルド                            | -- | ✅ | docker-compose.ymlファイルからDockerfileやビルドコンテキストを読み取ってビルドします。 |
| Dockerfileの実験的機能の使用                         | ✅ | ✅ | ビルドステップ単位で、パッケージマネージャのキャッシュ(--mount&nbsp;tyle=cache)や認証情報(--mount&nbsp;type=secret)をマウントしたり、ネットワークの制御(--network=none\|host\|default)などができます。<br>詳細は [GitHub上のドキュメント][5] を参照してください。 |

[^1]: [moby/buildkit: concurrent, cache-efficient, and Dockerfile-agnostic builder toolkit][1]
[^2]: [docker/buildx: Docker CLI plugin for extended build capabilities with BuildKit · GitHub][2]
[^3]: [Docker Buildx | Docker Documentation][3]
[^4]: Docker Blogでのマルチプラットフォームビルドの解説 [Multi-arch build and images, the simple way - Docker Blog][4]
[^5]: Dockerfileの実験的機能については [Dockerfile frontend experimental syntaxes - buildkit/experimental.md GitHub][5] を参照。
[^6]: 各ディストリビューションに応じたパッケージマネージャ、または [multiarch/qemu-user-static - Docker Hub][6] のDockerイメージを使用してインストールしてください。

[1]: https://github.com/moby/buildkit
[2]: https://github.com/docker/buildx
[3]: https://docs.docker.com/buildx/working-with-buildx/
[4]: https://www.docker.com/blog/multi-arch-build-and-images-the-simple-way/
[5]: https://github.com/moby/buildkit/blob/master/frontend/dockerfile/docs/experimental.md
[6]: https://hub.docker.com/r/multiarch/qemu-user-static/
