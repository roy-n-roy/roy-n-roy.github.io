# OCIとサイト間VPNを構築

MikroTik社のルーターに搭載されているRouterOSを使用してOracle Cloud Infrastracture (OCI) と自宅のネットワークをサイト間VPNで接続します。  

![](/imgs/routeros_site-to-site_vpn_oci.svg)

## 設定仕様

以下の表の仕様で設定します。

| 項目                                                   | 設定値           |
| :----------------------------------------------------- | :--------------- |
| RouterOS のグローバルIPアドレス                        | 203.0.113.1      |
| RouterOS のプライベートネットワークアドレス            | 192.168.0.0/17   |
| OCI の仮想クラウド・ネットワークのネットワークアドレス | 192.168.128.0/17 |
| VPN接続する対象の OCI 内サブネット名                   | "Private Subnet" |

## OCIの設定

### 前提条件
* OCI上でサイト間VPN接続する対象のVCN(仮想クラウド・ネットワーク)とサブネットが作成済みであること。
* サイト間VPN接続する対象のサブネット: "Private Subnet" のOCIDを取得していること。
* OCI CLI[^2]がセットアップ済みであること。
* jqコマンド[^3]がインストール済みであること。

### OCI CLIでの設定
ここからは、OCI CLIを使用してコマンドで設定していきます。  

``` bash title="OCIでのサイト間VPN構築"
# Private Subnet のOCIDを変数に設定
subnet_id="ocid1.subnet.oc1.ap-tokyo-1.000000000000000000000000000000000000000000000000000000000000"

# 自宅ルーターに割り当てられたパブリックIPv4アドレスを設定
ip_addr="203.0.113.1"

# サブネットIDから対象のVCN OCIDとコンパートメントOCIDを取得
vcn_id=$(oci network subnet get --subnet-id $subnet_id \
		--query 'data."vcn-id"' --raw-output)
cpmt_id=$(oci network vcn get --vcn-id $vcn_id \
		--query 'data."compartment-id"' --raw-output)

# 動的ルーティング・ゲートウェイの作成
drg_id=$(oci network drg create --compartment-id $cpmt_id \
		--display-name "動的ルーティング・ゲートウェイ" --query data.id --raw-output)

# 動的ルーティング・ゲートウェイに既存のVCNへの接続を作成
oci network drg-attachment create --drg-id $drg_id --vcn-id $vcn_id \
		--display-name "VCNアタッチメント" 

# 対象サブネットのルート・テーブルIDを取得
rt_id=$(oci network subnet get --subnet-id $subnet_id \
		--query 'data."route-table-id"' --raw-output)

# ルート・テーブルの内容を取得
rt=$(oci network route-table get --rt-id $rt_id \
		--query 'data."route-rules"')

# 既存のルート・テーブルに動的ルーティングゲートウェイへの経路を追加
oci network route-table update --rt-id $rt_id --route-rules \
		$(echo $rt | jq '. |= .+[{"destination": "192.168.0.0/17",
			"networkEntityId":"'$drg_id'"}]') --force

# CPEの作成
cpe_id=$(oci network cpe create --compartment-id $cpmt_id \
		--ip-address $ip_addr --display-name "自宅ルーター" \
		--query data.id --raw-output)

# IPSec接続の作成
ipsec_id=$(oci network ip-sec-connection create \
		--compartment-id $cpmt_id --cpe-id $cpe_id --drg-id $drg_id \
		--display-name "OCI-自宅間VPN接続" --tunnel-configuration \
			'[{"displayName": "VPNトンネル1","ikeVersion": "V2","routing": "STATIC"},
			{"displayName": "VPNトンネル2","ikeVersion": "V2","routing": "STATIC"}]' \
		--cpe-local-identifier-type IP_ADDRESS --cpe-local-identifier $ip_addr \
		--static-routes '["192.168.0.0/17"]' --query data.id --raw-output)

# <OCI側IPアドレス1>の取得
oci network ip-sec-tunnel list --ipsc-id $ipsec_id --query 'data[0]."vpn-ip"' --all
# <OCI側IPアドレス2>の取得
oci network ip-sec-tunnel list --ipsc-id $ipsec_id --query 'data[1]."vpn-ip"' --all

# <共有シークレット1>の取得
oci network ip-sec-psk get --ipsc-id $ipsec_id \
		--tunnel-id $(oci network ip-sec-tunnel list --ipsc-id $ipsec_id \
		--query 'data[0].id' --raw-output --all)
# <共有シークレット2>の取得
oci network ip-sec-psk get --ipsc-id $ipsec_id \
		--tunnel-id $(oci network ip-sec-tunnel list --ipsc-id $ipsec_id \
		--query 'data[1].id' --raw-output --all)
```

