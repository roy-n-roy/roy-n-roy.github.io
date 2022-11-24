# WSLでRed Hat Enterprise Linuxを利用する
Red Hat Enterprise Linuxは、開発者向けのRed Hat Developer Program[^1]に参加することで、無償で入手が可能です。  
今回はこちらを利用して、WSLへRed Hat Enterprise Linux(RHEL) 9.1をインストールします。

## イメージ入手
WSLへディストリビューションを追加するためには、rootfsのイメージが必要となります。  
RHELのrootfsを作成するため、dnfコマンドを利用できるLinuxディストリビューション(Fedora等)上で作業していきます。

!!! example "rootfs作成"
	``` bash
	# RHELメディアのリポジトリ設定ファイルを作成
	> cat << _END_ > ./media.repo
	[InstallMedia-BaseOS]
	name=Red Hat Enterprise Linux 9.1.0 - BaseOS
	mediaid=None
	metadata_expire=-1
	gpgcheck=0
	cost=500
	baseurl=file://$PWD/rhel9-iso/BaseOS/
	gpgkey=file://$PWD/rhel9-iso/RPM-GPG-KEY-redhat-release
	_END_

	# rootfsを作成
	> mkdir rootfs
	> sudo dnf -y -c media.repo --installroot $PWD/rhel9-rootfs \
		--disablerepo "*" --enablerepo "InstallMedia-BaseOS" groupinstall "Minimal Install"

	# tarボールにrootfsをアーカイブ
	> tar cf rhel9-rootfs.tar -C rhel9-rootfs/ .

	# 作成したrootfsのtarファイルをWindows側に移動
	> mv rhel9-rootfs.tar /mnt/c/Users/user/.
	```

## rootfsのインポート
作成したrootfsをWSLへインポートします。
これは、Windows上のPowershellで作業していきます。

!!! example "rootfsのインポート"
	``` posh
	# インストール先フォルダの作成
	> New-Item $env:LOCALAPPDATA\wsl\RHEL\9 -ItemType Directory

	# rootfsのインポート
	> wsl.exe --import RHEL $env:LOCALAPPDATA\wsl\RHEL\9 .\rhel9-rootfs.tar

	# 確認
	> wsl.exe -d RHEL grep PRETTY_NAME /etc/os-release
	PRETTY_NAME="Red Hat Enterprise Linux 9.1 (Plow)"
	```

## ユーザの作成とsudoの有効化
初期状態ではrootユーザしかないため、作業用ユーザを作成してsudoが利用できるようにします。
ここでは、作成するユーザ名は「`roy`」としています。


!!! example "ユーザ作成とsudoの有効化"
	``` bash
	# group作成
	> groupadd -g 1000 roy

	# ユーザ作成
	> useradd -g 1000 -u 1000 roy

	# wheelグループにユーザを追加
	> usermod -G wheel roy

	# royユーザにパスワードを設定
	> passwd roy

	# royユーザに切り替え
	> su - roy

	# sudoが利用出来るか確認
	> sudo subscription-manager status

	```

## wslで使用するデフォルトユーザの変更
現在の設定ではRHELを起動した時にはrootユーザでログインされるようになっています。  
これを変更するにはWindows上のレジストリか、[各ディストロの `/etc/wsl.conf` に設定](../wslconfig/#wslconf)することで変更できます。  
ここでは、レジストリでの設定方法を紹介します。Windows上のPowershellで作業していきます。  

!!! example "デフォルトユーザの変更"
	``` posh
	# RHELのレジストリキーを検索
	> $reg_key=(reg.exe query HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Lxss /s /d /f RHEL)[1]

	# レジストリキーを確認
	> reg.exe query $reg_key

	# デフォルトユーザのUIDを設定
	> reg.exe add $reg_key /v DefaultUid /t REG_DWORD /d 1000 /f
	```

その後、WSLのRHELを起動すると先ほど作成したユーザ`roy`でログインされていることが確認できます。

## サブスクリプション登録
パッケージの更新を入手するため、サブスクリプションマネージャーを利用して登録を実行します。  
登録の方法はRHRLのドキュメント[^2]を参照します。  

!!! example "サブスクリプション登録"
	``` bash
	# サブスクリプション登録
	> subscription-manager register
	## ユーザIDとパスワードを入力

	# パッケージ更新
	> sudo dnf update -y
	```


## インポートしたRHELをWSLから削除
ディストロを削除するには、WSLへの登録を解除した後にインポートしたフォルダを削除します。

!!! example "ディストリビューション削除"
	``` posh
	# wslから登録解除
	> wsl.exe --unregister RHEL

	# ファイルシステムが保存されているインポート先フォルダを削除
	> Remove-Item -Recurse $env:LOCALAPPDATA\wsl\RHEL\9

	# 手動でインポートしたディストロ全てを削除する場合
	> Remove-Item -Recurse $env:LOCALAPPDATA\wsl\
	```


[^1]: [Red Hat Developer Programに参加して最新技術を学習しよう - 赤帽エンジニアブログ](https://rheb.hatenablog.com/entry/developer-program)
[^2]: [第4章 システム登録およびサブスクリプション管理 Red Hat Enterprise Linux 9 - Red Hat Customer Portal](https://access.redhat.com/documentation/ja-jp/red_hat_enterprise_linux/9/html/configuring_basic_system_settings/assembly_registering-the-system-and-managing-subscriptions_configuring-basic-system-settings#proc_registering-the-system-after-the-installation_assembly_registering-the-system-and-managing-subscriptions)