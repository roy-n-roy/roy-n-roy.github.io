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

そのため、WSLではLinuxシステムコールAPIをWindowsの機能として用意し、その上にLinuxディストリビューションをMicrosoft Storeでインストールするという形式をとっています。  

WSLにはバージョン1とバージョン2が存在し、それぞれLinuxシステムコールAPIの提供方法が異なります。  

| バージョン            | ベース技術                                              | システムコールAPI提供方法                   |
| --------------------- | ------------------------------------------------------- | ------------------------------------------- |
| バージョン1<br>(WSL1) | 「ピコプロセス」と呼ばれる<br>Windowsのプロセス隔離技術 | LxCore.sys/Lxss.sysという<br>NTカーネルドライバがLinux<br>システムコールをエミュレーション |
| バージョン2<br>(WSL2) | 軽量仮想マシン(lightweight VM)技術                      | 仮想マシン上で<br>実際のLinuxカーネルを稼働 |

なお、本記事ではWSLのバージョンを区別する場合には、WSLバージョン1を「WSL1」、  
バージョン2を「WSL2」として記載し、バージョンを明記せずに「WSL」とのみ記載する場合は両方を指すものとします。  

## WSL1の機能
### システムコールAPIの提供
* WSL1:ピコプロセスとカーネルモードLxCore.sys, lsxx.sys
	https://blogs.msdn.microsoft.com/wsl/2016/05/23/pico-process-overview/
	https://github.com/ionescu007/lxss/blob/master/WSL-BlueHat-Final.pdf
	* システムコール
	* プロセス管理、メモリ管理
	* ネットワーク

### ファイルシステム
* WSL1:ファイルシステム VolFsとDrvFs

### Linux→Windowsファイルシステムへのアクセス

## initの機能
### ユーザランド起動
* 共通: initとユーザランド起動

### Windows→Linuxファイルシステムへのアクセス
WindowsからLinux上のファイルシステムへは、UNCパスで`\\wsl$\[ディストリビューション名]`を指定することで、WSLで起動しているディストリビューションのファイルシステムへアクセスすることができます。  

#### 仕組み
Windows上からLinuxファイルシステムへのアクセスには「Plan 9 Filesystem Protocol(9P)」と呼ばれるプロトコルが利用されています。
これは、「Plan 9 from Bell Labs」というUNIXの後継としてベル研究所で開発されたOSにおいて、システムの構成要素間の接続を目的として開発されたネットワークプロトコルです。  

WSLではこれを応用して、Windows・Linux間の接続に用いられています。


<a href="/imgs/windows_wsl_windows_to_linux_file_access.png" data-lightbox="windows_wsl_windows_to_linux_file_access"><img src="/imgs/windows_wsl_windows_to_linux_file_access.png" /></a>  

### Linux→Windowsプログラムの呼び出し
* 共通: Linux内からWindowsプログラムの呼び出し

## WSL2の機能
### システムコールAPIの提供
* WSL2: Utility VMとLinuxカーネル

### ファイルシステム
* WSL2:仮想HDD(root.vhdx)

### Linux→Windowsファイルシステムへのアクセス
* WSL2:9P






# WSL2
Windows Subsystem for Linux(WSL)は仮想マシンのオーバーヘッドなしでGNU/Linuxの実行バイナリ(Executable and Linkable Format, ELF)を実行することのできる環境を提供する機能です。
Windows 10 バージョン1709 以降のHome/Proエディション共に利用することができます。  

2020年春ごろに公開予定のWindows 10 バージョン2004 以降では、現行のWSL(以降、バージョン1と記載) に加えて、WSL2(以降、WSL2 もしくは バージョン2と記載) を利用出来るようになります。

## WSL2の改善点
WSL2では、バージョン1と比較して、下記の改善がなされています。

* Linux上でのファイルアクセス速度の向上
* システムコールの完全互換

一方で、Linux上から、NTFSなどのWindows上のファイルへのアクセス速度は下がっているため、多くのファイルアクセスが必要な場面ではLinux側へファイルを移動させた上で処理する方が良いとされています。

これは、WSLバージョン1が「Windows上でELFバイナリを実行する」機能であったのに比べ、WSLバージョン2は「軽量仮想マシン上でLinuxコンテナを動作させる」機能であることによるものです。  


## 起動
1. `wsl.exe`をランチャーとして起動する
1. `wsl.exe`が`wslhost.exe`を子プロセスとして起動
1. `wslhost.exe`が`conhost.exe`を子プロセスとして起動し、コンソールと接続
1. 


## アーキテクチャ比較
<figure style="text-align: center;">
<a href="/imgs/windows_wsl_wsl2.png" data-lightbox="windows_wsl_wsl2"><img src="/imgs/windows_wsl_wsl2.png" /></a>  
<figcaption>図. WSLとWSL2 アーキテクチャの概略</figcaption>
</figure>