ここで、最後に取得した<OCI側IPアドレス1、2>、<共有シークレット1、2>は、次のRouterOSの設定で使用するのでメモしておきます。  

## RouterOSの設定
こちらもコマンドを使用して設定していきます。  

``` bash title="RouterOSでのサイト間VPN設定"
/ip firewall filter
# IKE, ESPのポートを許可
add action=accept chain=input dst-port=500 in-interface=all-ppp protocol=udp
add action=accept chain=input in-interface=all-ppp protocol=ipsec-esp

# OCI側ネットワークとのフォワーディングを許可
add action=accept chain=forward \
		dst-address=192.168.128.0/17 in-interface=all-ethernet
add action=accept chain=forward \
		out-interface=all-ethernet src-address=192.168.128.0/17

# NAT(IPマスカレード)設定をしている場合、IPSecを通した通信もNAT変換されてしまうため
# 既存のNAT変換設定よりも先に、VPN接続先のアドレスに対してNAT変換を無効にする設定をする
/ip firewall nat
add action=accept chain=srcnat dst-address=192.168.128.0/17 place-before=0

# ポリシーグループを作成
/ip ipsec policy group
add name=oci-vpn

# フェーズ1(ISAKMP)パラメータ設定
/ip ipsec profile
add name=oci-ike2 dh-group=ecp384 dpd-interval=disable-dpd \
		enc-algorithm=aes-256 hash-algorithm=sha384 lifetime=8h nat-traversal=no

# フェーズ2(IPSec)パラメータ設定
/ip ipsec proposal
add name=oci-ipsec auth-algorithms="" \
		enc-algorithms=aes-256-gcm lifetime=1h pfs-group=modp1536

# VPN接続先設定
/ip ipsec peer
add name=oci-vpn1 address=<OCI側IPアドレス1>/32 exchange-mode=ike2 profile=oci-ike2
add name=oci-vpn2 address=<OCI側IPアドレス2>/32 exchange-mode=ike2 profile=oci-ike2

# VPN接続に使用する認証情報
/ip ipsec identity
add peer=oci-vpn1 policy-template-group=oci-vpn my-id=address:203.0.113.1 \
		remote-id=ignore auth-method=pre-shared-key secret=<共有シークレット1>
add peer=oci-vpn2 policy-template-group=oci-vpn my-id=address:203.0.113.1 \
		remote-id=ignore auth-method=pre-shared-key secret=<共有シークレット2>

# IPSec適用ポリシーの設定
/ip ipsec policy
add peer=oci-vpn1,oci-vpn2 dst-address=192.168.128.0/17 \
		src-address=192.168.0.0/17 proposal=oci-ipsec tunnel=yes

# VPNトンネルを通過する場合のMSSを設定 (1)
/ip firewall mangle
add action=change-mss chain=forward dst-address=192.168.128.0/17 new-mss=1358 \
		passthrough=yes protocol=tcp tcp-flags=syn
```

1. ここで設定する数値は、[MSSの計算](#mss)を参照

### MSSの計算
RouterOSの設定の最後でMSSを設定していますが、これを設定しない場合 1358 Byteを越えたTCPセグメントは破棄されてしまいます。  
そのため、例えばサーバへSSH接続した際に「ログインはできるがコマンドを実行すると応答の途中で切断されてしまう」といった現象が発生してしまいます。  


設定する値は下記の計算で求められますが、ここで載せているのはフレッツのPPPoE接続での例ですので、実際に設定する際にはインターネット接続方式に応じた値を計算して設定するようにしてください。

|                              |           |
| :--------------------------- | --------: |
| フレッツ PPPoE MTU           |     1454  |
| IPヘッダ                     |      -20  |
| NATトラバーサル(無し)        |      - 0  |
| ESPヘッダ                    |      - 8  |
| ESP初期化ベクトル(AES-GCM)   |      - 8  |
| ESP初期化トレーラー(AES-GCM) |      - 4  |
| ESP認証データ(SHA384)        |     - 16  |
| IPヘッダ                     |     - 20  |
| TCPヘッダ                    |     - 20  |
| IPSec MSS                    | **1358**  |


[^1]: [サポートされているIPSecパラメータ - Oracle Cloud Infrastructureドキュメント](https://docs.oracle.com/ja-jp/iaas/Content/Network/Reference/supportedIPsecparams.htm)  
[^2]: [コマンドライン・インタフェース(CLI) - Oracle Cloud Infrastructureドキュメント](https://docs.oracle.com/ja-jp/iaas/Content/API/Concepts/cliconcepts.htm)  
[^3]: [jq (https://stedolan.github.io/jq/)](https://stedolan.github.io/jq/)  
