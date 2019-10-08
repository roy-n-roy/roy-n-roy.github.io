## ホストからのバックアップ

### バックアップ用ユーザの作成
adminでログインし、`backup`グループ/ユーザを作成し、公開鍵認証で接続出来るようにする。

#### SSH公開鍵作成 on Host PC
* 公開鍵/秘密鍵を作成  
よしなに入力する。  
パスフレーズを設定する場合は、ssh-agentへのパスフレーズ登録を行う。  

`> ssh-keygen -t rsa -b 4096`
```
Generating public/private rsa key pair.
Enter file in which to save the key (C:\Users\ryo/.ssh/id_rsa):
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in C:\Users\ryo/.ssh/id_rsa.
Your public key has been saved in C:\Users\ryo/.ssh/id_rsa.pub.
The key fingerprint is:
...
```

* 公開鍵をルータへ転送  

`> scp ~/.ssh/id_rsa.pub admin@192.168.XXX.XXX:.`
```
admin@192.168.XXX.XXX's password:
id_rsa.pub                             100%  605     0.6KB/s   00:00
```

* `~/.ssh/config`ファイルへ、ルータのIPアドレス/ユーザを追記する  
下記を追記する。

!!! note "~/.ssh/config"
	```
	Host Router  
	    Hostname 192.168.XXX.XXX
	    User backup
	```

#### バックアップ用ユーザ作成 on RouterOS
* グループ作成  

`/user group add name=backup policy=ssh,ftp,read,policy,test,sensitive`

* ユーザ作成  

`/user add name=backup group=backup password=************`

* 公開鍵の紐付け  

`/user ssh-keys import user=backup public-key-file=id_rsa.pub`

#### 接続確認 on Host PC
* 接続の確認  
パスワード入力なしに表示される。  

`> ssh Router "/system resource print"`

!!! success "Result"
	```
	                   uptime: 1w1d22h17m27s
	                  version: 6.45.6 (stable)
	               build-time: Sep/10/2019 09:06:31
	              free-memory: 428.1MiB
	             total-memory: 480.0MiB
	                      cpu: Intel(R)
	                cpu-count: 2
	            cpu-frequency: 3695MHz
	                 cpu-load: 1%
	           free-hdd-space: 29.3MiB
	          total-hdd-space: 63.5MiB
	  write-sect-since-reboot: 130136
	         write-sect-total: 130137
	        architecture-name: x86_64
	               board-name: CHR
	                 platform: MikroTik
	```

### バックアップ実行

#### スクリプト作成

* 下記の様なバックアップスクリプトを作成する

!!! example "backup_routeros.ps1"
	<script src="https://gist.github.com/roy-n-roy/3d52f6b831189ee9cc503590fee65aaa.js?file=backup_routeros.ps1"></script>

#### 実行

!!! success "Result"
	```
	PS C:\tools> .\backup_router.ps1
	Connected to Router.
	Fetching /Backup-20191008-164812.backup to C:/Users/Public/RouterOS_backup/Backup-20191008-164812.backup
	/Backup-20191008-164812.backup                                                      100%  354KB 338.2MB/s   00:00
	2019/10/08 16:48:12 バックアップに成功しました
	```
