# WSLでCentOS/Fedoraを利用する
WSLでUbuntuやOpen SUSEなどのディストリビューションを追加するには、Microsoft Storeからインストールすることができますが、 ~~CentOSは2019/12現在、Storeで公開されていません。~~ (2020/06/04 更新) 有志によって公開されていますが有償のようです。  
しかし、WSLでは自身でディストリビューションを追加することができます。

## イメージ入手
WSLへディストリビューションを追加するためには、rootfsのイメージが必要となります。  
今回はDockerなどのコンテナ用に用意されているrootfsイメージをダウンロードして利用します。  
Windows上のPowershellで作業していきます。


=== "CentOS"
	CentOSのダウンロードWebサイトでは、コンテナイメージのLayerの中身だけを取り出したファイルが公開されているので、そちらをrootfsとして利用します。

	!!! example "ダウンロード・解凍"
		``` bash
		# ダウンロード
		> curl.exe -O https://cloud.centos.org/centos/8/x86_64/images/CentOS-8-Container-8.1.1911-20200113.3-layer.x86_64.tar.xz
		# 既存のディストロを利用してxzファイルを解凍(`wsl.exe -e`= デフォルトのディストロ内でコマンドを実行)
		> wsl.exe -e unxz CentOS-8-Container-8.1.1911-20200113.3-layer.x86_64.tar.xz

		> Get-ChildItem CentOS-8-Container-8.1.1911-20200113.3-layer.x86_64.tar
			Directory: C:\Users\Roy

		 Mode                 LastWriteTime         Length Name
		 ----                 -------------         ------ ----
		 -a---          2020/06/04    11:32      256276480 CentOS-8-Container-8.1.1911-20200113.3-layer.x86_64.tar
		```

=== "Fedora"
	FedoraのダウンロードWebサイトでは、コンテナ環境へロードできるイメージファイルが公開されているので、そちらからrootfsとなるデータを取り出して利用します。

	!!! example "ダウンロード・解凍"
		``` bash
		# ダウンロード
		> curl.exe -O https://nrt.edge.kernel.org/fedora-buffet/fedora/linux/releases/32/Container/x86_64/images/Fedora-Container-Base-32-1.6.x86_64.tar.xz

		# layer.tarのパスを取得(`wsl.exe -e`= デフォルトのディストロ内でコマンドを実行)
		> $layer=(wsl.exe -e tar xf ./Fedora-Container-Base-32-1.6.x86_64.tar.xz manifest.json -O | ConvertFrom-Json).Layers
		# 既存のディストロを利用してtar.xzファイルの中からlayer.tarを解凍
		> wsl.exe -e tar xf ./Fedora-Container-Base-32-1.6.x86_64.tar.xz $layer

		> Get-ChildItem $layer
			Directory: C:\Users\Roy\d2b89e44ce52ccef64b35efd58302988a82469bf6c5cfeb1d6b3c7e7e0af6e07

		 Mode                 LastWriteTime         Length Name
		 ----                 -------------         ------ ----
		 -a---          2020/04/23     7:31      207544320 layer.tar
		```

