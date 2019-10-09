# Web Console
## 概要
Raspberry PiとPCを接続し、ブラウザからRaspberry Piにアクセスすることで
Web画面上で、あたかも直接PCを操作しているかのような環境を実現する。  

| 環境 |   |
| - | - |
| モデル | Raspberry Pi4 |
| ディストリビューション | Raspbian 10 Buster |

## 実現に必要な機能
PCを操作するための機能として「モニター」「キーボード」が、
加えてGUIで操作するには「マウス」も必要となる。

Web ConsoleではRaspberry Piを用いて、「キーボード」「マウス」「モニター」の3つをエミュレーションし、ブラウザからの入出力操作を実現する。  
それぞれを下記の様に実現した。  

| 機能 | 要件 | 方法 | 利用した<br>ソフトウェア |
| - | - | - | - |
| 「キーボード」「マウス」<br>エミュレーション | ブラウザからRaspberry Piへのキー・マウス入力 | WebブラウザとWebSocket                    | Node.jsを用いた<br>自作アプリ |
|                                          | Raspberry PiからPCへのキー・マウス操作再現   | USB On-the-Goを用いた<br>USBマウス・キーボードのエミュレーション | Linuxカーネルモジュール(libcomposite) |
| 「モニター」<br>エミュレーション          | PCから<br>Raspberry Piへの映像入力          | CSI-2 to HDMIブリッジモジュールを用いたHDMI入力 | Video4Linuxドライバ |
|                                          | Raspberry Piから<br>ブラウザへの画面表示     | Webブラウザへの動画ストリーミング配信      | WebRTCクライアント "Momo" |

## 接続方法

<style>
figure#raspi_fig { display:table; table-layout:fixed; }
figure#raspi_fig div { display:table-cell; vertical-align:middle; }
figure#raspi_fig div#hdmi { text-align:right; }
figure#raspi_fig div#lan { text-align:left; }
figure#raspi_fig figcaption { text-align:center; }
</style>
<figure id="raspi_fig">
<div id="hdmi"><br><br>HDMIケーブル→<br>(PCに接続)<br><br><br>USB Type-C→</div>
<img width="400" src="/imgs/raspberrypi_webconsole.jpg" />
<figcaption>Raspberry PiとCSI-2 to HDMIブリッジ</figcaption>
<div id="lan">←LANケーブル<br><br><br><br><br><br><br></div>
</figure>

