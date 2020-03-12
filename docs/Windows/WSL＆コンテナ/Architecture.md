# WSLのアーキテクチャ
## WSLで実現できること
Windows Subsystem for Linux(WSL)は少ないオーバーヘッドでGNU/LinuxのCLIプログラムを実行できる環境を提供する機能です。

Windowsでは「Portable Executable」という形式の実行ファイルのみを動作させることができます。
しかし、Linuxなどで利用されている実行ファイルは「Executable and Linkable Format(ELF)」と呼ばれる形式であるため、通常はWindows上で動作させることはできません。  

LinuxのCLIプログラムを利用できる環境を用意するには、下記のような機能が必要です。

* Linuxカーネルの機能  
	ファイルシステム・プロセス管理・メモリ管理などのシステムコールAPIの提供
* シェル環境  
	bash, zsh, kshなど
* パッケージマネージャ  
	プログラムとライブラリの入手方法の提供

WSLではLinuxシステムコールAPIをWindowsの機能として用意し、その上にLinuxディストリビューションをMicrosoft Storeからインストールするという形式をとっています。  

WSLにはバージョン1とバージョン2が存在し、それぞれLinuxシステムコールAPIの提供方法が異なります。  

| バージョン            | ベース技術                                              | システムコールAPI提供方法                   |
| --------------------- | ------------------------------------------------------- | ------------------------------------------- |
| バージョン1<br>(WSL1) | 「ピコプロセス」と呼ばれる<br>Windowsのプロセス隔離技術 | LxCore.sys/Lxss.sysという<br>NTカーネルドライバがLinux<br>システムコールをエミュレーション<br>(Linuxカーネルを使用しない) |
| バージョン2<br>(WSL2) | 軽量仮想マシン(lightweight VM)<br>+Linuxカーネル        | 仮想マシン上でLinuxカーネルを稼働 |

なお、本記事ではWSLのバージョンを明確に区別するため、WSLバージョン1を「WSL1」、バージョン2を「WSL2」と記載します。  
また、WSL1とWSL2の両方に共通する機能の場合は「WSL1/WSL2」という風に記載します。  

## WSL1の機能
### 構成要素
WSL1は、下記の図に示されるような要素から成り立っています。

<a href="/imgs/windows_wsl_wsl1.png" data-lightbox="windows_wsl_wsl1"><img src="/imgs/windows_wsl_wsl1.png" /></a>  

* ランチャー/フロントエンド(wsl.exe/wslhost.exe)

* LxssManager(LxssManager.dll)

* ピコプロバイダー(カーネルモードドライバー: LxCore.sys/Lxss.sys)

* ピコプロセス
	* MS製initプロセス
	* Linuxディストリビューション

* Plan9プロトコル リダイレクタ(カーネルモードドライバー: p9rdr.sys)

参考: DEFEND AND UNDERSTAND WSL - ionescu007/lxss - Github[^1]

### プロセス管理と「ピコプロセス」
WSL1では、Windows上で「ピコプロセス(Pico Process)」[^2]と呼ばれる形式のプロセスとして、Linuxプログラムを動作させます。  

「ピコプロセス」は、Windowsの「最小プロセス(Minimal Porcess)」という仕組みを利用して実現しています。
「最小プロセス」は通常のユーザーモードプロセスと下記のような点が異なります。

!!! quote "「最小プロセス」の特徴"

> 1. ntdll.dllはプロセスにマップされない  
		ユーザーモードのバイナリーである「ntdll.dll」は、デフォルトでプロセスにマップされません。  

> 2. PEBは生成されない  
	プロセスの管理に使用するPEB（Process Environment Block）は生成されません。  

> 3. 初期スレッドは生成されない  
	プロセス生成時、初期スレッド（メインスレッド）を生成しません。  

> 4. TEBは自動的に生成されない  
	「ピコプロセス」内でスレッドが生成されても、スレッドの管理に使用するTEB（Thread Environment Block）は自動的に生成されません。  

> 5. 共有ユーザーデータセクションはマップされない  
	共有ユーザーデータセクションは、プロセスにマップされません。  
	共有ユーザーデータセクションとは、すべてのユーザーモードのアドレス空間に読み込み専用でマップされ、システム共通の情報を効果的に検索するために使用されるブロックです。  

