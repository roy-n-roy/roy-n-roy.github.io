# WSL2
Windows Subsystem for Linux(WSL)は仮想マシンのオーバーヘッドなしでGNU/Linuxの実行バイナリ(Executable and Linkable Format, ELF)を実行することのできる環境を提供します。
Windows 10 バージョン2004 以降では、現行のWSL(以降、バージョン1と記載) に加えて、WSL2(以降、WSL2 もしくは バージョン2と記載) を利用出来るようになります。

## WSL2の改善点
WSL2では、バージョン1と比べて、下記の改善がなされています。

* Linux上でのファイルアクセス速度の向上
* システムコールの完全互換

一方で、Linux上から、NTFSなどのWindows上のファイルへのアクセス速度は下がっているため、多くのファイルアクセスが必要な場面ではLinux側へファイルを移動させた上で処理する方が良いでしょう。

## アーキテクチャ比較
### WSL1のアーキテクチャ
WSL2との比較の前に、WSL1の仕組みについて説明していきます。
#### プロセス関連
WSLバージョン1では、LxssManagerがWindows上のサービスとして常駐しています。
これが、Linux上ではカーネルの代替として機能します。  

Windows上で、Linuxディストリビューションを起動するとLxssManagerの子プロセスとしてinitプロセスが立ち上がります。
Linux側でも同じくinitプロセスがプロセスID=1のプロセスとして起動され、全てのプロセスはinitプロセスの子孫として紐付けられて起動します。  

Linux上では、これがカーネルの代替として、ファイルシステムドライバや


<figure style="text-align: center;">
<a href="/imgs/windows_wsl_wsl2.png" data-lightbox="windows_wsl_wsl2"><img src="/imgs/windows_wsl_wsl2.png" /></a>  
<figcaption>図. WSLとWSL2 アーキテクチャの比較</figcaption>
</figure>