??? tips "2020/06/04 更新前の記事 (rawファイルを利用する場合)"
	## 面倒なことはイヤという方に
	こちらで公開されているツールを利用しましょう。  
	[yuk7/CentWSL - GitHub](https://github.com/yuk7/CentWSL)

	## rootfsの作成
	WSLへディストリビューションを追加するためには、rootfsのイメージが必要となります。  
	今回はクラウド用に用意されているrootfsイメージをダウンロードして流用します。  
	ここからは、WSL上のUbuntuで作業していきます。

	!!! example "rootfs作成"
		``` bash
		# ダウンロード・解凍
		> curl -O https://cloud.centos.org/centos/7/images/CentOS-7-x86_64-GenericCloud-1907.raw.tar.gz
		> tar xf CentOS-7-x86_64-GenericCloud.raw.tar.gz

		# 「losetup -l」で空きLoopデバイスを確認して、rawファイルを割当て
		> losetup -l
		> sudo losetup --partscan /dev/loop0 CentOS-7-x86_64-GenericCloud-1907.raw
		
		# マウント
		> mkdir rootfs
		> sudo mount /dev/loop0p1 rootfs

		# tarボールにrootfsをアーカイブ
		> tar cf centos7_rootfs.tar -C rootfs/ .

		# 後片付け
		> sudo umount rootfs
		> sudo losetup -d /dev/loop0

		# 作成したrootfsのtarファイルをWindows側に移動
		> mv centos7_rootfs.tar /mnt/c/Users/user/.
		```

## rootfsのインポート
作成したrootfsをWSLへインポートします。
これは、Windows上のPowershellで作業していきます。

=== "CentOS"
	!!! example "rootfsのインポート"
		``` bash
		# インストール先フォルダの作成
		> New-Item $env:LOCALAPPDATA\wsl\CentOS\8.1.1911 -ItemType Directory

		# rootfsのインポート
		> wsl.exe --import CentOS $env:LOCALAPPDATA\wsl\CentOS\8.1.1911 .\CentOS-8-Container-8.1.1911-20200113.3-layer.x86_64.tar

		# 確認
		> wsl.exe -d CentOS grep PRETTY_NAME /etc/os-release
		PRETTY_NAME="CentOS Linux 8 (Core)"
		```
=== "Fedora"
	!!! example "rootfsのインポート"
		``` bash
		# インストール先フォルダの作成
		> New-Item $env:LOCALAPPDATA\wsl\Fedora\32-1.6 -ItemType Directory

		# rootfsのインポート
		> wsl.exe --import Fedora $env:LOCALAPPDATA\wsl\Fedora\32-1.6 .\d2b89e44ce52ccef64b35efd58302988a82469bf6c5cfeb1d6b3c7e7e0af6e07\layer.tar

		# 確認
		> wsl.exe -d Fedora grep PRETTY_NAME /etc/os-release
		PRETTY_NAME="Fedora 32 (Container Image)"
		```

## CentOS/Fedoraにログイン
任意のフォルダもしくはデスクトップを右クリックし、「新規作成」→「ショートカット」を選択し、
CentOS/Fedoraへログインするためのショートカットを作成します。  

|                      |                                         |                                         |
| -------------------- | --------------------------------------- | --------------------------------------- |
| 項目の場所           | `C:\Windows\System32\wsl.exe -d CentOS` | `C:\Windows\System32\wsl.exe -d Fedora` |
| ショートカットの名前 | CentOS 8.1                              | Fedora 32                               |

作成したショートカットから起動します。

<a href="/imgs/windows_wsl_centos.png" data-lightbox="windows_wsl_centos"><img src="/imgs/windows_wsl_centos.png" width=75% /></a>  

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
	> sudo yum update

	```

## wslで使用するデフォルトユーザの変更
現在の設定ではCentOSを起動した時にはrootユーザでログインされるようになっています。  
これを変更するにはWindows上のレジストリか、[各ディストロの `/etc/wsl.conf` に設定](../wslconfig/#wslconf)することで変更できます。  
ここでは、レジストリでの設定方法を紹介します。  

1. レジストリエディタを開き、`HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Lxss`を開きます。
1. その下にあるキー(フォルダ)の中から、`DistributionName`の値が「`CentOS`」になっているものを探します。
1. 同じキー(フォルダ)内にある`DefaultUid`の値を「0」から「1000(10進数)」に変更します。
1. レジストリエディタを閉じます。

<a href="/imgs/windows_wsl_centos_registry.png" data-lightbox="windows_wsl_centos_registry"><img src="/imgs/windows_wsl_centos_registry.png" width=75% /></a>  

その後、先ほど作成したショートカットからCentOSを起動すると先ほど作成したユーザ`roy`でログインされていることが確認できます。

## アイコンを変更したい  
CentOS/FedoraのWebサイトからロゴイメージなどを入手して、ショートカットの「プロパティ」→「アイコンの変更」でダウンロードしたアイコンを割り当てるなどしてください。

## インポートしたディストロを削除したい
ディストロを削除するには、WSLへの登録を解除した後に、インポートしたフォルダを削除します。

!!! example "ディストリビューション削除"
	```
	# wslから登録解除
	> wsl.exe --unregister CentOS
	> wsl.exe --unregister Fedora

	# ファイルシステムが保存されているインポート先フォルダを削除
	> Remove-Item -Recurse $env:LOCALAPPDATA\wsl\CentOS\8.1.1911\
	> Remove-Item -Recurse $env:LOCALAPPDATA\wsl\Fedora\32-1.6\

	# 手動でインポートしたディストロ全てを削除する場合
	> Remove-Item -Recurse $env:LOCALAPPDATA\wsl\
	```


??? tips "2020/06/04 更新前の記事 (クラウド・コンテナ用イメージが公開されていない場合)"
	## ~~CentOS8を使いたい~~ => yumコマンドでrootfsを作成
	2019/12/08時点ではCentOS8のクラウド用イメージが公開されていないため、RPMパッケージから作成します。
	CentOS7へログインし、CentOS8のrootfsを作成していきます。

	!!! example "rootfs作成"
		``` bash
		# CentOS8のリポジトリ設定ファイルを作成
		> cat << _END_ > ./centos8.repo
		[centos8-base]
		name=CentOS-8-Base
		baseurl=http://mirror.centos.org/centos/8/BaseOS/x86_64/os/
		gpgcheck=0
		_END_

		# rootfsを作成
		> mkdir rootfs
		> sudo yum -y -c centos.repo --installroot=$PWD/rootfs \
				--disablerepo="*" --enablerepo="centos8-base" groupinstall "Minimal Install"

		# tarボールにrootfsをアーカイブ
		> tar cf centos8_rootfs.tar -C rootfs/ .

		# 作成したrootfsのtarファイルをWindows側に移動
		> mv centos8_rootfs.tar /mnt/c/Users/user/.
		```

	以降は、CentOS7と同様にインポートするとCentOS8環境が利用できるようになります。