> 6. PEB/TEBなしで動作する  
	従来のプロセスのようにプロセスが常にPEB/TEBを持っている前提で動作する個所は、PEB/TEBなしでもプロセスを扱えるように変更されています。  

> 7. カーネルは積極的にプロセスの管理を行わない  
	Windowsカーネルは、積極的にプロセスの管理を行いません。  
	しかしスレッドのスケジューリングやメモリー管理など、ユーザーが利用したいOSのすべての基盤技術は引き続き提供されます。  

> 引用元: <cite>WSL その19 - WSLを構成する基盤の1つであるピコプロセスとは - kledgeb[^3]</cite>  

「ピコプロセス」は、これらの特徴を利用して、通常のWindowsプロセスからの隔離と最小限のプロセス管理を実現しています。  

### システムコールAPIの提供
WSL1では、LxCore.sys, lsxx.sysの2つのカーネルモードドライバーがNTカーネル上で動作しています。  
この2つのドライバーは「ピコプロバイダー」と呼ばれ、これらがLinuxシステムコールAPIを提供しています。  
「ピコプロセス」の呼び出したシステムコールや例外は、ドライバー上での処理やWindowsシステムコールへの変換されます。
これにより、WSL1においてLinuxカーネル相当の機能を実現しています。  

参考文献: WSL その24 - システムコールとは（前編）・LinuxカーネルのシステムコールとWindows NTカーネルのシステムコール - kledgeb[^4]

### ファイルシステム
#### VolFs
「VolFs」とは、WSL1で動作するディストリビューションのルートパーティションで使用するファイルシステムです。  
これは、WSL1独自のファイルシステムであり、WSL1ではext4やxfs、btrfsといったファイルシステムをルートパーティションに利用することはできません。

VolFsでのファイルの実体は、WindowsのNTFS上に保存されています。  
しかし、NTFSではLinux上で利用されるパーミッション情報などが保存できないため、VolFsでは実ファイルとは別にメタデータとしてパーミッション情報を保存しています。  

VolFsは、ext4やxfs、btrfsと同様に、Virtual File System(VFS)というファイルシステムの抽象化インターフェースの上に実装されており、他のLinux上で利用されるファイルシステムと同様に扱うことができるようになっています。  

#### DrvFs
「DrvFs」とは、WSL1の中からWindows上のCドライブなどの「ドライブ文字を割り当てられているローカルファイルシステム」へアクセスするためのファイルシステムです。  
ネットワークドライブには対応していません。  

こちらもWSL1の独自のファイルシステムですが、パーミッション情報などはログインしたユーザで`777`もしくは`555`で固定されており、変更することはできません。  

WSLの起動時に自動マウントされるようになっていますが、USBフラッシュディスクなどを後から接続した場合は、下記のようなコマンドで手動マウントすることでアクセスできるようになります。  

!!! example "Eドライブをマウント"
	```
	sudo mkdir /mnt/e
	sudo mount -t drvfs E: /mnt/e
	```

## initプロセスについて
Linuxシステムでは通常、カーネルによりinitプロセスが起動され、その後initが各Daemonの起動を担い、Linuxシステム上の全てのプロセスはプロセスID = 1 のinitプロセスを親として起動されます。  

WSLでも、initプロセスが全プロセスの親プロセスとなる点は同様です。  
しかし、WSLで利用されるinitは、WSL専用にMS社によって開発されたソフトウェアであり、通常のLinuxで利用されているSystem V initやsystemdとは異なるものとなっています。  

WSLのinitプログラムは`/sbin/init`ではなく、`/init`に配置されています。  

### ユーザランドプロセスの起動
WSLでは、Daemonの起動は行われず、この点がSystem V initやsystemdなどとは異なります。  

WSLが起動されると、プロセスID = 1 のプロセスとして最初に起動し、`/etc/passwd`ファイルに記載されているログインシェルを実行します。  

### Windows→Linuxファイルシステムへのアクセス
またWSLのinitは、WindowsからLinuxファイルシステムへアクセスするための機能を提供しています。  

WindowsからLinux上のファイルシステムへは、UNCパスで`\\wsl$\[ディストリビューション名]`を指定することで、WSLで起動しているディストリビューションのファイルシステムへアクセスすることができます。  

