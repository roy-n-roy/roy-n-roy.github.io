# テザリング(有線ケーブル)でのVPN接続エラー
私は、外出先から自宅へVPN接続できるように、IPsec/IKEv2の[VPNサーバの設定](/RouterOS/VPN Server)をしており、Windows PCでVPN接続するときにはiPhoneのテザリングでのインターネット経由でVPN接続をしています。  

iPhoneのテザリングを利用するには「Lightningケーブル接続」「Wi-Fi接続」「Bluetooth接続」の3通りの方法があります。
Windows PCからVPN接続をするときに「Wi-Fi接続」でのテザリング経由では正常に接続できるのですが、「Lightningケーブル」での有線接続の場合に、VPN接続がエラーとなることがありました。  

<figure style="text-align: center;">
<a href="/imgs/windows_vpn_error_wireless_success.png" data-lightbox="vpn_connect" data-title="Wi-Fi(無線LAN)テザリング経由のVPN接続の成功結果"><img src="/imgs/windows_vpn_error_wireless_success.png" width="45%" /></a>
<a href="/imgs/windows_vpn_error_wired_error.png" data-lightbox="vpn_connect" data-title="Lightningケーブル(有線)経由のVPN接続の失敗結果"><img src="/imgs/windows_vpn_error_wired_error.png" width="45%" /></a>  
<figcaption>図 1, 2. Wi-Fi(無線LAN)テザリング経由のVPN接続の成功結果 (左) と<br>
Lightningケーブル(有線)経由のVPN接続の失敗結果 (右)</figcaption>
</figure>

どちらも同じiPhoneを同じ日に、同じ場所で、同じキャリア(docomo)を使用しており、接続できない原因が分かりませんでした。  

## IPsec/IKEv2接続時の処理



