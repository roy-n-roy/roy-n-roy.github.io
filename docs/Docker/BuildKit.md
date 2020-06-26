
# BuildKitでイメージをビルドする

Dockerでコンテナイメージをビルドするときに、下記のようなことを考えていました。

* コンテナイメージのサイズを小さくしたい
* ビルド時間を短くしたい
* Raspberry Piでも動くコンテナイメージを作りたい

## 結論
* [Best practices for writing Dockerfiles | Docker Documentation][7]を読みましょう
* BuildKitでビルドしてみましょう

[7]: https://docs.docker.com/develop/develop-images/dockerfile_best-practices/

説明をスキップしてビルド方法が知りたい場合は、[フル機能のBuildKitでビルド](#buildkit_2) から読んでください。

### コンテナイメージのサイズを小さくするには
* AlpineLinuxのイメージをベースに選択する
* マルチステージビルドを採用し、ビルド成果物だけを実行イメージに配置する
* パッケージマネージャのキャッシュをレイヤーに残さない

### ビルド時間を短くするには
* マルチステージビルドを採用し、BuildKitで各ステージを並列ビルドする
* ビルドキャッシュを最大限利用する

### Raspberry Piでも動くコンテナイメージを作るには
* BuildKitを使用して、マルチアーキテクチャ対応のコンテナイメージをビルドする

## BuildKitとは
BuildKitとは、コンテナをビルドするためのツールキットであり、
`buildkitd`というデーモンと`buildctl`というCLIツールで構成されています。

また、BuildKitの機能の一部はDocker 18.06以降のDocker Engineに統合されており、
Docker単体でもBuildKitの一部機能を利用することができます。

Docker Engine統合版と`buildkitd`での利用可能な機能については[利用できる機能の比較][#_3]を参照してください。

### 利用できる機能の比較

| 機能 | Docker Engine<br>統合版 | `buildkitd`<br>デーモン版 | 説明 |
| --------------- | :---------------------: | :---------------------: | ---- |
| マルチステージビルドの並列実行                     | ✅ | ✅ | マルチステージDockerfileの各ステージのビルドを可能な限り並列で実行します。 |
| マルチプラットフォーム対応のイメージビルド         | -- | ✅ | Intel(一般的なPC/サーバ)やArm(Raspberry Piなど)の複数のアーキテクチャで利用できるDockerイメージをビルドします。 |
| Composeファイルでのビルド                          | -- | ✅ | docker-compose.ymlファイルからDockerfileやビルドコンテキストを読み取ってビルドします。 |
| ビルドキャッシュの出力<br>&emsp;&emsp;inline形式   | ✅ | ✅ | ビルドキャッシュをイメージに埋め込み、DockerHubなどのレジストリに保存します。<br>マルチステージビルドの場合は、最終的にコマンドが実行されるステージのキャッシュのみが保存されます。 |
| &emsp;&emsp;registry形式                           | -- | ✅ | ビルドキャッシュとイメージを分けて、DockerHubなどのレジストリに保存します。<br>マルチステージビルドの場合、全てのステージのキャッシュを保存できます。 |
| &emsp;&emsp;local形式                              | -- | ✅ | OCIイメージフォーマットに準拠した形式で、ローカルディレクトリにビルドキャッシュを保存します。<br>マルチステージビルドの場合、全てのステージのキャッシュを保存できます。 |
| ビルドキャッシュの使用<br>&emsp;&emsp;registry形式 | ✅ | ✅ | DockerHubなどのレジストリから、inline形式/egistry形式のビルドキャッシュを取得します。 |
| &emsp;&emsp;local形式                              | -- | ✅ | ローカルディレクトリから、local形式のビルドキャッシュを取得します。 |
| Dockerfileの実験的機能の使用                       | ✅ | ✅ | ビルドステップ単位で、パッケージマネージャのキャッシュ(--mount&nbsp;tyle=cache)や認証情報(--mount&nbsp;type=secret)をマウントしたり、ネットワークの制御(--network=none\|host\|default)などができます。<br>詳細は [GitHub上のドキュメント][6] を参照してください。 |

## フル機能のBuildKitでビルド
フル機能のBuildKitを使用してビルドをするには、`buildkitd`デーモンを起動して`buildctl`コマンドから実行できますが、
すでにDockerを使用している場合は、docker-buildxプラグインを利用すると便利です。

### docker-buildxプラグインでビルド

[docker-buildx][3]プラグインを利用するには下記の2点が必要です。

* **Docker CLIの実験的機能の有効化**  
    docker-buildxは2020年6月現在では、まだ実験的機能と位置づけられているため、
    docker CLIの設定で実験的機能を有効化する必要があります。  

* **docker-buildxプラグインのインストール** (Docker for Linuxの場合)  
    Docker for Linuxを使用している場合は、[GitHubのdocker/buildx][3] リポジトリのリリースページからバイナリをダウンロード/インストールします。  

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
        ```
=== "Docker Desktop for Windows/Mac の場合"
    Docker DesktopのSettings画面で画面中央の「CLI Experimental」のトグルスイッチを有効にしてから
    右下の「Apply & Restart」ボタンをクリックして反映します。

    <img src="/imgs/docker_buildkit_enable_cli_experimental_on_desktop.png" />
    docker-buildxは、Docker Desktopに含まれているため、インストール不要です。

また、docker-buildxプラグインには、ビルダーインスタンスと呼ばれる要素があります。
フル機能のBuildKitを利用するには、'docker-container'ドライバのビルダーインスタンスを使用してビルドを実行します。

!!! info "参考: ビルダーインスタンスのドライバの種類"
    | ドライバ         | ビルド実行方法                                                                    |
    | ---------------- | --------------------------------------------------------------------------------- |
    | docker           | Docker Engineに統合されているBuildKitを使用してでビルド                           |
    | docker-container | `buildkitd`,`buildctl`がインストールされたDockerコンテナを作成/起動してビルド     |
    | kubernetes       | `buildkitd`,`buildctl`がインストールされたKubernetesのポッドを作成/起動してビルド |

!!! tip "Dockerコンテナのビルダーインスタンスでビルド実行"
    ``` bash
    # コンテナドライバのビルダーインスタンスを作成、現在のインスタンスを切り替える
    docker buildx create --driver docker-container --name container-builder --use
    docker buildx build .

    # ビルダーインスタンスのコンテナを停止する
    docker buildx stop
    ```

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

## Docker EngineのBuildKitでビルド
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

## 参考文献
[moby/buildkit: concurrent, cache-efficient, and Dockerfile-agnostic builder toolkit · GitHub][1]  
[BuildKitによりDockerとDocker Composeで外部キャッシュを使った効率的なビルドをする方法 - Qiita][2]  
[docker/buildx: Docker CLI plugin for extended build capabilities with BuildKit · GitHub][3]  
[Docker Buildx | Docker Documentation][4]  
[Docker Buildx · Actions · GitHub Marketplace][5]  

[1]: https://github.com/moby/buildkit
[2]: https://qiita.com/tatsurou313/items/ad86da1bb9e8e570b6fa
[3]: https://github.com/docker/buildx
[4]: https://docs.docker.com/buildx/working-with-buildx/
[5]: https://github.com/marketplace/actions/docker-buildx
[6]: https://github.com/moby/buildkit/blob/master/frontend/dockerfile/docs/experimental.md
