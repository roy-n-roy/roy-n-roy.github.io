# WSLでCentOSを利用する
WSLでUbuntuやOpen SUSEなどのディストリビューションを追加するには、Microsoft Storeからインストールすることができますが、CentOSは2019/12現在、Storeで公開されていません。  
しかし、WSLでは自身でディストリビューションを追加することができます。

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
	curl -O https://cloud.centos.org/centos/7/images/CentOS-7-x86_64-GenericCloud-1907.raw.tar.gz
	tar xf CentOS-7-x86_64-GenericCloud.raw.tar.gz

	# 「losetup -l」で空きLoopデバイスを確認して、rawファイルを割当て
	losetup -l
	sudo losetup --partscan /dev/loop0 CentOS-7-x86_64-GenericCloud-1907.raw
	
	# マウント
	mkdir rootfs
	sudo mount /dev/loop0p1 rootfs

	# tarボールにrootfsをアーカイブ
	tar cf centos7_rootfs.tar -C rootfs/ .

	# 後片付け
	sudo umount rootfs
	sudo losetup -d /dev/loop0

	# 作成したrootfsのtarファイルをWindows側に移動
	mv centos7_rootfs.tar /mnt/c/Users/user/.
	```

## rootfsのインポート
作成したrootfsをWSLへインポートします。
これは、Windows上のPowershellで作業していきます。

!!! example "rootfsのインポート"
	```
	# インストール先フォルダの作成
	New-Item .\AppData\Local\wsl\CentOS\7.7.1907 -ItemType Directory

	# rootfsのインポート
	wsl.exe --import CentOS .\AppData\Local\wsl\CentOS\7.7.1907 .\centos7_rootfs.tar
	```

## CentOSにログイン
任意のフォルダもしくはデスクトップを右クリックし、「新規作成」→「ショートカット」を選択し、
CentOSへログインするためのショートカットを作成します。  

|                      |                                         |
| -------------------- | --------------------------------------- |
| 項目の場所           | `C:\Windows\System32\wsl.exe -d CentOS` |
| ショートカットの名前 | CentOS 7.7                              |

作成したショートカットから起動します。

<a href="/imgs/windows_wsl_centos.png" data-lightbox="windows_wsl_centos"><img src="/imgs/windows_wsl_centos.png" width=75% /></a>  

## ユーザの作成とsudoの有効化
初期状態ではrootユーザしかないため、作業用ユーザを作成してsudoが利用できるようにします。
ここでは、作成するユーザ名は「`roy`」としています。


!!! example "ユーザ作成とsudoの有効化"
	```
	# group作成
	groupadd -g 1000 roy

	# ユーザ作成
	useradd -g 1000 -u 1000 roy

	# wheelグループにユーザを追加
	usermod -G wheel roy

	# royユーザにパスワードを設定
	passwd roy

	# royユーザに切り替え
	su - roy

	# sudoが利用出来るか確認
	sudo yum update

	```

## wslで使用するデフォルトユーザの変更
現在の設定ではCentOSを起動した時にはrootユーザでログインされるようになっています。  
これを変更するにはWindows上のレジストリを修正する必要があります。修正は、下記の手順で行います。  

1. レジストリエディタを開き、`HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Lxss`を開きます。
1. その下にあるキー(フォルダ)の中から、`DistributionName`の値が「`CentOS`」になっているものを探します。
1. 同じキー(フォルダ)内にある`DefaultUid`の値を「0」から「1000(10進数)」に変更します。
1. レジストリエディタを閉じます。

<a href="/imgs/windows_wsl_centos_registry.png" data-lightbox="windows_wsl_centos_registry"><img src="/imgs/windows_wsl_centos_registry.png" width=75% /></a>  

その後、先ほど作成したショートカットからCentOSを起動すると先ほど作成したユーザ`roy`でログインされていることが確認できます。

## アイコンを変更したい  
CentOSのWebサイトからfavicon.icoをダウンロードして、ショートカットの「プロパティ」→「アイコンの変更」でダウンロードしたアイコンを割り当てるなどしてください。

## CentOS8を使いたい
2019/12/08時点ではCentOS8のクラウド用イメージが公開されていないため、RPMパッケージから作成します。
CentOS7へログインし、CentOS8のrootfsを作成していきます。

!!! example "rootfs作成"
	``` bash
	# CentOS8のリポジトリ設定ファイルを作成
	cat << _END_ > ./centos8.repo
	[centos8-base]
	name=CentOS-8-Base
	baseurl=http://mirror.centos.org/centos/8/BaseOS/x86_64/os/
	gpgcheck=0
	_END_

	# rootfsを作成
	mkdir rootfs
	sudo yum -y -c centos.repo --installroot=$PWD/rootfs \
	        --disablerepo="*" --enablerepo="centos8-base" groupinstall "Minimal Install"

	# tarボールにrootfsをアーカイブ
	tar cf centos8_rootfs.tar -C rootfs/ .

	# 作成したrootfsのtarファイルをWindows側に移動
	mv centos8_rootfs.tar /mnt/c/Users/user/.
	```

以降は、CentOS7と同様にインポートするとCentOS8環境が利用できるようになります。
