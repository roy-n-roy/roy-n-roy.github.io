
## 目的
* 出先で編集しようと思っていたデータをモバイルPCに同期し忘れていた  
* 自宅PCでコミットしたソースコードをGitHubにプッシュし忘れていた  

そんな時、出先から自宅にどこからでも接続できれば、宅内ファイルサーバにはアクセス出来るし、Wake-on-Lanで自宅PCを起動してソースコードをアップロードすることもできます。  

なので、自宅へ接続できるVPNサーバを立てることにしました。

## 要件
今回のVPNの要件は、下記の3点です。

* インターネットから自宅内のネットワークへ接続できる
* クライアント端末はWindows10 PCおよびiOS12～13のiPhoneおよびiPad
* できればOSの機能のみで接続したい

## 外部からのアクセス環境
一方、昨今の国内インターネット接続環境はNTT東西のNGN光ファイバ網、auひかりの光ファイバ網、ケーブルテレビ網、4G LTE無線ネットワーク網などがあるかと思いますが、私の家ではフレッツ光を利用しています。  
フレッツ光のIPv4 PPPoE接続は夕方～夜間にかけての、いわゆるゴールデンタイム帯にプロバイダ側の網終端装置で輻輳が発生して、十分に速度が出ないといったことが起きています。  
それらの回避のため、最近のISP契約ではJPNEの提供する「v6プラス」など、MAP-EやDS-Liteといった技術を利用したIPv4 over IPv6接続(網終端装置を経由しないIPv4インターネット接続)サービスが増えてきています。  
しかしながら、これらのサービスはIPv4グローバルアドレスを複数のユーザで共有しており、任意のネットワークポートの開放が難しいものとなっています[^1][^2]。
よって、今回は宅内からのインターネット接続とは別のISP契約を用意してPPPoE接続し、サーバ公開用のインターネット接続環境を利用することにしました。

## VPN接続方式の選定
インターネットVPNの方式として、下記を検討しました。  
以前にL2TP/IPsecを利用したことがあったので、今回はIKEv2を使ってみることにしました。  

| プロトコル | Windows対応 | iOS対応 |
| ---- | ---------- | ------- |
| PPTP | 〇 | ※iOS10以降は使用不可 |
| L2TP/IPsec | 〇 | 〇 |
| MS-SSTP | 〇 | ※3rd Partyソフトが必要 |
| IKEv2 | 〇 | 〇 |
| OpenVPN | ※3rd Partyソフトが必要 | ※3rd Partyソフトが必要 |
| SoftEtherVPN | ※3rd Partyソフトが必要<br>※サーバ自体へはL2TP/IPsec,<br>MS-SSTPなどで接続可 | ※サーバ自体へは<br>L2TP/IPsecなどで接続可 |

## VPNサーバソフトウェアの選定
VPNサーバを立てるということは、外部からの入り口を作ることになりますから、セキュリティに気を遣う必要があります。
汎用OSの上でVPNサーバを動かすことも考えたのですが、その場合にはOSとVPNサーバソフトウェアのセキュリティ情報の両方を追っていく必要があり、運用が面倒だと考えました。  
また、VPNサーバにはそれ以外の仕事をさせたくなかったので、今回はMikroTik社のRouterOSを利用して構築することにしました。  

## ネットワーク設計  
下記のようなネットワーク構成としました。

![](/imgs/home_server_network.svg)

DMZ側のFirewallには下記のように設定しました。

* 宅内ネットワークからDMZへの接続および、その折り返しを許可する
* 宅内ネットワークからVPNルータへの接続を許可する
* DMZからインターネットへの接続および、その折り返しを許可し、NAT変換する
* DMZからVPNルータへのDNS問い合わせを許可する
* VPNクライアントネットワークから宅内ネットワークへの接続を一部ポートのみで許可する
* 外部からのVPN接続を指定したポートのみで許可する
* 外部からWebサーバへの接続を指定したアドレス範囲・ポートのみで許可し、NAT変換する
* その他の接続を拒否する