|                          | WSL1                                       | WSL2                                       |
| ------------------------ | ------------------------------------------ | ------------------------------------------ |
| ベース技術               | ピコプロセスと呼ばれるプロセス隔離環境     | Utility VMと呼ばれるの軽量仮想化環境       |
| カーネルランド           | Linuxカーネルは存在せず、ピコプロバイダーがシステムコールを変換しNTカーネル上で動作 | 軽量VM上でLinuxカーネルが動作 |
| Linuxプロセス            | Windowsプロセス(Pico Process)として動作    | 仮想マシン上で動作、ホストからは見えない   |
| Linuxプロセスの起動      | MS製init(9Pサーバ機能を兼ねる)             | ←                                         |
| フロントエンド           | `wsl.exe`および`wslhost.exe`がLxssManagerを経由してLinux内のinitと通信し、`conhost.exe`を用いてコンソールへ表示する | ← |
| Linuxシステムコール      | LxssManagerが受け取り、WindowsカーネルAPIに変換した上で、Windows NTカーネルが実行する。<br>一部のシステムコールには対応しない。 | Linuxカーネルでシステムコールを解釈し、<br>Hyper-V仮想マシン上で実行する。 |
| プロセス管理             | Windows上のプロセスとして管理される。 | Linuxカーネルにより管理される。   |
| メモリ管理               | Windows上でプロセス単位に管理される        | Linuxカーネルにより管理される。Windows上では仮想マシンの利用メモリとして扱われる。 |
| ファイルシステム         | wslfs(VolFs)をシステムパーティションとして利用する。 | 仮想HDDファイル上のext4等のファイルシステムをシステムパーティションとして利用する。 |
| デバイスアクセス         | デバイスファイルやprocfsを一部のみエミュレート | Linuxカーネルにより仮想マシンに接続されたデバイスファイルや完全なprocfsが提供される |
| LinuxからWindowsファイルシステムへのアクセス | VolFSとしてNTFS,ReFSをマウントし、9Pサーバを経由してアクセス | ← |
| WindowsからLinuxファイルシステムへのアクセス | 9Pサーバを経由して`\\wsl$`からUNCパスでアクセス | ← |

### WSL1のアーキテクチャ
WSL2との比較の前に、WSL1の仕組みについて説明していきます。
#### プロセス管理
Windows上で、Linuxディストリビューションを起動する時には、`wsl.exe`をランチャーとして起動します。
これは`ubuntu.exe`などから起動した場合も同様で、その子プロセスとして`wsl.exe`を起動しています。

`wsl.exe`を起動すると、その子プロセスとして`wslhost.exe`(WSL Backgroud Host)、孫プロセスとして`conhost.exe`(Console Host)を起動します。
それぞれがLinux側ユーザモードプロセスとの通信やWindows上でのコンソール表示などを行っています。

また同時に、LxssManagerの子プロセスとしてinitプロセスが立ち上がります。
なおこちらは、システムコールなどカーネルモードの通信をしているものと思われます。

Linux側でも同じく`/init`に配置されるinitプロセスがプロセスID=1のプロセスとして起動され、全てのプロセスはinitプロセスの子孫として紐付けられて起動します。  
ただし、このinitプロセスはSystem V initではなく、9Pサーバの機能を有するMS製のバイナリだそうで、これを用いてWindows側との通信を行っています。  

なお、WSLではSystem V initやSystemdは動作しておらず、自動起動スクリプトなども実行されません。

また、Linux上で起動したbashなどのELFバイナリのプロセスはWindowsプロセスとして起動され、Windowsプロセスとして管理されます。ですので、Windows上のタスクマネージャなどからでも確認することができます。

また、Linux側からコマンドプロンプトなどのWindowsアプリケーションを呼び出すこともできます。
仕組みとしては、Linux側でWindows側の実行ファイルが呼び出されると、前述のinitプログラムをWindowsアプリケーションのパスを引数に指定して起動します。
一方Windows側では、Linux側からの呼び出しを受けて、`wsl.exe`の子プロセスとしてWindows実行ファイルを実行します。
これにより、Linux内部からWindows実行ファイルを実行することができるようになっています。

なお、

#### メモリ管理
前述の通り、LinuxのバイナリがWindowsのプロセスとして動作するため、LxssManagerを通じてNTカーネル側でメモリを割り当てされているのだと思われます。

#### システムコール
WSLバージョン1では、LxssManagerというサービスがWindows上に常駐しています。
これが、Linux上ではカーネルの代替として機能します。  

LxssManagerは、ユーザランドプロセスからのシステムコールを受け付けて、Windows側のNT Kernelに流します。
ただし、一部のシステムコールは提供されていないため、iptablesなど動作しないプログラムも存在します。

#### ファイルシステム
WSLバージョン1では、ルートファイルシステムにはext4やxfsでもNTFSでもなく、`lxfs`というWSL独自のファイルシステムを使用しています。  
その実態は、「ファイルやフォルダはNTFS上に配置し、パーミッション情報などのメタデータを別途保持するもの」のようです。  
ですので、Windows上からLinuxのhomeディレクトリの内容などを参照することはできますが、編集するとメタデータに不整合が発生するため、避ける必要があります。  

一方、WSLではWindowsのCドライブなどが、初期状態でマウントされており、参照・編集することができます。  
こちらは`drvfs`というファイルシステムになっており、見た目上のパーミッションは`777`でオーナーはログインユーザ自身になっていますが、Windows上のアクセス権限とはリンクしておらず、パーミッションを変更することもできないようになっています。  

#### デバイス管理
ほとんどのデバイスは生えていませんが、COMポート(/dev/ttyS0など)やWindows側のネットワークデバイス、cpuinfoなどは見えるようです。

### WSL2のアーキテクチャ
#### プロセス管理
Windows上ではHyper-Vコンテナとして仮想マシンが常駐起動しており、その上でMS社によってカスタマイズされたLinuxカーネルが動作しています。
Linuxディストリビューションを起動すると前述の仮想マシン内でLinuxコンテナが起動し、WSL1と同様のinitプロセスが起動します。
Linux上で起動したbashなどのELFバイナリのプロセスはLinuxカーネルにより管理され、Windows側からは確認することができません。

