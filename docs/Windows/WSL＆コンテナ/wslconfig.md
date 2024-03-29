# wsl.conf と .wslconfig

WSL上のディストリビューションの構成について、`/etc/wsl.conf`で設定することができます。  
また、WSL2の各ディストリビューションのコンテナをホストする軽量仮想マシンの構成については、
各ユーザの`C:\Users\[username]\.wslconfig`で設定することができます。  
詳細は、[Microsoftのドキュメント](https://docs.microsoft.com/ja-jp/windows/wsl/wsl-config#configuration-options)を参照してください。  

なお、最新ビルドの情報について知りたい場合は、[WSLのリリースノート](https://docs.microsoft.com/ja-jp/windows/wsl/release-notes)を参照するとよいでしょう。

## wsl.conf:ディストリビューション毎の構成


!!! info "/etc/wsl.conf"
	``` 
	[automount]
	enabled=true                # Cドライブなどの DrvFs の自動マウントする
	mountFsTab=true             # WSLの起動時に /etc/fstab を読み込んで自動的にマウントする
	root="/mnt/"                # DrvFsのマウント先
	options=""                  # DrvFsのマウントオプション
	                            # 規定値: `uid=1000,gid=1000,umask=000,fmask=000,dmask=000,metadata=disabled,case=off`
	crossDistro=true            # ディストリビューションを跨いだマウントをサポートする (ver2004以降)
	[network]
	generateHosts=true          # /etc/hosts を自動生成する
	generateResolvConf=true     # /etc/resolv.conf を自動生成する
	hostname=<string>           # WSLディストリビューションのホスト名 規定値: Windowsのホスト名と同じ
	[interop]
	enabled=true                # WSL内からWindowsプログラムの起動をサポートする (ver1809以降)
	appendWindowsPath=true      # WSL内のPATH環境変数に、WindowsのPATH環境変数を追加する (ver1809以降)
	[user]
	default=<string>            # 規定のログインユーザ名を指定する (ver2004以降) 規定値: レジストリ値に従う
	[filesystem]
	umask=0022                  # デフォルトのパーミッションを指定する (ver2004以降)
	[boot]
	systemd=true                # Systemdを有効にする (WSLバージョン 0.67.6以降)
	command=""                  # WSLインスタンス開始時に実行するコマンド、rootユーザで実行される (Windows11およびWindows Server 2022以降)
	```


## .wslconf:WSL2の軽量仮想マシンの構成


!!! info "%USERPROFILE%\\.wslconfig"
	```
	[wsl2]
	kernel=<path>               # カスタムLinuxカーネルの(Windows上の)パスを指定する
	kernelCommandLine=<string>  # カーネルコマンド引数を指定する
	memory=<size>               # WSL2の軽量仮想マシンで使用する最大メモリサイズを指定する
	processors=<number>         # WSL2の軽量仮想マシンで使用するCPU数を指定する
	swap=<size>                 # WSL2の軽量仮想マシンで使用するスワップファイルのサイズを指定する
	                            # 0を指定した場合はスワップファイルを使用しない
	swapFile=<path>             # スワップファイルに使用するVHDファイルの(Windows上の)パスを指定する
	localhostForwarding=true    # WSLのネットワークポート待ち受けを、ホストマシンにフォワーディングする
	pageReporting=true          # WSL2仮想マシンに割り当てられた未使用のメモリを再利用する
	guiApplications=true        # WSLgを利用してWSL上でGUIアプリケーションの実行サポートを有効化する (Windows11のみ)
	debugConsole=false          # WSL2ディストリビューションの起動時にdmesgの内容を表示する
	nestedVirtualization=true   # WSL2ディストリビューション内でNested Virtualizationを有効化する (Windows11のみ)
	vmIdleTimeout               # WSL2仮想マシンがアイドル状態になってからシャットダウンされるまでの時間(ミリ秒) (Windows11のみ)

	# <path> entries must be absolute Windows paths with escaped backslashes,
	# for example C:\\Users\\Ben\\kernel
	# <size> entries must be size followed by unit, for example 8GB or 512MB
	```
