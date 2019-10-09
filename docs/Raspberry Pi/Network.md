# ネットワーク設定

| 環境 |   |
| - | - |
| モデル | Raspberry Pi4 |
| ディストリビューション | Raspbian 10 Buster |
| インターフェース | eth0, usb0(USB-OTG), wlan0 |
| 接続優先度 | 有線LAN ⇒ USB-LAN ⇒<br>どちらも接続していない場合にのみ無線LAN APを起動 |

ネットワーク設定は下記とする。  

| インターフェース | ネットワーク設定 |
| - | - |
| eth0 | DHCPでIPアドレス/ゲートウェイを取得 |
| usb0 | 1対1接続のため、Raspberry PiをDHCPサーバとして機能させる。<br>Raspberry PI: `192.168.255.254/30`<br>対向PC: `192.168.255.253/30` |
| wlan0 | 1対多接続、Raspberry PiをDHCPサーバとして機能させる。<br>Raspberry PI: `192.168.253.1/24`<br>無線LANクライアント: `192.168.253.2～254/24` |

### Systemd-networkd
デフォルトのDHCP Client daemonを削除して、systemd-networkdを有効化する。  

1. dhcpcdを削除  
```
sudo apt purge dhcpcd  
```

1. 設定ファイルの配置
```
mv eth.network usb0.network wlan0.network /etc/systemd/network/.  
```

	!!! example "eth.network"
		<script src="https://gist.github.com/roy-n-roy/69cc483810efe17b7356d73036e9a2e2.js?file=eth.network"></script>

	!!! example "usb0.network"
		<script src="https://gist.github.com/roy-n-roy/69cc483810efe17b7356d73036e9a2e2.js?file=usb0.network"></script>

	!!! example "wlan0.network"
		<script src="https://gist.github.com/roy-n-roy/69cc483810efe17b7356d73036e9a2e2.js?file=wlan0.network"></script>

1. systemd-networkd, systemd-resolvedを有効化  
```
sudo systemctl enable systemd-networkd  
sudo systemctl enable systemd-resolved  
```
### USB on the GoのEthernetアダプタ有効化
1. 下記のスクリプトを`/usr/local/bin`に配置

	!!! example "init_usb_otg.sh"
		<script src="https://gist.github.com/roy-n-roy/69cc483810efe17b7356d73036e9a2e2.js?file=init_usb_otg.sh"></script>

1. 起動時に実行されるようsystemd serviceファイルを`/etc/systemd/system`に配置

	!!! example "usb_init.service"
		<script src="https://gist.github.com/roy-n-roy/69cc483810efe17b7356d73036e9a2e2.js?file=usb_init.service"></script>

1. usb_initを有効化
```
systemd daemon-reload
systemd enable usb_init
```

### Raspberry Piの無線LAN AP化
1. networkd-dispatcher, hostapdをインストール  
```
sudo apt install hostapd  
```

1. 設定ファイルを配置  
```
mv hostapd.conf /etc/hostapd/.  
```

1. hostapdを有効化  
```
sudo systemctl unmask hostapd  
```

### 接続優先度による無線LAN AP 起動/停止の設定
1. networkd-dispatcher, hostapdをインストール  
```
sudo apt install networkd-dispatcher  
```

1. 設定ファイルを配置  
他のネットワーク接続(eth0,usb0)が接続されている(routable)場合は無線LAN APを停止、  
他が切断された場合は無線LAN APを起動するスクリプトを設定する。
```
mv stop_ap.sh /etc/networkd-dispatcher/routable.d/.  
mv start_ap.sh /etc/networkd-dispatcher/off.d/.  
```

!!! example "stop_ap.sh"
	<script src="https://gist.github.com/roy-n-roy/69cc483810efe17b7356d73036e9a2e2.js?file=stop_ap.sh"></script>

!!! example "start_ap.sh"
	<script src="https://gist.github.com/roy-n-roy/69cc483810efe17b7356d73036e9a2e2.js?file=start_ap.sh"></script>

### USB接続時のPC側ドライバ
USB接続されたRaspberry Piのイーサネットポート`usb0`は、RNDIS(Remote Network Driver Interface Specification)と呼ばれる規格に則ったものであるため、Windows10であれば別途ドライバを準備する必要はない。  
しかし、セットアップ情報ファイル(INF)ファイルは用意されていないため、接続しただけではドライバが適用されない。  

そのため、初回接続時には下記の手順でドライバを適用する必要がある。
なお、この情報は2019/10時点のものであり、将来的には変更されている可能性がある点を事前に断っておく。  

1. デバイスマネージャを開く  
「RNDIS」というデバイスに警告アイコンが表示されている。これをダブルクリックするとプロパティ画面が表示される。  
<img width="400" src="/imgs/raspberrypi_network_devicemanager.png" />
<img width="250" src="/imgs/raspberrypi_network_deviceproperty.png" />  

1. ドライバ更新開始  
「ドライバの更新」ボタンからドライバ更新を開始する。  
「コンピューターを参照してドライバーソフトウェアを検索」「コンピューター上の利用可能なドライバーの一覧から選択します」と順に選択していく。  
<img width="450" src="/imgs/raspberrypi_network_driverupdate1.png" />  
<img width="450" src="/imgs/raspberrypi_network_driverupdate2.png" />  

1. ドライバ種別の選択  
続いて、「ネットワークアダプター」選択して次へ
<img width="450" src="/imgs/raspberrypi_network_driverupdate3.png" />  

1. ドライバの選択  
製造元の一覧から「Microsoft」を選択し、さらに「リモートNDIS互換デバイス」を選択して次へ
「ドライバーの更新警告」メッセージが表示されるが、無視して「はい」を選択  
<img width="450" src="/imgs/raspberrypi_network_driverupdate4.png" />  

1. ドライバ更新完了  
「ドライバーが正常に更新されました」と表示されれば更新完了である  
<img width="450" src="/imgs/raspberrypi_network_driverupdate5.png" />  