## 苦労した点
* 正しく動作するレポートディスクリプタの作成  
マウス・キーボードデバイスのエミュレーションのためにUSB HIDデバイスの機能に応じたレポートディスクリプタ[^1]の作成が必要となる。  
簡単な3ボタンマウスであれば、インターネット上に例がいくつか見つかるのだが、「横スクロール」「指定座標へのポインタの移動」などを実現ためには自身で作成が必要となった。
* WebRTCでのブラウザへの画面表示  
WebRTCは、様々な用途を想定しているためか、とにかく仕様が複雑[^2]で、また、Webブラウザの外で実装しようとなると数千行のプログラムを自作するハメになる。  
しかし、運良く技術書典7にサークル参加されていた[でんでんらぼ](https://techbookfest.org/event/tbf07/circle/5152352327696384)さんの同人誌、[WebRTCをブラウザ外で使ってブラウザでできることを増やしてみませんか?](https://tnoho.booth.pm/items/1572872)を拝読したことで、一気に解決した。  

## マウス・キーボードエミュレーション
### WebSocketを用いたNode.jsアプリ
ブラウザへのマウス・キーボード入力をRaspberry Piで受け取るためのNode.jsアプリケーションを自作した。  
[roy-n-roy/raspi_web_console - GitHub](https://github.com/roy-n-roy/raspi_web_console)  

Socket.ioとExpressを用いた簡単なプログラムである。  

キーボード入力については、ブラウザの[KeyboardEvent](https://developer.mozilla.org/ja/docs/Web/API/KeyboardEvent)で受け取ったキー入力をUSB HIDキーコード[^3]にマッピングした上で、エミュレーションデバイスに渡している。  

マウス入力については、ブラウザの[MouseEvent](https://developer.mozilla.org/ja/docs/Web/API/MouseEvent)で受け取ったマウスの移動量・スクロール量を後述のUSB HIDエミュレーションデバイスにそのまま渡している。  

しかし、これでは**「ブラウザ上のマウスポインタの位置」と「接続先PC上のマウスポインタの位置」にズレが生じて**しまう。  
よって、絶対位置指定でポインタの位置を修正する必要がある。  

そのため、マウスとデジタイザ(ペンタブレットの様な機器)を合体させたデバイスをエミュレーションし、
ブラウザの外からポインタが入ってきたタイミングでモニタ上の絶対位置もエミュレーションデバイスに渡している。

また、後述のWebRTCのシグナリングサーバでもWebSocketを利用しているため、ブラウザからシグナリングサーバへのWebsocketコネクションのProxyも行っている。  

* アプリケーションのインストール

	``` bash
	# Node.jsをインストール
	curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -
	sudo apt install -y nodejs

	# アプリケーションのダウンロードとインストール
	curl -L -O https://github.com/roy-n-roy/raspi_web_console/archive/master.zip
	unzip raspi_web_console-master.zip
	cd raspi_web_console-master
	sudo bash ./setup.sh
	```

### USB On-the-Go機能を用いたUSBマウス・キーボードのエミュレーション
USB On-the-Go機能を利用するために、Raspbian(Linux)の起動時設定を変更する。

1. 起動パラメータにLinux Device Tree Overlay "dwc2" USBコントローラドライバを設定  

	``` bash
	echo "dtoverlay=dwc2" >> /boot/config.txt
	```

1. 起動時にLinuxカーネルモジュール "dwc2" と "libcomposite"[^4] を読み込むよう設定  

	``` bash
	echo "dwc2" >> /etc/modules
	echo "libcomposite" >> /etc/modules
	```

1. libcomposite でUSBデバイスをエミュレーションするための設定  
	デバイスディスクリプタ/コンフィグディスクリプタ/レポートディスクリプタと呼ばれる情報を設定する。  

	下記のスクリプトで設定すると、`/dev/hidg0`(キーボードエミュレータ), `/dev/hidg1`(マウス・デジタイザエミュレータ)というデバイスファイルが生えてくる。  
	これらのデバイスファイルに、後述の構造のデータを書き込むと、接続先のPCでキーボードやマウスとして動作する。  

	なお、デジタイザデバイスとはペンタブレットなどの様なカーソルの位置入力デバイスのことを指す。  

	!!! example "init_usb.sh"
		``` bash
		mkdir -p /sys/kernel/config/usb_gadget/gadget
		cd /sys/kernel/config/usb_gadget/gadget

		### Device Descriptorの設定
		# VendorID
		echo 0x1d6b > idVendor # Linux Foundation
		# USB HID Specification Release
		echo 0x0200 > bcdUSB # USB2
		# USB Class code
		echo 0xEF > bDeviceClass # Miscellaneous Device Class
		# USB SubClass code
		echo 0x02 > bDeviceSubClass # Common
		# USB Protocol code
		echo 0x01 > bDeviceProtocol # Interface Association Descriptor

		# ProductID (assigned by manufacturer)
		echo 0x0001 > idProduct
		# Device release number(assigned by manufacturer)
		echo 0x0100 > bcdDevice # v1.0.0

		# language code: 0x409=ENGLISH_US
		mkdir -p strings/0x409
		echo "fedcba9876543210" > strings/0x409/serialnumber # 適当に設定
		echo "Raspberry Pi" > strings/0x409/manufacturer
		echo "Generic USB Composite Device" > strings/0x409/product

		### Configuration Descriptorの設定
		mkdir -p configs/c.1/strings/0x409
		echo 1500 > configs/c.1/MaxPower # 1500*2mA= 3.0A
		echo "Config 1: ECM network" > configs/c.1/strings/0x409/configuration

		### Report Descriptor定義
		# Keyboard Report Descriptor
		# (Modifier keys + 6 simultaneous Keys -> 8 Bytes)
		KEYBD_REPT=""
		KEYBD_REPT+="0501"      # USAGE_PAGE (Generic Desktop)
		KEYBD_REPT+="0906"      # USAGE (Keyboard)
		KEYBD_REPT+="A101"      # COLLECTION (Application)
		KEYBD_REPT+="0507"      #   USAGE_PAGE (Keyboard)
		KEYBD_REPT+="19E0"      #   USAGE_MINIMUM (Keyboard LeftControl)
		KEYBD_REPT+="29E7"      #   USAGE_MAXIMUM (Keyboard Right GUI)
		KEYBD_REPT+="1500"      #   LOGICAL_MINIMUM (0)
		KEYBD_REPT+="2501"      #   LOGICAL_MAXIMUM (1)
		KEYBD_REPT+="7501"      #   REPORT_SIZE (1)
		KEYBD_REPT+="9508"      #   REPORT_COUNT (8)
		KEYBD_REPT+="8102"      #   INPUT (Data,Var,Abs)
		KEYBD_REPT+="7508"      #   REPORT_SIZE (8)
		KEYBD_REPT+="9501"      #   REPORT_COUNT (1)
		KEYBD_REPT+="8103"      #   INPUT (Cnst,Var,Abs)
		KEYBD_REPT+="1900"      #   USAGE_MINIMUM (Reserved (no event indicated))
		KEYBD_REPT+="299F"      #   USAGE_MAXIMUM (Keyboard Separator)
		KEYBD_REPT+="1500"      #   LOGICAL_MINIMUM (0)
		KEYBD_REPT+="259F"      #   LOGICAL_MAXIMUM (175)
		KEYBD_REPT+="7508"      #   REPORT_SIZE (8)
		KEYBD_REPT+="9506"      #   REPORT_COUNT (6)
		KEYBD_REPT+="8100"      #   INPUT (Data,Ary,Abs)
		KEYBD_REPT+="0508"      #   USAGE_PAGE (LEDs)
		KEYBD_REPT+="1901"      #   USAGE_MINIMUM (Num Lock)
		KEYBD_REPT+="2905"      #   USAGE_MAXIMUM (Kana)
		KEYBD_REPT+="1500"      #   LOGICAL_MINIMUM (0)
		KEYBD_REPT+="2501"      #   LOGICAL_MAXIMUM (1)
		KEYBD_REPT+="7501"      #   REPORT_SIZE (1)
		KEYBD_REPT+="9505"      #   REPORT_COUNT (5)
		KEYBD_REPT+="9102"      #   OUTPUT (Data,Var,Abs)
		KEYBD_REPT+="7503"      #   REPORT_SIZE (3)
		KEYBD_REPT+="9501"      #   REPORT_COUNT (1)
		KEYBD_REPT+="9103"      #   OUTPUT (Cnst,Var,Abs)
		KEYBD_REPT+="C0"        # END_COLLECTION

		# Mouse and Digitizer Report Descriptor
		#  (report_id=1, 5 Buttons, X, Y, Wheel, AC Pan -> 1byte + 1byte + 4*2 Bytes)
		#  (report_id=2, 5 Buttons, X, Y, padding*2     -> 1byte + 1byte + 4*2 Bytes)
		MOUSE_REPT=""
		# マウス部分
		MOUSE_REPT+="0501"      # USAGE_PAGE (Generic Desktop)
		MOUSE_REPT+="0902"      # USAGE (Mouse)
		MOUSE_REPT+="A101"      # COLLECTION (Application)
		MOUSE_REPT+="0901"      #   USAGE (Pointer)
		MOUSE_REPT+="A100"      #   COLLECTION (Physical)
		MOUSE_REPT+="8501"      #     REPORT_ID (1)
		MOUSE_REPT+="0509"      #     USAGE_PAGE (Button)
		MOUSE_REPT+="1901"      #     USAGE_MINIMUM (Button 1)
		MOUSE_REPT+="2905"      #     USAGE_MAXIMUM (Button 5)
		MOUSE_REPT+="1500"      #     LOGICAL_MINIMUM (0)
		MOUSE_REPT+="2501"      #     LOGICAL_MAXIMUM (1)
		MOUSE_REPT+="7501"      #     REPORT_SIZE (1)
		MOUSE_REPT+="9505"      #     REPORT_COUNT (5)
		MOUSE_REPT+="8102"      #     INPUT (Data,Var,Abs)
		MOUSE_REPT+="7503"      #     REPORT_SIZE (3)
		MOUSE_REPT+="9501"      #     REPORT_COUNT (1)
		MOUSE_REPT+="8101"      #     INPUT (Cnst,Ary,Abs)
		MOUSE_REPT+="0501"      #     USAGE_PAGE (Generic Desktop)
		MOUSE_REPT+="0930"      #     USAGE (X)
		MOUSE_REPT+="0931"      #     USAGE (Y)
		MOUSE_REPT+="0938"      #     USAGE (Wheel)
		MOUSE_REPT+="160180"    #     LOGICAL_MINIMUM (-32767)
		MOUSE_REPT+="26FF7F"    #     LOGICAL_MAXIMUM (32767)
		MOUSE_REPT+="7510"      #     REPORT_SIZE (16)
		MOUSE_REPT+="9503"      #     REPORT_COUNT (3)
		MOUSE_REPT+="8106"      #     INPUT (Data,Var,Rel)
		MOUSE_REPT+="050C"      #     USAGE_PAGE (Consumer Devices)
		MOUSE_REPT+="0A3802"    #     USAGE (AC Pan)
		MOUSE_REPT+="160180"    #     LOGICAL_MINIMUM (-32767)
		MOUSE_REPT+="26FF7F"    #     LOGICAL_MAXIMUM (32767)
		MOUSE_REPT+="7510"      #     REPORT_SIZE (16)
		MOUSE_REPT+="9501"      #     REPORT_COUNT (1)
		MOUSE_REPT+="8106"      #     INPUT (Data,Var,Rel)
		MOUSE_REPT+="C0"        #   END_COLLECTION
		MOUSE_REPT+="C0"        # END_COLLECTION
		# デジタイザ部分
		MOUSE_REPT+="050D"      # USAGE_PAGE (Digitizers)
		MOUSE_REPT+="0902"      # USAGE (Pen)
		MOUSE_REPT+="A101"      # COLLECTION (Application)
		MOUSE_REPT+="8502"      #   REPORT_ID (2)
		MOUSE_REPT+="0920"      #   USAGE (Stylus)
		MOUSE_REPT+="A100"      #   COLLECTION (Physical)
		MOUSE_REPT+="1500"      #     LOGICAL_MINIMUM (0)
		MOUSE_REPT+="2501"      #     LOGICAL_MAXIMUM (1)
		MOUSE_REPT+="0942"      #     USAGE (Tip Switch)
		MOUSE_REPT+="0944"      #     USAGE (Barrel Switch)
		MOUSE_REPT+="093C"      #     USAGE (Invert)
		MOUSE_REPT+="0945"      #     USAGE (Eraser Switch)
		MOUSE_REPT+="0932"      #     USAGE (In Range)
		MOUSE_REPT+="7501"      #     REPORT_SIZE (1)
		MOUSE_REPT+="9505"      #     REPORT_COUNT (5)
		MOUSE_REPT+="8102"      #     INPUT (Data,Var,Abs)
		MOUSE_REPT+="7503"      #     REPORT_SIZE (3)
		MOUSE_REPT+="9501"      #     REPORT_COUNT (1)
		MOUSE_REPT+="8101"      #     INPUT (Cnst,Ary,Abs)
		MOUSE_REPT+="0501"      #     USAGE_PAGE (Generic Desktop)
		MOUSE_REPT+="7510"      #     REPORT_SIZE (16)
		MOUSE_REPT+="9501"      #     REPORT_COUNT (1)
		MOUSE_REPT+="5500"      #     UNIT_EXPONENT (0)
		MOUSE_REPT+="6513"      #     UNIT (Inch,EngLinear)
		MOUSE_REPT+="3500"      #     PHYSICAL_MINIMUM (0)
		MOUSE_REPT+="1500"      #     LOGICAL_MINIMUM (0)
		MOUSE_REPT+="0930"      #     USAGE (X)
		MOUSE_REPT+="460005"    #     PHYSICAL_MAXIMUM (1280)
		MOUSE_REPT+="260005"    #     LOGICAL_MAXIMUM (1280)
		MOUSE_REPT+="8102"      #     INPUT (Data,Var,Abs)
		MOUSE_REPT+="0931"      #     USAGE (Y)
		MOUSE_REPT+="46D002"    #     PHYSICAL_MAXIMUM (720)
		MOUSE_REPT+="26D002"    #     LOGICAL_MAXIMUM (720)
		MOUSE_REPT+="8102"      #     INPUT (Data,Var,Abs)
		MOUSE_REPT+="7520"      #     REPORT_SIZE (32)
		MOUSE_REPT+="8101"      #     INPUT (Cnst,Ary,Abs)
		MOUSE_REPT+="C0"        #   END_COLLECTION
		MOUSE_REPT+="C0"        # END_COLLECTION

		if [ -n ""$(cat UDC)"" ]; then echo > UDC; fi

		### Report Descriptorの設定
		# Keyboard
		N="usb0"
		if [ -L configs/c.1/hid.$N ]; then rm configs/c.1/hid.$N; fi
		mkdir -p functions/hid.$N
		echo 1 > functions/hid.$N/subclass # Boot Device
		echo 1 > functions/hid.$N/protocol # Keyboard
		echo 8 > functions/hid.$N/report_length # Report length: 8bytes
		echo $KEYBD_REPT | xxd -r -ps > functions/hid.$N/report_desc
		ln -s functions/hid.$N configs/c.1/

		# Mouse
		N="usb1"
		if [ -L configs/c.1/hid.$N ]; then rm configs/c.1/hid.$N; fi
		mkdir -p functions/hid.$N
		echo 0 > functions/hid.$N/subclass # No Subclass
		echo 0 > functions/hid.$N/protocol # None
		echo 10 > functions/hid.$N/report_length  # Report length: 10bytes
		echo $MOUSE_REPT | xxd -r -ps > functions/hid.$N/report_desc
		ln -s functions/hid.$N configs/c.1/

		ls /sys/class/udc > UDC
		```

	* キーボード入力のデータ構造  
		キーボードデバイス `/dev/hidg0` に入力する。  

		| bytes\bit | 7&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;6&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;5&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;4&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0 |
		| :-------: | :--------------: |
		| 0バイト目  | 右Win&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;右Alt&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;右Shift&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;右Ctrl&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;左Win&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;左Alt&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;左Shift&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;左Ctrl |
		| 1バイト目  | (Zero Padding)  |
		| 2バイト目  | 1番目に押下したキーコード |
		| 3バイト目  | 2番目に押下したキーコード |
		| 4バイト目  | 3番目に押下したキーコード |
		| 5バイト目  | 4番目に押下したキーコード |
		| 6バイト目  | 5番目に押下したキーコード |
		| 7バイト目  | 6番目に押下したキーコード |

	* マウス入力のデータ構造  
		マウス/デジタイザデバイス `/dev/hidg1` に入力する。  
		マウスとして使用する場合は、0バイト目にレポートID = 0x01 を指定する。  

		後述のデジタイザ入力も同様だが、各数値は範囲 -32,767 ～ 32,767 の2バイト数値(signed int16)で入力する。  

		| bytes\bit | 7&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;6&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;5&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;4&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0 |
		| :-------: | :--------------: |
		| 0バイト目  | Report ID = 0x01 |
		| 1バイト目  | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(5 bits Zero Padding)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Button3&nbsp;&nbsp;Button2&nbsp;&nbsp;Button1 |
		| 2バイト目  | カーソル 横方向 移動量 (下位バイト) |
		| 3バイト目  | カーソル 横方向 移動量 (上位バイト) |
		| 4バイト目  | カーソル 縦方向 移動量 (下位バイト) |
		| 5バイト目  | カーソル 縦方向 移動量 (上位バイト) |
		| 6バイト目  | スクロール 縦方向 移動量 (下位バイト) |
		| 7バイト目  | スクロール 縦方向 移動量 (上位バイト) |
		| 8バイト目  | スクロール 縦方向 移動量 (下位バイト) |
		| 9バイト目  | スクロール 縦方向 移動量 (上位バイト) |

	* デジタイザ入力のデータ構造  
		マウス/デジタイザデバイス `/dev/hidg1` に入力する。  
		デジタイザとして使用する場合は、0バイト目にレポートID = 0x02 を指定する。  

		| bytes\bit | 7&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;6&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;5&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;4&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;0 |
		| :-------: | :--------------: |
		| 0バイト目  | Report ID = 0x02 |
		| 1バイト目  | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(3 bits Zero Padding)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;InRange&nbsp;&nbsp;EraserSw&nbsp;&nbsp;&nbsp;Invert&nbsp;&nbsp;&nbsp;BarrelSw&nbsp;&nbsp;&nbsp;TipSw |
		| 2バイト目  | カーソル 横方向 絶対位置 (下位バイト) |
		| 3バイト目  | カーソル 横方向 絶対位置 (上位バイト) |
		| 4バイト目  | カーソル 縦方向 絶対位置 (下位バイト) |
		| 5バイト目  | カーソル 縦方向 絶対位置 (上位バイト) |
		| 6バイト目  | (Zero Padding)  |
		| 7バイト目  | (Zero Padding)  |
		| 8バイト目  | (Zero Padding)  |
		| 9バイト目  | (Zero Padding)  |

		また、1バイト目は(今回の用途では)常に下記の様に入力する。

		| bit           | 値 | 用途                                      |
		| ------------- | -- | ---------------------------------------- |
		| (Padding)     |  0 |                                          |
		| (Padding)     |  0 |                                          |
		| (Padding)     |  0 |                                          |
		| InRange       |  1 | カーソルがデジタイザ上にあることを示す       |
		| Eraser Switch |  0 | 消しゴムスイッチが押されていることを示す     |
		| Invert        |  0 | ペンの反対側の端(シャーペンの消しゴムの方)が<br>デジタイザ上にあることを示す |
		| Barrel Switch |  0 | バレルボタンが押されていることを示す        |
		| Tip Switch    |  0 | ペンがデジタイザの表面に触れていることを示す |

		絶対位置は、画面左上の座標を X=0, Y=0 とし、画面右下の座標を X=1280, Y=720 として入力する。  
		ここでの最大座標は、レポートディスクリプタ内の`USAGE (X)`, `USAGE (Y)`の直後に指定している`LOGICAL_MAXIMUM (1280)`, `LOGICAL_MAXIMUM (720)`である。  


## モニターエミュレーション
### CSI-2 to HDMIブリッジモジュールを用いたHDMI入力
CSI-2(Camera Serial Interface 2)とはMIPI(Mobile Industry Processor Interface)アライアンスによって策定された、
モバイル機器のプロセッサにカメラを接続するためのインターフェースの規格  
Raspberry Piはモバイル向けのCPUを搭載しており、CSI-2インターフェースを用いてカメラからの静止画/動画入力が利用できる。

PC等からのHDMI出力をCSI-2インターフェースに入力できるよう変換するモジュールがHDMI-CSIブリッジモジュールである。  
今回は[ドイツ Auvidea社の B101 HDMI to CSI-2 Bridge (15 pin FPC)](https://auvidea.eu/b101-hdmi-to-csi-2-bridge-15-pin-fpc/)を使用した。  
モジュールを接続した状態の図が[こちら](#_3)。  

Raspberry PiでCSI-2インターフェースを利用するには、`raspi-config`での有効化が必要である。  
```
sudo raspi-config
```

`raspi-config`を実行すると対話形式での入力画面が表示されるので、  
```
"5 Interfacing Options" ->
"P1 Camera" "Enable/Disable connection to the Raspberry Pi Camera"
```
と順に選択してCSI-2インターフェースを有効化する。


### Webブラウザへの動画ストリーミング配信
2019/10 現在、Webブラウザへの動画ストリーミング配信には、HLSとWebRTCを用いた方法の2種類がある。  
結果的に、今回はリアルタイム性を重視して、WebRTCを使用することにした。  

また、WebRTCにはシグナリングサーバ/ICEサーバと呼ばれるサーバが必要であるため、それらについてもRaspberry Pi上に構築した。  

#### WebRTC ストリーミング配信
ストリーミング配信には、時雨同社の[WebRTC Native Client Momo](https://github.com/shiguredo/momo)を利用した。  
Momo は libwebrtc を利用しブラウザなしで様々な環境で動作する WebRTC ネイティブクライアントであり、時雨堂社によりメンテナンスされ、Raspbian Buster, Ubuntu, MacOS用バイナリが提供されている。  
今回は、[GithubのReleaseページ](https://github.com/shiguredo/momo/releases/latest)よりバイナリをダウンロードし、インストールした。

``` bash
curl -L -O https://github.com/shiguredo/momo/releases/download/19.09.2/momo-19.09.2_raspbian-buster_armv7.tar.gz
tar xf momo-19.09.2_raspbian-buster_armv7.tar.gz
sudo cp momo-19.09.2_raspbian-buster_armv7/momo /usr/local/bin/.
chmod +x /usr/local/bin/momo
```

#### シグナリングサーバ
こちらも、時雨堂社の[WebRTC向けシグナリングサーバ Ayame](https://github.com/OpenAyame/ayame)と、[Ayame Web SDK](https://github.com/OpenAyame/ayame-web-sdk)ライブラリを利用した。  

AyameについてはArm用バイナリが配布されてないため、
[GithubのReleaseページ](https://github.com/OpenAyame/ayame/releases/latest)からソースコードをダウンロード自身でクロスコンパイルした。
Go言語で書かれているため、クロスコンパイルは容易である。これはPC上のLinuxから行う。

``` bash
curl -L -O https://github.com/OpenAyame/ayame/archive/19.08.0.tar.gz
tar xf ayame-19.08.0.tar.gz
cd ayame-19.08.0
GO111MODULE=on GOOS=linux GOARCH=arm GOARM=7 go build -ldflags '-s -w -X main.AyameVersion=${VERSION}' -o ayame
```

生成された`ayame`バイナリと設定ファイルをRaspberryPiへ転送し、momoと同様に`/usr/local/bin`にインストールする。

``` bash
scp -p ayame config.yaml pi@raspberrypi.local:~/.
ssh pi@raspberrypi.local "sudo cp ~pi/ayame /usr/local/bin/."
ssh pi@raspberrypi.local "sudo mkdir -p /usr/local/etc/ayame && sudo cp ~pi/config.yaml /usr/local/etc/ayame/."
```

#### ICEサーバ
ICEサーバとはWebRTCにおいて、Peer-to-peer通信を確立するために、NAT越えなどを実現するための情報を提供するサーバである。
今回はローカルネットワーク上で通信するため、ICEサーバについては必要ないが、とりあえずインストールしてみる。  

ICEサーバについてはcoTurnというOSSを利用する。Raspbianのリポジトリからインストールする。

``` bash
sudo apt install coturn
```

## Systemdサービス設定
USB On-the-Goの設定スクリプト `usb_init.sh`と、Momo、Ayameの自動起動設定を行う。  

``` bash
sudo mkdir -p /usr/local/etc/default/

sudo vi /etc/systemd/system/usb_init.service
sudo vi /etc/systemd/system/momo.service
sudo vi /usr/local/etc/default/momo
sudo vi /etc/systemd/system/ayame.service
```

!!! example "usb_init.service"
	```
	[Unit]
	Description=Initialize USB Composite settings
	Before=network-pre.target

	[Service]
	Type=oneshot
	RemainAfterExit=yes
	ExecStart=/usr/local/bin/init_usb.sh

	[Install]
	WantedBy=multi-user.target
	```

!!! example "momo.service"
	```
	[Unit]
	Description=WebRTC Native Client Momo

	[Service]
	Type=simple
	WorkingDirectory=/var/log
	EnvironmentFile=/usr/local/etc/default/momo
	ExecStart=/usr/local/bin/momo --no-audio --video-device $VIDEO_DEVICE $OPTIONS ayame $AYAME_URL $ROOM_ID
	Restart=always

	[Install]
	WantedBy=multi-user.target
	```

!!! example "/usr/local/etc/default/momo"
	```
	VIDEO_DEVICE=/dev/video0
	AYAME_URL=ws://localhost:3000/signaling
	ROOM_ID=web_console
	OPTIONS=--force-i420 --use-native --resolution HD --fixed-resolution
	```

!!! example "ayame.service"
	```
	[Unit]
	Description=WebRTC Signaling Server Ayame

	[Service]
	Type=simple
	WorkingDirectory=/usr/local/etc/ayame
	ExecStart=/usr/local/bin/ayame
	Restart=always

	[Install]
	WantedBy=multi-user.target
	```

``` bash
sudo systemctl daemon-reload
sudo systemctl enable usb_init
sudo systemctl enable momo
sudo systemctl enable ayame

sudo reboot
```


<br><br><br><br>
# メモ書き
以降は、ブラウザへの動画配信を実現するWebRTCとHLSについて、調べたことを下記にメモ書き程度に残しておく。  

## Web Real-Time Communication(WebRTC)
Google社によって開発された、ウェブブラウザやモバイルアプリケーションにシンプルなAPI経由でリアルタイム通信を提供する自由かつオープンソースのプロジェクトである。  

ウェブページ内で直接のピア・ツー・ピア通信によって、プラグインのインストールやネイティブアプリのダウンロードをせずに、  
ウェブブラウザ間のボイスチャット、ビデオチャット、ファイル共有が可能になる。  
[- Wikipedia「WebRTC」より引用](https://ja.wikipedia.org/wiki/WebRTC)

Peer-to-peer通信である点が特徴。  
**動画配信のためのプトロコルではなく** ブラウザを用いたリアルタイム通信のための技術である。  

#### 配信方法
Webブラウザ上からWebカメラやモニター共有の動画などを配信することができる。
また、ベースがPeer-to-Peer通信のため、接続先情報の交換やNAT超えなどの仕組みが用意されている。  
javascriptでHTML5のvideoタグのソースオブジェクトにストリーミング配信動画を設定することで、ブラウザ上に表示する。  
HLSと比較すると遅延の少ないリアルタイム配信が可能。

!!! note
	下記の記事を参考にした。  
	[WebRTC スタックコトハジメ](https://gist.github.com/voluntas/6fcece7f424607c957d5)  
	[詳解 WebRTC](https://gist.github.com/voluntas/a9dc017ea85aea5ffb7db73af5c6b4f9)  
	[WebRTCにて(S)RTCPが必要な理由 - iwashi.co](http://iwashi.co/2014/12/12/why-do-we-need-rtcp-in-webrtc)  

## HTTP Live Streaming(HLS)
Apple社によって開発された、動画を配信するためのプロトコル。  
MP4(H.264, AAC)ファイルを分割したものと、マスターファイル、インデックスファイルと呼ばれるファイル(拡張子: .m3u8)を用いる。  

#### 配信方法
分割したファイル群をWebサーバに配置し、HTML5のvideoタグを用いて配信ができる。  

#### 詳細解説
!!! note
	HLSについては下記の記事が詳しかった。  
	[動画配信技術 その1 - HTTP Live Streaming(HLS) - Akamai Japan Blog](https://blogs.akamai.com/jp/2013/02/-1---http-live-streaminghls.html)

動画の分割と配置が必要なため、リアルタイム配信ではある程度の遅延が発生する。  

ffmpeg等で、ファイルの分割とインデックスファイルを作成可能。  

!!! example
	input.mp4からoutput.m3u8というインデックスファイルと  
	output001.ts, output002.tsといった分割されたmpeg2-tsファイルに変換する。  

	$ `ffmpeg -i input.mp4 -c:v libx264 -c:a libfdk_aac -f hls -hls_time 5 -movflags faststart -hls_playlist_type vod -hls_segment_filename "output%3d.ts" output.m3u8`

[^1]: HIDデバイスでは"レポート"と呼ばれる単位でデータをやりとりする。レポートの形式を定めたものがレポートディスクリプタである。
[^2]: [WebRTC 1.0: Real-time Communication Between Browsers](https://w3c.github.io/webrtc-pc/)で12000行ほど、[Media Capture and Streams]で5000行ほどの英文の仕様書となっている。
[^3]: USB HIDのキーコードについては[Human Interface Devices (HID) Information](https://www.usb.org/hid)内の"HID Usage Tables"ページ内のPDF資料に記載の、"10. Keyboard/Keypad Page (0x07) "を参照
[^4]: インターネット上には"g_hid"を用いている記述も見つかるが、Raspbian Busterでは動作しなかった。