# Host Compute Service(HCS)
# Windowsのコンテナ
Windowsで利用できるコンテナ技術の一つ。  
Windowsのコンテナには大きく2種類あり、WindowsコンテナとHyper-Vコンテナと呼ばれる。  

利用できるOSバージョン/エディションは下記の通り。  

* Windows 10 Pro バージョン 1607以降
* Windows 10 Enterprise バージョン 1607以降
* Windows Server 2016
* Windows Server 2019

コンテナの操作にはdockerコマンドを利用するが、詳細についてはここでは割愛する。

## hcsdiag
Windowsコンテナの操作には通常dockerを利用するが、その他に`hcsdiag.exe`というものが存在する。  
しかしながら、コマンドのリファレンスが現時点(2019/12)で見つからないため、実行可能であったものをここに記載する。  
なお、hcsとはHost Computing Serviceの略のようである。


| command | 動作  |
| ------- | ----- |
| `hcsdiag list` |  |
| `hcsdiag exec <GUID>` |  |
| `hcsdiag console <GUID>` |  |

hcsdiag [options...]
 list Lists running containers and VMs.
 exec [-uvm] Executes a process inside the container.
 console [-uvm] [command line] Launches an interactive console inside the container.
 read [-uvm] [host file] Reads a file from the container and outputs it to standard output or a file.
 write [-uvm] [host file] Writes from standard input or a host file to a file in the container. kill Terminates a running container. 
 share [-uvm] [-readonly] Shares a host folder into the container.
