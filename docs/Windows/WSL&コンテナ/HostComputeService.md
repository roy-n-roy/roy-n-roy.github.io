# Windowsのコンテナ
## Host Compute Service(HCS)
Host Conpute ServiceはWindowsでコンテナを扱うためのAPIを提供するサービスです。[^1]
このサービスが、Linuxでのcontainerdとruncにあたる機能を提供します。  
Windowsのコンテナには大きく2種類あり、Windowsコンテナ(プロセス分離モード)とHyper-Vコンテナ(Hyper-V分離モード)と呼ばれています。[^1]  

2019/12現在、各モードのコンテナが利用できるOSバージョン/エディションは下記の通りです。  

* Windows Server 2016
* Windows Server 2019
* Windows 10 Pro バージョン 1607以降
* Windows 10 Enterprise バージョン 1607以降
	* ただし、Windowsコンテナの実行は バージョン 1809以降のみ可能

コンテナの操作にはdockerコマンドを利用するが、詳細についてはここでは割愛します。

## hcsdiag
Windowsコンテナの操作にはdockerを利用する場合が多いが、その他に`hcsdiag.exe`というものが存在します。  
しかしながら、コマンドのリファレンスが現時点(2019/12)で見つからないため、そのオプションと実行した結果をここに記載します。  

### **hcsdiag list**  
英語での説明:  
> 'Lists running containers and VMs.'  

実行した結果:  
&emsp;コンテナ or VMの一覧が表示される。  
&emsp;項目は、左から「コンテナ/VMの種類」「ステータス」「GUID」「作成したサービス?」と予想。

!!! example "hcsdiag list"
	上から、「Hyper-V コンテナ テンプレート」「Hyper-V コンテナ」「WSL2用仮想マシン」「Hyper-V仮想マシン」の4項目が表示されている。  
	なお、4つめの項目が「VMMS」となっている「Hyper-V仮想マシン」も起動しているが、「ステータス」は「Running」になっていない。  
	理由は分からない。  
	```
	PS > hcsdiag list
	0ACF54A5-CEEF-454A-BDC7-56D2C9A223B9
		Hyper-V Container Template, Created, 0ACF54A5-CEEF-454A-BDC7-56D2C9A223B9

	0c5b099512a9041d71b54544680416ac497a96b40206958a118777b2592393f6
		Hyper-V Container,          Running, 2A0A7D9B-25D0-4C18-B620-4FC1E92740F9, docker

	3F098403-148F-49FE-9EA3-1729298CD01F
		VM,                         Running, 3F098403-148F-49FE-9EA3-1729298CD01F, WSL

	EB83922C-E87B-45FF-B2A3-BBB773644DCA
		VM,                         Created, EB83922C-E87B-45FF-B2A3-BBB773644DCA, VMMS
	```
### **hcsdiag exec [-uvm] &lt;GUID&gt; [command line] **  
英語での説明:  
> 'Executes a process inside the container.'  

実行した結果:  
&emsp;コンテナの場合はプロセスを実行できたが、VMの場合はできない。  

!!! example "hcsdiag exec"
	```
	PS > hcsdiag exec 0c5b099512a9041d71b54544680416ac497a96b40206958a118777b2592393f6 cmd /c "dir C:\"
		Volume in drive C has no label.
		Volume Serial Number is C280-441F

		Directory of C:\

	11/27/2019  06:55 PM             5,510 License.txt
	12/25/2019  05:08 PM    <DIR>          Users
	12/25/2019  05:08 PM    <DIR>          Windows
					1 File(s)          5,510 bytes
					2 Dir(s)  21,299,453,952 bytes free
	PS > hcsdiag exec 3F098403-148F-49FE-9EA3-1729298CD01F bash
	PS > $?
	False
	PS > hcsdiag exec 3F098403-148F-49FE-9EA3-1729298CD01F cmd
	PS > $?
	False
	```

### **hcsdiag console [-uvm] &lt;GUID&gt;**  
英語での説明:  
> 'Launches an interactive console inside the container.'  

実行した結果:  
&emsp;コンテナの場合はコマンドプロンプトが表示されたが、VMの場合は何も起きない。

!!! example "hcsdiag read"
	```
	PS > hcsdiag console 0c5b099512a9041d71b54544680416ac497a96b40206958a118777b2592393f6
	Microsoft Windows [Version 10.0.19035.1]
	(c) 2019 Microsoft Corporation. All rights reserved.

	C:\Windows\system32>
	```

### **hcsdiag read [-uvm] &lt;GUID&gt; [host file] **  
英語での説明:  
> 'Reads a file from the container and outputs it to standard output or a file.'  

実行した結果:  
&emsp;コンテナの場合はコンテナ内のファイルが表示されたが、VMの場合は何も起きない。

