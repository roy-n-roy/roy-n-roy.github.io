
# BuildKitでイメージをビルドする

## BuildKitとは
下記引用。  

> BuildKit とはビルドツールキットです。
> ソースコードを変換して効率的で表現力豊かで再現可能な方法で成果物を構築することが出来ます。
> 
> 以下の特徴があります。[(参考)][1]
> 
> * 自動ガベージコレクション
>    * フロントエンドフォーマットの拡張
>    * 並列的な依存関係の解決
>    * 効率的な命令キャッシュ
>    * ビルドキャッシュのインポート/エクスポート
>    * ネストされたビルドジョブの呼び出し
>    * 分散ワーカー
>    * 複数のアウトプットフォーマット
>    * プラガブルなアーキテクチャ
>    * 管理者権限が不要な実行
> 
> BuildKit は moby プロジェクトが作成したビルドツールキットであり、Docker とは独立しているプロジェクトで開発されたものです。
> 
> Docker や Docker Compose で正式に利用できるようになりつつあるため、しばしば Docker の新しいビルド機能として紹介されています。
> 
> 引用: <cite>[BuildKitによりDockerとDocker Composeで外部キャッシュを使った効率的なビルドをする方法 - Qiita][2]</cite>

## BuildKitの実装

2020年6月時点では、BuildKitの実装は下記の2種類が存在します。

1. Docker 18.06以降のDocker Engineに統合されているBuildKit
1. buildkitdというデーモンとして実装されているBuildKit


2.のデーモン版では 1.のEngine統合版に対して、新たな機能が追加されています。
また、Dockerとは完全に分離されており、BuildKit単体でもイメージをビルドが可能になっています。

dockerコマンドから 2.のBuildKitでフル機能を利用するには、[docker-buildx][3]というプラグインを利用します。

それぞれで、利用できる機能については下記の表を参照してください。

### 利用できる機能の比較

| 機能 | Docker Engine<br>統合版 | buildkitd<br>デーモン版 | 説明 |
| --------------- | :---------------------: | :---------------------: | ---- |
| マルチステージビルドの並列実行                     | ✅ | ✅ | マルチステージDockerfileの各ステージのビルドを可能な限り並列で実行します。 |
| マルチプラットフォーム対応のイメージビルド         | -- | ✅ | Intel(一般的なPC/サーバ)やArm(Raspberry Piなど)の複数のアーキテクチャで利用できるDockerイメージをビルドします。 |
| Composeファイルでのビルド                          | -- | ✅ | docker-compose.ymlファイルからDockerfileやビルドコンテキストを読み取ってビルドします。 |
| ビルドキャッシュの出力<br>&emsp;&emsp;inline形式   | ✅ | ✅ | ビルドキャッシュをイメージに埋め込み、DockerHubなどのレジストリに保存します。<br>マルチステージビルドの場合は、最終的にコマンドが実行されるステージのキャッシュのみが保存されます。 |
| &emsp;&emsp;registry形式                           | -- | ✅ | ビルドキャッシュとイメージを分けて、DockerHubなどのレジストリに保存します。<br>マルチステージビルドの場合、全てのステージのキャッシュを保存できます。 |
| &emsp;&emsp;local形式                              | -- | ✅ | OCIイメージフォーマットに準拠した形式で、ローカルディレクトリにビルドキャッシュを保存します。<br>マルチステージビルドの場合、全てのステージのキャッシュを保存できます。 |
| ビルドキャッシュの使用<br>&emsp;&emsp;registry形式 | ✅ | ✅ | DockerHubなどのレジストリから、inline形式/egistry形式のビルドキャッシュを取得します。 |
| &emsp;&emsp;local形式                              | -- | ✅ | ローカルディレクトリから、local形式のビルドキャッシュを取得します。 |
| Dockerfileの実験的機能の使用                       | ✅ | ✅ | ビルドステップ単位で、パッケージマネージャのキャッシュ(--mount&nbsp;tyle=cache)や認証情報(--mount&nbsp;type=secret)をマウントしたり、ネットワークを制御(--network=none\|host\|default)するなどができます。<br>詳細は [GitHub上のドキュメント][6] を参照してください。 |

## Docker EngineのBuildKitを利用する

Docker 18.06以降のDocker Engineに統合されているBuildKitを利用するには、2つの方法があります。

0. Docker Engineの設定を変更して利用する方法  
    この方法では、docker build実行時にデフォルトでBuildKitを使用するように、Dockerデーモンの設定ファイルを変更します。  

    ??? tip "設定方法"
        `/etc/docker/daemon.json`ファイルに下記を追加してからDocker Engineを再起動します。
        ``` json
        {
        "features": {
                "buildkit": true
            }
        }
        ```

        bashの場合

        ``` bash
        # /etc/docker/daemon.jsonファイルに設定追加
        (test -f /etc/docker/daemon.json && cat /etc/docker/daemon.json || echo "{}") | \
            jq '. |= .+{"features": {"buildkit": true}}' | sudo tee /etc/docker/daemon.json
        # Docker Engineを再起動
        sudo systemctl restart docker.servie

        # Dockerイメージをビルド
        docker build .
        ```
    設定変更とデーモンの再起動をするため、root権限が必要になります。  
    root権限が取得できない場合や、一時的にBuildKitを利用する場合は、2. の方法を試してください。

