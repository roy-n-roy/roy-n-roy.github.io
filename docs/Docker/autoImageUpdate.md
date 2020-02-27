# Docker Composeのイメージ更新自動化
Docker Composeで起動したコンテナのイメージを自動更新したかったので、
下記のようなスクリプトを作成してcrontabに登録しました。

<script src="https://gist.github.com/roy-n-roy/fc9fef25b2436d766238035a4fa6d3e3.js"></script>

## 前提条件
* 対象は、 `/etc/docker-compose.d/*/docker-compose.yml` で定義された実行中の全てのコンテナ。
* イメージをDocker Hubから取得してコンテナを作り直すため、コンテナ内で作業している時間帯に実行してはならない。
* コンテナを作り直すため、コンテナ内で変更した内容は破棄される。
