
# Docker BuildKit

## BuildKitとは
下記引用。  

> BuildKit とはビルドツールキットです。
> ソースコードを変換して効率的で表現力豊かで再現可能な方法で成果物を構築することが出来ます。
> 
> 以下の特徴があります。[(参考)][1][^1]
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
> <cite>[BuildKitによりDockerとDocker Composeで外部キャッシュを使った効率的なビルドをする方法 - Qiita][2][^2]</cite>

## BuildKitの利用方法

BuildKitを利用するには、下記の2種類の方法があります。

0. docker単体(プラグイン追加なし)で利用する方法
0. docker-buildxプラグインを追加インストールして利用する方法

ただし、1.のdocker単体で利用する方法では、一部機能に制限があります。

## 利用できる機能の比較

| 機能         | docker単体   | buildxプラグイン |   |
| ------------ | ------------ | ---------------- | - |
| ビルドステップの並列実行 | ○ | ○ |
| ビルドキャッシュの出力<br>&emsp;&emsp;inline形式 | ○ | ○ |
| &emsp;&emsp;registry形式 | × | ○ |
| &emsp;&emsp;local形式 | × | ○ |
| ビルドキャッシュの使用<br>&emsp;&emsp;registry形式 | ○ | ○ |
| &emsp;&emsp;local形式 | × | ○ |
| Dockerfileの実験的機能の使用<br>&emsp;&emsp;RUN --mount=type=bind | ○ | ○ |
| &emsp;&emsp;RUN --mount=type=cache | ○ | ○ |
| &emsp;&emsp;RUN --mount=type=tmpfs | ○ | ○ |
| &emsp;&emsp;RUN --mount=type=secret | ○ | ○ |
| &emsp;&emsp;RUN --mount=type=ssh | ○ | ○ |
| &emsp;&emsp;RUN --security=insecure\|sandbox | ○ | ○ |
| &emsp;&emsp;RUN --network=none\|host\|default | ○ | ○ |


## プラグインなしで利用する
docker単体でBuildKitを利用する方法です。  

* 方法1
    `/etc/docker/daemon.json` ファイルに下記の設定を追加します。


    !!! info "/etc/docker/daemon.json"
        ``` json
        {
           "features": {
                "buildkit": true
            }
        }
        ```

* 方法2
    環境変数で`DOCKER_BUILDKIT=1`を設定します。  
    bashの場合: `export DOCKER_BUILDKIT=1`

上記のどちらかを設定した上で、`docker build`コマンドを実行するとBuildKitが有効化されます。

## docker-buildxプラグインを使って利用する

docker-buildxは2020年6月現在では、まだ実験的機能と位置づけられています。  
そのためbuildxを利用するには、まずdocker CLIの設定で実験的機能を有効化する必要があります。  

### 実験的機能の有効化
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

### docker-buildxプラグインのインストール
Docker Desktop for Windows/Macを利用している場合は、あらかじめbuildxプラグインがDocker Desktopに含まれているため、インストールは不要です。  
Docker for Linuxの場合は、[GitHubのdocker/buildx][3][^3] リポジトリのリリースページからバイナリをダウンロードして、
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

[1]: https://github.com/moby/buildkit
[2]: https://qiita.com/tatsurou313/items/ad86da1bb9e8e570b6fa
[3]: https://github.com/docker/buildx
[4]: https://docs.docker.com/buildx/working-with-buildx/
[5]: https://github.com/marketplace/actions/docker-buildx

[^1]: [moby/buildkit: concurrent, cache-efficient, and Dockerfile-agnostic builder toolkit · GitHub][1]
[^2]: [BuildKitによりDockerとDocker Composeで外部キャッシュを使った効率的なビルドをする方法 - Qiita][2]
[^3]: [docker/buildx: Docker CLI plugin for extended build capabilities with BuildKit · GitHub][3]
[^4]: [Docker Buildx | Docker Documentation][4]
[^5]: [Docker Buildx · Actions · GitHub Marketplace][5]
