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

<figure id="wireshark_connect_success" style="text-align: center;">
<a href="/imgs/windows_vpn_error_wireshark_connect_success.png" data-lightbox="wireshark_connect" data-title="VPN接続成功時のネットワークダンプ<br>IKE">
<img src="/imgs/windows_vpn_error_wireshark_connect_success.png" width="95%" /></a>
<figcaption>図 4. VPN接続成功時のネットワークダンプ
</figcaption>
</figure>
[図4](#wireshark_connect_success) に沿って、それぞれのパケットを解説したものが下記の表です。

| No.     | 種類           | パケットの解説                                                                    |
| ------- | -------------- | --------------------------------------------------------------------------------- |
| 64      | DNS問い合わせ  | DNSサーバへ、VPNサーバの名前から<br>IPアドレスを問い合わせています。              |
| 65      | DNS問い合わせ  | DNSサーバからのNo.64への応答です。                                                |
| 66, 69  | IKE SA初期交換 | お互いの使用できる暗号化方式、暗号化鍵、<br>NAT越えのための情報を送信しています。 |
| 70      | IKE SA初期交換 | VPNサーバからの66, 69への応答です。                                               |
| 71 - 82 | IKE 認証交換   | 認証情報やNAT越えの情報などを送信しています。                                     |
| 84, 85  | IKE 認証交換   | VPNサーバからの71 - 82への応答です。                                              |

<figure style="text-align: center;">
<a href="/imgs/windows_vpn_error_wireshark_connect_failure.png" data-lightbox="wireshark_connect"  data-title="VPN接続失敗時のネットワークダンプ">
<img src="/imgs/windows_vpn_error_wireshark_connect_failure.png" width="95%" /></a>
<figcaption>図 5. VPN接続失敗時のネットワークダンプ</figcaption>
</figure>