## VPN認証方式  
認証方式は、クライアント証明書での認証としました。

## VPNサーバ構築  
実際にRouterOSへ設定していきます。  
作業を始める前に、バックアップを取得しておきましょう。  

```
/system backup save name=YYYYMMDD-HHMM-before-vpn-setting.backup password=********
```

なお、今回はRouterOS 6.45.6で実施しています。将来のアップデートで設定方法が変更になる可能性もありますので、ご留意ください。  
詳細、また最新の情報については [Manual:IP/IPsec - MikroTik Wiki](https://wiki.mikrotik.com/wiki/Manual:IP/IPsec#Application_Examples) を確認することを強く推奨します。  

なお、ここではVPNルータのIPアドレスにドメイン名`vpn.yourdomain.com`が割り当てられているものとして進めます。  

### 独自認証局とサーバ・クライアント証明書の作成
VPNサーバ・クライアントの正真性検証や認証に使用する証明書を用意します。  
正規の認証局から購入してインポートしても良いですが、今回はRouterOS上で認証局を構築し、証明書を作成・署名します。  


1. 独自CAの構築  
	まず、VPNサーバ・クライアント認証鍵に署名するためのCAを作成します。
	```
	/certificate add common-name="VPN Root CA" name=ca key-size=2048 days-valid=3650 country=JP key-usage=key-cert-sign,crl-sign trusted=yes
	/certificate sign ca ca-crl-host=vpn.yourdomain.com
	```

1. VPNサーバ証明書の作成  
	次に、VPNサーバのサーバ証明書を作成し、CAで署名します。
	
	```
	/certificate add common-name=vpn.yourdomain.com name=server key-size=2048 days-valid=3650 country=JP subject-alt-name=DNS:vpn.yourdomain.com key-usage=digital-signature,key-encipherment,data-encipherment,ipsec-tunnel,ipsec-end-system,tls-server
	/certificate sign server ca=ca
	/certificate set server trusted=yes
	```

1. クライアント証明書の作成  
	クライアントを認証するための証明書を作成し、CAで署名します。

	```
	/certificate add common-name=user1@vpn.yourdomain.com name=client_user1 key-size=2048 days-valid=3650 country=JP subject-alt-name=email:user1@vpn.yourdomain.com key-usage=digital-signature,key-encipherment,data-encipherment,ipsec-user,ipsec-tunnel,ipsec-end-system,tls-client
	/certificate sign client_user1 ca=ca
	/certificate set client_user1 trusted=yes
	```

	!!! tip "もし、証明書が流出するなどして、失効させる場合"
		下記のコマンドで証明書を失効させることができます。

		```
		/certificate set client_user1 trusted=no
		/certificate issued-revoke client_user1
		```

1. クライアント向けに証明書をエクスポート  
	Windows/iOS用で証明書をインストールさせるため、エクスポートします。  
	このとき、必ずパスフレーズを設定するようにしてください。パスフレーズを設定しないと正しい証明書ストアにインストールされなくなります。  

	* Windows向けにはPKCS12フォーマットでエクスポートします。これにより、CAとクライアント証明書が紐付いた状態でWindowsへインポートされます。  
	* iOS向けにはCAとクライアント証明書の両方をエクスポートします。iOSはPKCS12フォーマットだとCAが紐付いた状態で上手くインポートされないそうです。  
	

	```
	# Windows向け
	/certificate export-certificate client_user1 export-passphrase=1234567890 type=pkcs12

	# iOS向け
	/certificate export-certificate ca type=pem
	/certificate export-certificate client_user1 export-passphrase=1234567890 type=pkcs12
	```

	エクスポートした証明書ファイルは、ブラウザからのダウンロード、scp,sftpでの転送するなりして、クライアントOSへ転送してください。  

### IPsec/IKEv2設定
RouterOS上でVPNサーバの設定をしていきます。  

```
# IPsec Phase1プロファイル、Phase2プロポーザルを作成
# ここでの認証アルゴリズムの組み合わせはWindowsとiOSの両方で使用できる組み合わせを設定する
/ip ipsec profile add dh-group=ecp256,modp2048,modp1536,modp1024 \
enc-algorithm=aes-256,aes-128 hash-algorithm=sha256 name=ike2

/ip ipsec proposal add auth-algorithms=sha256,sha1 \
enc-algorithms=aes-256-cbc,aes-128-cbc name=ike2 pfs-group=none

# クライアントに割り当てるIPアドレスプールを作成
/ip pool add name=ike2-pool ranges=192.168.4.2-192.168.4.254

# アドレスプールをIKEv2接続で使用するよう設定
# また、1対1接続になるよう設定
/ip ipsec mode-config add address-pool=ike2-pool \
address-prefix-length=32 name=ike2-conf split-include=0.0.0.0/0

# ポリシーグループとポリシーテンプレートを作成
/ip ipsec policy group add name=ike2-policies

/ip ipsec policy add dst-address=0.0.0.0/0 group=ike2-policies \
proposal=ike2 src-address=0.0.0.0/0 template=yes

# ピア設定を作成し、認証アルゴリズムと紐付け
/ip ipsec peer add exchange-mode=ike2 name=ike2 passive=yes profile=ike2

# クライアント認証の設定を作成
# クライアント認証方法を証明書に設定し、クライアント証明書・サーバ証明書を紐付け
# ピア設定・アドレスプール・ポリシーグループを紐付け
/ip ipsec identity add auth-method=digital-signature certificate=server \
match-by=certificate remote-certificate=client_user1 remote-id=ignore \
generate-policy=port-strict mode-config=ike2-conf notrack-chain=prerouting \
peer=ike2 policy-template-group=ike2-policies
```

以上でRouterOSでの設定は完了です。完了後にもバックアップを取っておきましょう。

```
/system backup save name=YYYYMMDD-HHMM-after-vpn-setting.backup password=********
```

### 接続確認
Windows10、iOSもしくはその両方でVPN接続できるか、確認してみます。  

#### Windows10の場合
まず、先の手順で作成した証明書をインポートします。  

証明書ファイル `client_user1.p12` をダブルクリックし、証明書のインポートウィザードを開始します。
このとき、保存場所は「ローカル コンピューター」を選んでください。  
また、途中でパスフレーズの入力を求められるので、エクスポートしたときのパスフレーズを入力してください。証明書ストアの設定はデフォルトの「証明書の種類に基づいて、自動的に証明書ストアを選択する。」で大丈夫です。  

<a href="/imgs/routeros_vpn_server_windows10_import1.png" data-lightbox="import_win"><img src="/imgs/routeros_vpn_server_windows10_import1.png" width=30% /></a>
<a href="/imgs/routeros_vpn_server_windows10_import2.png" data-lightbox="import_win"><img src="/imgs/routeros_vpn_server_windows10_import2.png" width=30% /></a>
<a href="/imgs/routeros_vpn_server_windows10_import3.png" data-lightbox="import_win"><img src="/imgs/routeros_vpn_server_windows10_import3.png" width=30% /></a>
<a href="/imgs/routeros_vpn_server_windows10_import4.png" data-lightbox="import_win"><img src="/imgs/routeros_vpn_server_windows10_import4.png" width=30% /></a>
<a href="/imgs/routeros_vpn_server_windows10_import5.png" data-lightbox="import_win"><img src="/imgs/routeros_vpn_server_windows10_import5.png" width=30% /></a>

次に、VPN接続の設定をしていきます。  

スタートボタン、もしくはWinキー+Iで設定画面を開きます。
そこから「ネットワークとインターネット」→「VPN」とたどっていき、「VPN接続を追加する」をクリックし、下記のように設定します。

| | |
|-|-|
| VPNプロバイダー | Windows(ビルドイン) |
| 接続名 | (お好みの名前を設定) |
| サーバー名またはアドレス | vpn.mydomain.com<br>(自身のVPNサーバのドメイン) |
| VPNの種類 | IKEv2 |
| サインイン情報の種類 | 証明書 |
| ユーザー名(オプション) | (空欄) |
| パスワード(オプション) | (空欄) |

<a href="/imgs/routeros_vpn_server_windows10_settings.png" data-lightbox="settings_win"><img src="/imgs/routeros_vpn_server_windows10_settings.png" width="60%" /></a>

設定完了後、VPN接続できることを確認します。  

#### iOS13の場合
まず、先の手順で作成したCA証明書をインポートします。  
`cert_export_ca.crt`ファイルを開くと、"設定" Appで確認するよう表示されるので、設定Appを開いてプロファイルをインストールします。  
インストールが完了すると、「<span style="color:LimeGreen;">検証済み ☑</span>」と表示されます。  

<a href="/imgs/routeros_vpn_server_ios13_import1.png" data-lightbox="import_ios"><img src="/imgs/routeros_vpn_server_ios13_import1.png" width=30% /></a>
<a href="/imgs/routeros_vpn_server_ios13_import2.png" data-lightbox="import_ios"><img src="/imgs/routeros_vpn_server_ios13_import2.png" width=30% /></a>
<a href="/imgs/routeros_vpn_server_ios13_import3.png" data-lightbox="import_ios"><img src="/imgs/routeros_vpn_server_ios13_import3.png" width=30% /></a>

次に`cert_export_client_user1.p12`を開き、同様にプロファイルをインストールします。  
こちらもインストール完了後、「一般」→「プロファイル」から確認すると「<span style="color:LimeGreen;">検証済み ☑</span>」と表示されます。  
<a href="/imgs/routeros_vpn_server_ios13_import4.png" data-lightbox="import_ios"><img src="/imgs/routeros_vpn_server_ios13_import4.png" width=30% /></a>
<a href="/imgs/routeros_vpn_server_ios13_import5.png" data-lightbox="import_ios"><img src="/imgs/routeros_vpn_server_ios13_import5.png" width=30% /></a>
<a href="/imgs/routeros_vpn_server_ios13_import6.png" data-lightbox="import_ios"><img src="/imgs/routeros_vpn_server_ios13_import6.png" width=30% /></a>
<a href="/imgs/routeros_vpn_server_ios13_import7.png" data-lightbox="import_ios"><img src="/imgs/routeros_vpn_server_ios13_import7.png" width=30% /></a>
<a href="/imgs/routeros_vpn_server_ios13_import8.png" data-lightbox="import_ios"><img src="/imgs/routeros_vpn_server_ios13_import8.png" width=30% /></a>
<a href="/imgs/routeros_vpn_server_ios13_import9.png" data-lightbox="import_ios"><img src="/imgs/routeros_vpn_server_ios13_import9.png" width=30% /></a>

最後に設定Appの「一般」→「VPN」と開き、「VPN構成の追加」をタップしてVPN構成を設定します。  
設定は下記の様に入力します。

<a href="/imgs/routeros_vpn_server_ios13_settings.png" data-lightbox="settings_ios"><img style="float: left;" src="/imgs/routeros_vpn_server_ios13_settings.png" width=30% /></a>

| | |
|-|-|
| タイプ | IKEv2 |
| 説明 | (お好みの名前を設定) |
| サーバ | vpn.mydomain.com<br>(自身のVPNサーバのドメイン) |
| リモートID | vpn.mydomain.com<br>(自身のVPNサーバのドメイン) |
| ローカルID | user1@vpn.mydomain.com<br>(クライアント証明書の名前) |
| ユーザ認証 | なし |
| 証明書を使用 | ON |
| 証明書 | user1@vpn.mydomain.com<br>(クライアント証明書の名前) |

<span style="clear: left;" />

設定完了後、VPN接続できることを確認します。  

[^1]: DS-LiteではISPからプライベートIPv4アドレスが割り当てられ、ISP側でNAT変換をしています。
[^2]: MAP-EではISP側から利用可能な外部ポートが割り当てられ、その範囲のみでしか外部公開することができません。