!!! example "hcsdiag read"
	```
	PS > hcsdiag read 0c5b099512a9041d71b54544680416ac497a96b40206958a118777b2592393f6 'C:\License.txt'
	MICROSOFT SOFTWARE SUPPLEMENTAL LICENSE
	FOR WINDOWS CONTAINER BASE IMAGE

	This Supplemental License is for the Windows Container Base Image ("Container Image").  If you comply with the terms of this Supplemental License you may use the Container Image as described below.

	   ≪以下略≫
	```


### **hcsdiag write [-uvm] [host file] &lt;GUID&gt;**  
英語での説明:  
> 'Writes from standard input or a host file to a file in the container.'  

実行した結果:  
&emsp;コンテナの場合はコンテナ内のファイルが作成されたが、VMの場合は何も起きない。

!!! example "hcsdiag write"
	```
	PS > hcsdiag write 0c5b099512a9041d71b54544680416ac497a96b40206958a118777b2592393f6 'C:\Users\ContainerUser\hoge.txt'
	hogehoge
	hoge
	PS > hcsdiag exec 0c5b099512a9041d71b54544680416ac497a96b40206958a118777b2592393f6 cmd /c 'more C:\Users\ContainerUser\hoge.txt'

	hogehoge
	hoge
	```

### **hcsdiag kill &lt;GUID&gt;**  
英語での説明:  
> 'Terminates a running container.'  

実行した結果:  
&emsp;コンテナの場合は強制終了、WSLのVMの場合も強制終了された。Hyper-V仮想マシンの場合は、仮想マシンが強制リセットされた。

!!! example "hcsdiag kill"
	```
	PS > hcsdiag list
	0ACF54A5-CEEF-454A-BDC7-56D2C9A223B9
		Hyper-V Container Template, Created, 0ACF54A5-CEEF-454A-BDC7-56D2C9A223B9

	0c5b099512a9041d71b54544680416ac497a96b40206958a118777b2592393f6
		Hyper-V Container,          Running, 2A0A7D9B-25D0-4C18-B620-4FC1E92740F9, docker

	3F098403-148F-49FE-9EA3-1729298CD01F
		VM,                         Running, 3F098403-148F-49FE-9EA3-1729298CD01F, WSL

	EB83922C-E87B-45FF-B2A3-BBB773644DCA
		VM,                         Created, EB83922C-E87B-45FF-B2A3-BBB773644DCA, VMMS

	PS C:\> hcsdiag kill 0c5b099512a9041d71b54544680416ac497a96b40206958a118777b2592393f6
	PS C:\> hcsdiag kill 3F098403-148F-49FE-9EA3-1729298CD01F
	PS C:\> hcsdiag kill EB83922C-E87B-45FF-B2A3-BBB773644DCA
	PS C:\> hcsdiag list
	0ACF54A5-CEEF-454A-BDC7-56D2C9A223B9
		Hyper-V Container Template, Created, 0ACF54A5-CEEF-454A-BDC7-56D2C9A223B9

	EB83922C-E87B-45FF-B2A3-BBB773644DCA
		VM,                         Created, EB83922C-E87B-45FF-B2A3-BBB773644DCA, VMMS

	PS C:\> hcsdiag kill EB83922C-E87B-45FF-B2A3-BBB773644DCA
	PS C:\> hcsdiag list
	0ACF54A5-CEEF-454A-BDC7-56D2C9A223B9
		Hyper-V Container Template, Created, 0ACF54A5-CEEF-454A-BDC7-56D2C9A223B9

	EB83922C-E87B-45FF-B2A3-BBB773644DCA
    VM,                         Created, EB83922C-E87B-45FF-B2A3-BBB773644DCA, VMMS

	```
### **hcsdiag share [-uvm] [-readonly] &lt;GUID&gt; <Folder> <DriveLetter>**  
英語での説明:  
> 'Shares a host folder into the container.'  

実行した結果:  
&emsp;コンテナの場合はコンテナにフォルダが共有された。VMの場合は何も起きない。

!!! example "hcsdiag share"
	```
	PS > hcsdiag share 0c5b099512a9041d71b54544680416ac497a96b40206958a118777b2592393f6 C:\temp Z:
	PS > hcsdiag exec 0c5b099512a9041d71b54544680416ac497a96b40206958a118777b2592393f6 cmd /c "dir Z:\"
	 Volume in drive Z has no label.
	 Volume Serial Number is 9A79-25D9

	 Directory of Z:\

	12/25/2019  07:25 PM    <DIR>          .
	12/25/2019  07:25 PM    <DIR>          ..
	               0 File(s)              0 bytes
	               2 Dir(s)  199,435,386,880 bytes free
	```

[^1]: [Windows 10におけるWindowsコンテナの「プロセス分離モード」対応最新情報 - @IT](https://www.atmarkit.co.jp/ait/articles/1912/24/news011.html) 2019年12月24日 05時00分 公開