## エラー原因の調査
VPN接続エラーの原因を特定するため、[Wireshark](https://www.wireshark.org/)を利用して、VPN接続時のパケットの流れを調べてみました。  

Wiresharkは64bit版のVersion 3.2.0をインストールしています。インストール時のオプションは全てデフォルトのままにしています。  
(同時にMicrosoft Visual C++ 2015-2019 再頒布可能 ランタイムと、NpCapがインストールされました。)  

Wiresharkを起動すると、PCのネットワークアダプターの一覧が表示されます。  
ここには、PCの内部で使用されている、仮想的なアダプターも表示されますが、調査のためにはVPN接続に使用しているインターネットに繋がっているアダプターを選択します。  
アダプターの名前の右には、線グラフのようなものが表示されており、これはネットワークの通信量を表しています。
アダプター名と通信量グラフを参考にして、対象のネットワークアダプターを選択してください。  

<figure style="text-align: center;">
<a href="/imgs/windows_vpn_error_wireshark_start.png" data-lightbox="wireshark_start"><img src="/imgs/windows_vpn_error_wireshark_start.png" width="95%" /></a>
<figcaption>図 3. Wiresharkを起動した画面</figcaption>
</figure>

そして、Wi-Fi経由とLightningケーブル経由でのVPN接続時のデータを取得した結果が下記の図です。
なお、下記のようなネットワークから取得したデータのことを「ネットワークダンプ」と呼びます。  

また、VPNサーバのIPアドレス部分は、画像を加工して黒色に塗りつぶしていますので、ご承知おき下さい。。  

<figure id="fig_wireshark_connect" style="text-align: center;">
<a href="/imgs/windows_vpn_error_wireshark_connect_success.png" data-lightbox="wireshark_connect" data-title="VPN接続成功時のネットワークダンプ<br>IKE">
<img src="/imgs/windows_vpn_error_wireshark_connect_success.png" width="80%" /></a>
<a href="/imgs/windows_vpn_error_wireshark_connect_failure.png" data-lightbox="wireshark_connect"  data-title="VPN接続失敗時のネットワークダンプ">
<img src="/imgs/windows_vpn_error_wireshark_connect_failure.png" width="80%" /></a>
<figcaption>図 4, 5. VPN接続成功時(上) と VPN接続失敗時(下) のネットワークダンプ</figcaption>
</figure>

まず前提として、IPsec/IKEv2接続の初期フェーズには、「IKE_SA_INIT」と「IKE_AUTH」の2つの処理があります。[^1]
これを踏まえて[図 4, 5](#fig_wireshark_connect)のIKE接続のパケットを見比べると下記のことが分かります。

* 失敗時にはVPNサーバからの「IKE_AUTH」の応答がない
* 成功時の「IKE_AUTH」の応答パケットでフラグメントが発生している

これらの事象から、下記の仮定を立てました。  
!!! question "仮定"
	<span style="font-size: x-large;">「IKE_AUTH」の応答パケットサイズがMTUを超過し、<br>パケットロスが発生しているのではないか</span>

## MTU設定の確認と変更
結果から書くと、MTUの値を変更することで「Lightningケーブル」経由のVPN接続が成功するようになりました。  

<figure style="text-align: center;">
<a href="/imgs/windows_vpn_error_wired_success.png" data-lightbox="vpn_connect_after" data-title="Lightningケーブル(有線)経由のVPN接続の成功結果"><img src="/imgs/windows_vpn_error_wired_success.png" width="30%" /></a>  
<figcaption>図 6. Lightningケーブル(有線)経由のVPN接続の成功結果</figcaption>
</figure>

以降に、MTU設定の確認と変更の手順を記載します。  

powershellプロンプトを開いて、ネットワークアダプターのMTUの確認と変更を行っていきます。

!!! example "MTU設定の確認"
	```
	netsh interface ipv4 show interface
	```

	!!! success ""
		```
		Idx     Met         MTU          状態                 名前
		---  ----------  ----------  ------------  ---------------------------
		19          25        1500  connected     イーサネット 5
		```
	⇒「イーサネット 5」MTUは、1500(デフォルト値)であることが分かる。

!!! example "最大フレームサイズの検証"
	```
	ping -f -l 1472 -n 1 www.nic.or.jp
	```

	!!! success ""
		```
		nic.or.jp [122.28.47.86]に ping を送信しています 1472 バイトのデータ:
		122.28.47.86 からの応答: バイト数 =1472 時間 =443ms TTL=47

		122.28.47.86 の ping 統計:
			パケット数: 送信 = 1、受信 = 1、損失 = 0 (0% の損失)、
		ラウンド トリップの概算時間 (ミリ秒):
			最小 = 443ms、最大 = 443ms、平均 = 443ms
		```
	```
	ping -f -l 1473 -n 1 www.nic.or.jp
	```

	!!! success ""
		```
		nic.or.jp [122.28.47.86]に ping を送信しています 1473 バイトのデータ:
		パケットの断片化が必要ですが、DF が設定されています。

		122.28.47.86 の ping 統計:
			パケット数: 送信 = 1、受信 = 0、損失 = 1 (100% の損失)、
		```
	サイズ=1473ではパケットロスが発生するが、サイズ=1472バイトでは発生していない。  
	⇒パケットロスの発生しないMTUの最大値は「1472」バイト

!!! example "MTU設定の変更"
	```
	netsh interface ipv4 set interface 19 mtu=1472
	netsh interface ipv4 show interface
	```

	!!! success ""
		```
		Idx     Met         MTU          状態                 名前
		---  ----------  ----------  ------------  ---------------------------
		19          25        1472  connected     イーサネット 5
		```
	⇒「イーサネット 5」MTUが、1472に変更されている。



<figure style="text-align: center;">
<a href="/imgs/windows_vpn_error_set_mtu.png" data-lightbox="set_mtu" data-title="Wi-Fi(無線LAN)テザリング経由のVPN接続の成功結果"><img src="/imgs/windows_vpn_error_set_mtu.png" width="95%" /></a>
<figcaption>図 7. MTUの設定確認と変更</figcaption>
</figure>

[^1]: [IKEv2 パケット交換とプロトコル レベルのデバッグ - Cisco](https://www.cisco.com/c/ja_jp/support/docs/security-vpn/ipsec-negotiation-ike-protocols/115936-understanding-ikev2-packet-exch-debug.html)