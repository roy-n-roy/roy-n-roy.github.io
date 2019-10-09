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
| 「キーボード」「マウス」<br>エミュレーション | ブラウザからRaspberry Piへのキー・マウス入力 | WebブラウザとWebSocket                    | NodeJSを用いた<br>自作アプリ |
|                                          | Raspberry PiからPCへのキー・マウス操作再現   | USB On-the-Goを用いた<br>USBマウス・キーボードのエミュレーション | Linuxカーネルモジュール(libcomposite) |
| 「モニター」<br>エミュレーション          | PCから<br>Raspberry Piへの映像入力          | CSI-HDMIブリッジモジュールを用いたHDMI入力 | Video4Linuxドライバ |
|                                          | Raspberry Piから<br>ブラウザへの画面表示     | Webブラウザへの動画ストリーミング配信      | WebRTCクライアント "Momo" |

## 苦労した点
* 正しく動作するレポートディスクリプタの作成  
マウス・キーボードデバイスのエミュレーションのためにUSB HIDデバイスの機能に応じたレポートディスクリプタ[^1]の作成が必要となる。  
簡単な3ボタンマウスであれば、インターネット上に例がいくつか見つかるのだが、「横スクロール」「指定座標へのポインタの移動」などを実現ためには自身で作成が必要となった。
* WebRTCでのブラウザへの画面表示  
WebRTCは、様々な用途を想定しているためか、とにかく仕様が複雑[^2]で、また、Webブラウザの外で実装しようとなると数千行のプログラムを自作するハメになる。  
しかし、運良く技術書典7にサークル参加されていた[でんでんらぼ](https://techbookfest.org/event/tbf07/circle/5152352327696384)さんの同人誌、[WebRTCをブラウザ外で使ってブラウザでできることを増やしてみませんか?](https://tnoho.booth.pm/items/1572872)を拝読したことで、一気に解決した。  

### マウス・キーボードエミュレーション
#### WebSocketを用いたNodeJSブラウザアプリ
ブラウザへのマウス・キーボード入力をRaspberry Piで受け取るためのNodeJSアプリケーションを自作した。  
[roy-n-roy/raspi_web_console - GitHub](https://github.com/roy-n-roy/raspi_web_console)  

Socket.ioとExpressを用いた簡単なプログラムである。  

キーボード入力については、ブラウザの[KeyboardEvent](https://developer.mozilla.org/ja/docs/Web/API/KeyboardEvent)で受け取ったキー入力をUSB HIDキーコード[^3]にマッピングした上で、エミュレーションデバイスに渡している。  

マウス入力については、ブラウザの[MouseEvent](https://developer.mozilla.org/ja/docs/Web/API/MouseEvent)で受け取ったマウスの移動量・スクロール量を後述のUSB HIDエミュレーションデバイスにそのまま渡している。  

しかし、これでは**「ブラウザ上のマウスポインタの位置」と「接続先PC上のマウスポインタの位置」にズレが生じる**。  
そのため、絶対位置指定でポインタの位置を修正する必要がある。  
そのためマウスとデジタイザ(ペンタブレットの様な機器)を合体させたデバイスをエミュレーションし、ブラウザの外からポインタが入ってきたタイミングでモニタ上の絶対位置もエミュレーションデバイスに渡している。

また、後述のWebRTCのシグナリングサーバでもWebSocketを利用しているため、ブラウザからシグナリングサーバへのWebsocketコネクションのProxyも行っている。  

#### USB On-the-Go機能を用いたUSBマウス・キーボードのエミュレーション
USB On-the-Go機能を利用するために、Raspbian(Linux)の起動時設定を変更する。

1. 起動パラメータにLinux Device Tree Overlay "dwc2" USBコントローラドライバを設定。  

	``` bash
	echo "dtoverlay=dwc2" >> /boot/config.txt
	```

1. 起動時にLinuxカーネルモジュール "dwc2" と "libcomposite" を読み込むよう設定。  

	``` bash
	echo "dwc2" >> /etc/modules
	echo "libcomposite" >> /etc/modules
	```

1. libcomposite でUSBデバイスをエミュレーションするため、ファイルを配置

	``` bash
	mkdir -p /sys/kernel/config/usb_gadget/gadget
	cd /sys/kernel/config/usb_gadget/gadget

	### Device Descriptorの設定
	# VendorID
	echo 0x1d6b > idVendor # Linux Foundation
	# ProductID
	echo 0x0104 > idProduct # Multifunction Composite Gadget
	# USB HID Specification Release
	echo 0x0200 > bcdUSB # USB2
	# USB Class code
	echo 0xEF > bDeviceClass
	# 
	echo 0x02 > bDeviceSubClass
	# 
	echo 0x01 > bDeviceProtocol

	# Device release number(assigned by manufacturer) <- 自由に変更可
	echo 0x0100 > bcdDevice # v1.0.0

	mkdir -p strings/0x409
	echo "fedcba9876543210" > strings/0x409/serialnumber
	echo "Raspberry Pi" > strings/0x409/manufacturer
	echo "Generic USB Composite Device" > strings/0x409/product
	mkdir -p configs/c.1/strings/0x409
	echo "Config 1: ECM network" > configs/c.1/strings/0x409/configuration
	echo 1000 > configs/c.1/MaxPower
	```


### モニターエミュレーション
#### CSI-HDMIブリッジモジュールを用いたHDMI入力
CSI-2(Camera Serial Interface 2)とはMIPI(Mobile Industry Processor Interface)アライアンスによって策定された、
モバイル機器のプロセッサにカメラを接続するためのインターフェースの規格  
Raspberry Piはモバイル向けのCPUを搭載しており、CSI-2インターフェースを用いてカメラからの静止画/動画入力が利用できる。

PC等からのHDMI出力をCSI-2インターフェースに入力できるよう変換するモジュールがHDMI-CSIブリッジモジュールである。  
今回は[ドイツ Auvidea社の B101 HDMI to CSI-2 Bridge (15 pin FPC)](https://auvidea.eu/b101-hdmi-to-csi-2-bridge-15-pin-fpc/)を使用した。

Raspberry PiでCSI-2インターフェースを利用するには、`raspi-config`での有効化が必要である。  
```
sudo raspi-config
```

`raspi-config`を実行すると対話形式での入力画面が表示されるので、  
"5 Interfacing Options" ->  
"P1 Camera" "Enable/Disable connection to the Raspberry Pi Camera"  
と選択してCSI-2インターフェースを有効化する。


#### Webブラウザへの動画ストリーミング配信
2019/10 現在、Webブラウザへの動画ストリーミング配信には、HLSとWebRTCを用いた方法の2種類がある。  
結果的に、今回はリアルタイム性を重視して、WebRTCを使用することにした。  

また、WebRTCにはシグナリングサーバ/ICEサーバと呼ばれるサーバが必要であるため、それらについてもRaspberry Pi上に構築した。  

##### WebRTC ストリーミング配信
ストリーミング配信には、時雨同社の[WebRTC Native Client Momo](https://github.com/shiguredo/momo)を利用した。  
Momo は libwebrtc を利用しブラウザなしで様々な環境で動作する WebRTC ネイティブクライアントであり、時雨堂社によりメンテナンスされ、Raspbian Buster, Ubuntu, MacOS用バイナリが提供されている。
[GithubのReleaseページ](https://github.com/shiguredo/momo/releases/latest)よりバイナリをダウンロードし、インストールした。

``` bash
curl -L -O https://github.com/shiguredo/momo/releases/download/19.09.2/momo-19.09.2_raspbian-buster_armv7.tar.gz
tar xf momo-19.09.2_raspbian-buster_armv7.tar.gz
sudo cp momo-19.09.2_raspbian-buster_armv7/momo /usr/local/bin/.
chmod +x /usr/local/bin/momo
```

##### シグナリングサーバ
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

生成された`ayame`バイナリをRaspberryPiへ転送し、momoと同様に`/usr/local/bin`にインストールしておく。

``` bash
scp -p ayame pi@raspberrypi.local:~/.
ssh pi@raspberrypi.local "sudo cp ~/ayame /usr/local/bin/."
```

##### ICEサーバ
ICEサーバとはWebRTCにおいて、Peer-to-peer通信を確立するために、NAT越えなどを実現するための情報を提供するサーバである。
今回はローカルネットワーク上で通信するため、ICEサーバについては必要ないが、とりあえずインストールしてみる。  

ICEサーバについてはcoTurnというOSSを利用する。Raspbianのリポジトリからインストールする。

``` bash
sudo apt install coturn
```


## メモ書き
ブラウザへの動画配信を実現するWebRTCとHLSについて、調べたことを下記にメモ書き程度に残しておく。  

### Web Real-Time Communication(WebRTC)
Google社によって開発された、ウェブブラウザやモバイルアプリケーションにシンプルなAPI経由でリアルタイム通信を提供する自由かつオープンソースのプロジェクトである。  

ウェブページ内で直接のピア・ツー・ピア通信によって、プラグインのインストールやネイティブアプリのダウンロードをせずに、  
ウェブブラウザ間のボイスチャット、ビデオチャット、ファイル共有が可能になる。  
[- Wikipedia「WebRTC」より引用](https://ja.wikipedia.org/wiki/WebRTC)

Peer-to-peer通信である点が特徴。  
**動画配信のためのプトロコルではなく** ブラウザを用いたリアルタイム通信のための技術である。  

##### 配信方法
Webブラウザ上からWebカメラやモニター共有の動画などを配信することができる。
また、ベースがPeer-to-Peer通信のため、接続先情報の交換やNAT超えなどの仕組みが用意されている。  
javascriptでHTML5のvideoタグのソースオブジェクトにストリーミング配信動画を設定することで、ブラウザ上に表示する。  
HLSと比較すると遅延の少ないリアルタイム配信が可能。

!!! note
	下記の記事を参考にした。  
	[WebRTC スタックコトハジメ](https://gist.github.com/voluntas/6fcece7f424607c957d5)  
	[詳解 WebRTC](https://gist.github.com/voluntas/a9dc017ea85aea5ffb7db73af5c6b4f9)  
	[WebRTCにて(S)RTCPが必要な理由 - iwashi.co](http://iwashi.co/2014/12/12/why-do-we-need-rtcp-in-webrtc)  

### HTTP Live Streaming(HLS)
Apple社によって開発された、動画を配信するためのプロトコル。  
MP4(H.264, AAC)ファイルを分割したものと、マスターファイル、インデックスファイルと呼ばれるファイル(拡張子: .m3u8)を用いる。  

##### 配信方法
分割したファイル群をWebサーバに配置し、HTML5のvideoタグを用いて配信ができる。  

##### 詳細解説
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