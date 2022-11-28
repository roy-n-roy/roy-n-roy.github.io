# RouterOSとOracle Cloud Infrastractureでサイト間VPNを構築する

## OCI設定


``` bash
# 対象のOCIコンパートメントIDを変数に設定
cpmt_id="ocid1.compartment.oc1..000000000000000000000000000000000000000000000000000000000000"
vcn_id="ocid1.vcn.oc1.ap-osaka-1.000000000000000000000000000000000000000000000000000000000000"
rt_id="ocid1.routetable.oc1.ap-osaka-1.000000000000000000000000000000000000000000000000000000000000"

# 自宅ルーターに割り当てられたパブリックIPv4アドレスを設定
ip_addr="203.0.113.1"

# 動的ルーティング・ゲートウェイの作成
drg_id=$(oci network drg create --compartment-id $cpmt_id --display-name "動的ルーティング・ゲートウェイ" --query data.id --raw-output)

# 動的ルーティング・ゲートウェイに既存のVCNへの接続を作成
oci network drg-attachment create --drg-id $drg_id --vcn-id $vcn_id --display-name "VCNアタッチメント" 

# 既存のルーティングテーブルを取得
rt=$(oci network route-table get --rt-id $rt_id | jq '.data["route-rules"]')

# 既存のルーティングテーブルに動的ルーティングゲートウェイへの経路を追加
oci network route-table update --rt-id $rt_id --route-rules $(echo $rt | jq '. |= .+[{"destination": "192.168.0.0/17","networkEntityId":"'$drg_id'"}]') --force

# CPEの作成
cpe_id=$(oci network cpe create --compartment-id $cpmt_id --ip-address $ip_addr --display-name "自宅ルーター" --query data.id --raw-output)

# IPSec接続の作成
ipsec_id=$(oci network ip-sec-connection create --compartment-id $cpmt_id --cpe-id $cpe_id --drg-id $drg_id --display-name "OCI-自宅間VPN接続" \
		--tunnel-configuration '[{"displayName": "VPNトンネル1","ikeVersion": "V2","routing": "STATIC"},{"displayName": "VPNトンネル2","ikeVersion": "V2","routing": "STATIC"}]'
		--cpe-local-identifier-type IP_ADDRESS --cpe-local-identifier $ip_addr --static-routes '["192.168.0.0/17"]' --query data.id --raw-output)

# <OCI側IPアドレス1>の取得
oci network ip-sec-tunnel list --ipsc-id $ipsec_id --query 'data[0]."vpn-ip"' --all
# <OCI側IPアドレス2>の取得
oci network ip-sec-tunnel list --ipsc-id $ipsec_id --query 'data[1]."vpn-ip"' --all

# <共有シークレット1>の取得
oci network ip-sec-psk get --ipsc-id $ipsec_id --tunnel-id $(oci network ip-sec-tunnel list --ipsc-id $ipsec_id --query 'data[0].id' --raw-output --all)
# <共有シークレット2>の取得
oci network ip-sec-psk get --ipsc-id $ipsec_id --tunnel-id $(oci network ip-sec-tunnel list --ipsc-id $ipsec_id --query 'data[1].id' --raw-output --all)
```

## RouterOS設定
``` conf
/ip firewall filter
# IKE, ESPのポートを許可
add action=accept chain=input dst-port=500 in-interface=all-ppp protocol=udp
add action=accept chain=input in-interface=all-ppp protocol=ipsec-esp

# OCI側ネットワークとのフォワーディングを許可
add action=accept chain=forward dst-address=192.168.128.0/17 in-interface=all-ethernet
add action=accept chain=forward out-interface=all-ethernet src-address=192.168.128.0/17

# NAT(IPマスカレード)設定をしている場合、IPSecを通した通信もNAT変換されてしまうため
# 既存のNAT変換設定よりも先に、VPN接続先のアドレスに対してNAT変換を無効にする設定をする
/ip firewall nat
add action=accept chain=srcnat dst-address=192.168.128.0/17 place-before=0

# ポリシーグループを作成
/ip ipsec policy group
add name=oci-vpn

# フェーズ1(ISAKMP)パラメータ設定
/ip ipsec profile
add name=oci-ike2 dh-group=ecp384 dpd-interval=disable-dpd enc-algorithm=aes-256 hash-algorithm=sha384 lifetime=8h nat-traversal=no

# フェーズ2(IPSec)パラメータ設定
/ip ipsec proposal
add name=oci-ipsec auth-algorithms="" enc-algorithms=aes-256-gcm lifetime=1h pfs-group=modp1536

# VPN接続先設定
/ip ipsec peer
add name=oci-vpn1 address=<OCI側IPアドレス1>/32 exchange-mode=ike2 profile=oci-ike2
add name=oci-vpn2 address=<OCI側IPアドレス2>/32 exchange-mode=ike2 profile=oci-ike2

# VPN接続に使用する認証情報
/ip ipsec identity
add peer=oci-vpn1 policy-template-group=oci-vpn my-id=address:203.0.113.1 remote-id=ignore auth-method=pre-shared-key secret=<共有シークレット1>
add peer=oci-vpn2 policy-template-group=oci-vpn my-id=address:203.0.113.1 remote-id=ignore auth-method=pre-shared-key secret=<共有シークレット2>

# IPSec適用ポリシーの設定
/ip ipsec policy
add peer=oci-vpn1,oci-vpn2 dst-address=192.168.128.0/17 src-address=192.168.0.0/17 proposal=oci-ipsec tunnel=yes

# VPNを通過する通る場合のMSSを設定
/ip firewall mangle
add action=change-mss chain=forward dst-address=192.168.128.0/17 new-mss=1358 passthrough=yes protocol=tcp tcp-flags=syn
```

### MSS計算

| フレッツ PPPoE MTU           |  1454  |
| IPヘッダ                     | -  20  |
| NATトラバーサル(無し)        | -   0  |
| ESPヘッダ                    | -   8  |
| ESP初期化ベクトル(AES-GCM)   | -   8  |
| ESP初期化トレーラー(AES-GCM) | -   4  |
| ESP認証データ(SHA384)        | -  16  |
| IPヘッダ                     | -  20  |
| TCPヘッダ                    | -  20  |
| IPSec MSS                    |  1358  |


[^1]: [サポートされているIPSecパラメータ - Oracle Cloud Infrastructureドキュメント](https://docs.oracle.com/ja-jp/iaas/Content/Network/Reference/supportedIPsecparams.htm)
