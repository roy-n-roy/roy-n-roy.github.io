# Docker Composeコマンドの更新スクリプト

Linuxでは、Docker自体はaptなどでパッケージ管理されていますが、docker-composeはcurlで取得してインストールするため、パッケージ管理されていません。  
新しいバージョンがあるかどうかの確認には、GitHubのリリースページを見に行く必要があり、更新を忘れがちになります。  

なので、docker-composeの更新をチェック・インストールするスクリプトを作成しました。  

<script src="https://gist.github.com/roy-n-roy/9f845ac90d3a19a79085c260525e61d8.js"></script>