#### 仕組み
Windows上からLinuxファイルシステムへのアクセスには「Plan 9 Filesystem Protocol(9P)」と呼ばれるプロトコルが利用されています。
これは、「Plan 9 from Bell Labs」というUNIXの後継としてベル研究所で開発されたOSにおいて、システムの構成要素間の接続を目的として開発されたネットワークプロトコルです。  

WSLのinitには9Pサーバを搭載しており、Windowsからネットワーク接続を通じて、9Pサーバへアクセスすることができます。  
initプロセスは、9Pサーバへのアクセスを受け取ると、Linuxファイルシステム上のファイルを読み書きするような形になっています。  

また、Windows側では`p9rdr.sys`というファイルシステムリダイレクタがカーネルモードドライバーとして稼働しています。  
このリダイレクタはWindowsプロセスから`\\wsl$`へアクセスした際に動作し、P9クライアントとしてWSL上のP9サーバへアクセスし、9Pサーバから受け取ったファイルやフォルダなどのデータをエクスプローラーなどのWindowsアプリケーション上に表現することで、WindowsからLinuxファイルシステムへのアクセスを実現しています。  

<a href="/imgs/windows_wsl_windows_to_linux_file_access.png" data-lightbox="windows_wsl_windows_to_linux_file_access"><img src="/imgs/windows_wsl_windows_to_linux_file_access.png" /></a>  

### Linux→Windowsプログラムの呼び出し
WSLでは、WSL内のbashなどから、`cmd.exe`などのWindowsプログラムを呼び出すことができます。  

#### 仕組み
initプログラムの引数にWindowsプログラムを指定すると、WSL内からWindows上へ情報が渡され、Windows上でプログラムが起動します。  

