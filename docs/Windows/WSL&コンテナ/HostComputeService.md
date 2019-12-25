# Host Compute Service(HCS)
# Windowsのコンテナ
Windowsで利用できるコンテナ技術の一つ。  
Windowsのコンテナには大きく2種類あり、Windowsコンテナ(プロセス分離モード)とHyper-Vコンテナ(Hyper-V分離モード)と呼ばれる。[^1]  

2019/12現在、各モードのコンテナが利用できるOSバージョン/エディションは下記の通りです。  

* Hyper-Vコンテナ
	* Windows 10 Pro バージョン 1607以降
	* Windows 10 Enterprise バージョン 1607以降
	* Windows Server 2016
	* Windows Server 2019
* Windowsコンテナ
	* Windows 10 Pro バージョン 1909以降
	* Windows 10 Enterprise バージョン 1909以降
	* Windows Server 2016
	* Windows Server 2019

コンテナの操作にはdockerコマンドを利用するが、詳細についてはここでは割愛する。

## hcsdiag
Windowsコンテナの操作にはdockerを利用する場合が多いが、その他に`hcsdiag.exe`というものが存在する。  
しかしながら、コマンドのリファレンスが現時点(2019/12)で見つからないため、そのオプションと実行した結果をここに記載する。  

| 引数 | 説明(英語) | 実行結果 |
| list | Lists running containers and VMs. | GUID, |
| exec [-uvm] <GUID> | Executes a process inside the container. |
| console [-uvm] [command line] Launches an interactive console inside the container. |
| read [-uvm] [host file] | Reads a file from the container and outputs it to standard output or a file. |
| write [-uvm] [host file] | Writes from standard input or a host file to a file in the container. |
| kill <GUID> | Terminates a running container. | 
| share [-uvm] [-readonly] <GUID> | Shares a host folder into the container. |

[^1]: [Windows 10におけるWindowsコンテナの「プロセス分離モード」対応最新情報 - @IT](https://www.atmarkit.co.jp/ait/articles/1912/24/news011.html) 2019年12月24日 05時00分 公開
