# LVM(Logical Volume Manager)
LinuxでHDDやSSDなどの物理ディスクを隠蔽し、論理ボリュームとして扱う仕組みです。  
OSをインストールし、稼働開始した後からディスク容量を追加したり、複数のディスクをまとめて利用したりすることができます。  

LVMは、下記のような要素から構成されています。  

* 物理ボリューム (Physical Volume, PV)  
	LVMで管理している物理ディスクのパーティションを指します。  
* ボリュームグループ (Volume Group, VG)  
	複数の物理ボリュームをまとめたグループを指します。  
* 論理ボリューム (Logical Volume, LV)
	ボリュームグループの一部、もしくは全部を切り出したものを指し、OSは論理ボリュームをマウントして利用します。  
	必ず、1つのボリュームグループから作成します。  

## LVMの拡張
OSの稼働中にディスク容量が不足した場合には、物理ディスクの空きがあれば、論理ディスクを拡張することができます。  
論理ディスクの拡張するためには、下記のコマンドを実行します。

!!! example "LVMへ新規ディスク追加"
	```
	# 新たなHDD/SSDをフォーマットし、物理ボリュームを作成
	sudo parted -s -a optimal /dev/sdx mklabel gpt mkpart primary 0% 100% set 1 lvm on
	# 作成したパーティションから物理ボリュームを作成
	sudo pvcreate /dev/sdx1
	# 確認
	sudo pvdisplay
	```

!!! example "物理ボリュームをボリュームグループ「ubuntu-vg」に追加"
	```
	sudo vgextend ubuntu-vg /dev/sdx1
	# 確認
	sudo vgdisplay
	sudo pvdisplay
	```

!!! example "ボリュームグループ「ubuntu-vg」の論理ボリューム「ubuntu-lv」に「5GB」追加"
	```
	sudo lvextend -L +5120m /dev/ubuntu-vg/ubuntu-lv
	# 確認
	sudo lvdisplay

	# ファイルシステム拡張
	sudo resize2fs /dev/ubuntu-vg/ubuntu-lv
	# 確認
	df -h
	```

もしくは、  

!!! example "ボリュームグループ「ubuntu-vg」の論理ボリューム「ubuntu-lv」を「最大サイズ」まで拡張"
	```
	sudo lvextend -l +100%FREE /dev/ubuntu-vg/ubuntu-lv
	# 確認
	sudo lvdisplay

	# ファイルシステム拡張
	sudo resize2fs /dev/ubuntu-vg/ubuntu-lv
	# 確認
	df -h
	```