WSLではDrvFSにより`/mnt/c/`などのディレクトリに、Windowsのファイルシステムをマウントしており、
Windowsプログラムはその配下に配置されています。  
WSLからWindowsプログラムを呼び出す際には、initプログラムの引数に`/mnt/c/`から始まるWindowsファイルシステム上のプログラムパスを与えると、initに内部で`C:\`から始まるWindows側でのパスに変換され、LxCore.sysなどを通して`wsl.exe`へ渡されます。
`wsl.exe`が渡されたパスのWindowsプログラムを起動することで、WSL内部からWindowsプログラムをしています。  

また、デフォルトでWindows上のPATH環境変数をWSLへ引き継いでいるため、フルパスを指定する必要がないようになっています。
(ただし、コマンドプロンプトやPowershellと異なり、`.exe`といった拡張子の指定は必要です。)  

## WSL2の機能
### WSL2とは
2020年春ごろに公開予定のWindows 10 バージョン2004 以降では、現行のWSL(以降、バージョン1と記載) に加えて、WSL2(以降、WSL2 もしくは バージョン2と記載) を利用出来るようになります。

WSL2では、バージョン1と比較して、下記の改善がなされています。

* Linux上でのファイルアクセス速度の向上
* システムコールの完全互換

WSL2は、WSL1を置き換えるものではなく、ディストリビューション単位でバージョン切り替えて利用することが出来ます。  

!!! note "WSL1からWSL2に切り替えるコマンド"

	```
	> wsl.exe --list --verbose
	  NAME                   STATE           VERSION
	* Ubuntu                 Running         1

	> wsl.exe --set-version Ubuntu 2
	変換中です。この処理には数分かかることがあります...
	WSL 2 との主な違いについては、https://aka.ms/wsl2 を参照してください
	変換が完了しました。

	> wsl.exe --list --verbose
	  NAME                   STATE           VERSION
	* Ubuntu                 Running         2
	```

??? note "WSL2からWSL1に戻すコマンド"

	```
	> wsl.exe --list --verbose
	  NAME                   STATE           VERSION
	* Ubuntu                 Running         2

	> wsl.exe --set-version Ubuntu 1
	変換中です。この処理には数分かかることがあります...
	変換が完了しました。

	> wsl.exe --list --verbose
	  NAME                   STATE           VERSION
	* Ubuntu                 Running         1
	```

### WSL2の構成要素
WSL2は、下記の図に示されるような要素から成り立っています。

<figure style="text-align: center;">
<a href="/imgs/windows_wsl_wsl2.png" data-lightbox="windows_wsl_wsl2"><img src="/imgs/windows_wsl_wsl2.png" /></a>  
<figcaption>図. WSLとWSL2 アーキテクチャの概略</figcaption>
</figure>

* ランチャー/フロントエンド(wsl.exe/wslhost.exe)

* LxssManager(LxssManager.dll)

* Hyper-V ホスト コンピューティング サービス(vmcompute.exe)

* 仮想マシン ワーカー プロセス(vmwp.exe : 9Pサーバ機能を含む)

* Hyper-Vハイパーバイザ
	* 軽量仮想マシン(Light-weight Virtual Machine)
		* Linuxカーネル
		* コンテナ
			* 仮想HDD(ext4.vhdx)
			* MS製init(9Pサーバ機能を含む)
			* Linuxディストリビューション

* Plan9プロトコル リダイレクタ(カーネルモードドライバー: p9rdr.sys)

参考: The new Windows subsystem for Linux architecture: a deep dive - BRK3068 - Microsoft Developer - YouTube[^6]

### システムコールAPIの提供
WSL2では、完全なLinuxシステムコールの提供のため、Linuxカーネルを実行しています。
カーネルの実行環境としてHyper-Vのような準仮想化ハイパーバイザを使用しており、ホストOSとなるWindows10もHyper-Vの有効化時と同様に、仮想化環境の中に入ります。  

対してWSL環境は、軽量仮想マシンと呼ばれるタイプの仮想マシンインスタンス上でLinuxカーネルが起動し、その上で実行されるコンテナランタイム上で動作します。(Ubuntuであれば、`Ubuntu` on `Container` on `Light weight VM` on `Hyper-V`です。)  
また、LinuxカーネルはMicrosoft社によりカスタマイズされたものが使用されており、これはGithub上で公開されています。[^5]

### ファイルシステム
### ルートファイルシステム
ディストリビューションがインストールされる、ルートファイルシステムが以下のように変更されています。

* WSL1: NTFS上にマッピングされたVolFS
* WSL2: 仮想HDD(root.vhdx)上のext4

NTFSを通して、メタデータを取得・設定する必要がなくなったために、アクセス速度が向上しています。

### Windowsファイルシステムへのアクセス
WSL内からWindows上のNTFSなどへアクセスする方法も変更されています。

* WSL1: DrvFSを通したアクセス
* WSL2: 9Pでのアクセス

WSL1でのDrvFSへのアクセスをシステムコールとして呼び出した際には、カーネルモードドライバーであるLxCore.sys, lsxx.sysが処理していました。  
しかし、WSL2では軽量仮想マシン+コンテナ技術を採用しているため、カーネルモードドライバーを利用した方法から、9Pを経由したアクセスに変更されています。

WSL内のinitと同様に、Windows側でも軽量仮想マシンのVM Workderプロセス内で9Pサーバが動作しており[^7]、
この9Pサーバを通じて、LinuxプロセスからCドライブなどへアクセスされます。


[^1]: [DEFEND AND UNDERSTAND WSL - ionescu007/lxss - Github](https://github.com/ionescu007/lxss/blob/master/WSL-BlueHat-Final.pdf)
[^2]: [Pico Process Overview - Windows Subsystem for Linux](https://blogs.msdn.microsoft.com/wsl/2016/05/23/pico-process-overview/)
[^3]: [WSL その19 - WSLを構成する基盤の1つであるピコプロセスとは - kledgeb](https://kledgeb.blogspot.com/2016/06/wsl-19-wsl1.html)
[^4]: [WSL その24 - システムコールとは（前編）・LinuxカーネルのシステムコールとWindows NTカーネルのシステムコール - kledgeb](https://kledgeb.blogspot.com/2016/06/wsl-24-linuxwindows-nt.html)
[^5]: [GitHub - microsoft/WSL2-Linux-Kernel : The source for the Linux kernel used in Windows Subsystem for Linux 2 (WSL2)](https://github.com/microsoft/WSL2-Linux-Kernel)
[^6]: [The new Windows subsystem for Linux architecture: a deep dive - BRK3068 - Microsoft Developer - YouTube](https://www.youtube.com/watch?v=lwhMThePdIo)
[^7]: [Attacking the VM Worker Process - Microsoft Security Response Center](https://msrc-blog.microsoft.com/2019/09/11/attacking-the-vm-worker-process/)
