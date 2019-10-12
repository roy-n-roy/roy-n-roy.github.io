# Wordpress
Wordpress Webサイトを作成し、https-portalでLet's Encryptのサーバ証明書を自動取得/公開する。外部からの80,443/TCP接続を解放する必要がある。  
また、ddclientで、Dynamic DNSのレコード更新を行う。  

バックアップスクリプト`wp_backup.sh`は、Wordpressで使用している`/var/run/html`とMySQLデータベースをバックアップする。  

* Weblogサイト作成&バックアップ  
[docker-compose.yml](https://gist.github.com/roy-n-roy/75370b28f639fdb489ca321001717eb8#file-docker-compose-yml)
<script src="https://gist.github.com/roy-n-roy/75370b28f639fdb489ca321001717eb8.js?file=docker-compose.yml"></script>
[wp_backup.sh](https://gist.github.com/roy-n-roy/75370b28f639fdb489ca321001717eb8#file-wp_backup-sh)
<script src="https://gist.github.com/roy-n-roy/75370b28f639fdb489ca321001717eb8.js?file=wp_backup.sh"></script>