0. 環境変数を設定して利用する方法  
    環境変数 `DOCKER_BUILDKIT` を設定すると`docker build`コマンド実行時にBuildKitでビルドされるようになります。

    ??? tip "環境変数の設定"
        環境変数で`DOCKER_BUILDKIT=1`を設定します。  
        bashの場合
        ``` bash
        export DOCKER_BUILDKIT=1
        docker build -t .
        # または
        DOCKER_BUILDKIT=1 docker build .
        ```
    環境変数の追加だけのため、root権限が不要です。  
    他のユーザーでも必ずBuildKitを使ってでビルドさせたい場合は、1.の方法で設定すると良いでしょう。

## フル機能のBuildKitを利用する

0. buildkitdを起動して、buildctlコマンドから利用する方法

    ??? tip "buildctlコマンドから利用"
        ```
            # buildkitをインストール
            curl -sSL https://github.com/moby/buildkit/releases/download/v0.7.1/buildkit-v0.7.1.linux-arm-v7.tar.gz | sudo tar zxf - -C /usr/local/
            # buildkitdデーモンを起動
            sudo buildkitd
            # buildctlコマンドでビルド実行
            sudo buildctl build --frontend=dockerfile.v0 --local context=. --local dockerfile=.
        ```

0. docker-buildxプラグインで、docker-containerドライバを通して利用する方法

    docker-buildxは2020年6月現在では、まだ実験的機能と位置づけられています。  
    そのためbuildxを利用するには、まずdocker CLIの設定で実験的機能を有効化した上で、
    docker-buildxプラグインをインストールする必要があります。  

    ??? tip "docker-buildxを通してBuildKitを利用"
        ``` bash
            # 実験的機能の有効化
            cp -p ~/.docker/config.json{,.bk} && jq '. |= .+{"experimental": "enabled"}' < ~/.docker/config.json.bk > ~/.docker/config.json
            # docker-buildxのインストール
            mkdir -p ~/.docker/cli-plugins
            curl -sSLo ~/.docker/cli-plugins/docker-buildx https://github.com/docker/buildx/releases/download/v0.4.1/buildx-v0.4.1.linux-amd64
            chmod +x ~/.docker/cli-plugins/docker-buildx
            # buildxのバージョン表示確認
            docker buildx version
        ```
    

    また、docker-buildxプラグインには、ビルダーインスタンスと呼ばれる構成要素があり、このインスタンスを使用してビルドを実行します。  
    デフォルトでは、Docker Engine統合のBuildKitを使用する"docker"ドライバのビルダーインスタンスを使用するにようなっているため、
    コンテナー内でbuildkitdデーモンを起動して、そこでビルドを実行する"docker-container"ドライバのビルダーインスタンスを作成し、ビルダーインスタンスを切り替えます。  

    ```
        # コンテナドライバのビルダーインスタンスを作成、現在のインスタンスを切り替える
        docker buildx create --name container-builder --driver docker-container --use
        docker buildx build .
        docker buildx stop
    ```

#### 実験的機能の有効化
* Docker for Linux の場合  
    ~/.docker/config.json ファイルで設定します。

    !!! info "~/.docker/config.json"
        ``` json
        {
            "experimental": "enabled"
        }
        ```

* Docker Desktop for Windows/Mac の場合  
    Docker DesktopのSettings画面を開き、**>_ Command Line** の中にある  
    トグルスイッチ **Enable experimental features** を有効にします。

#### docker-buildxプラグインのインストール
Docker Desktop for Windows/Macを利用している場合は、あらかじめbuildxプラグインがDocker Desktopに含まれているため、インストールは不要です。  
Docker for Linuxの場合は、[GitHubのdocker/buildx][3] リポジトリのリリースページからバイナリをダウンロードして、
`~/.docker/cli-plugins/docker-buildx`へリネーム/保存します。  
CLIでは、下記のコマンドを実行します。

!!! info "docker-buildxプラグインのインストール"
    ``` bash
    mkdir -p  ~/.docker/cli-plugins && \
    docker run --rm alpine:latest sh -c \
    "apk add --no-cache curl jq > /dev/null \
    && curl -sS https://api.github.com/repos/docker/buildx/releases/latest | \
        jq -r '.assets[].browser_download_url' | grep linux-amd64 | xargs curl -sSL" \
                > ~/.docker/cli-plugins/docker-buildx \
    && chmod a+x ~/.docker/cli-plugins/docker-buildx
    ```

## ビルドキャッシュの種類

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
