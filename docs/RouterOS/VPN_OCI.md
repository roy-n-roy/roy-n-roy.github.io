# RouterOSとOracle Cloud Infrastractureでサイト間VPNを構築する

## OCI設定


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
add name=oci-vpn1 address=168.138.36.15/32 exchange-mode=ike2 profile=oci-ike2
add name=oci-vpn2 address=168.138.37.14/32 exchange-mode=ike2 profile=oci-ike2

# VPN接続に使用する認証情報
/ip ipsec identity
add peer=oci-vpn1 policy-template-group=oci-vpn my-id=address:165.100.177.79 remote-id=ignore auth-method=pre-shared-key secret=<OCIコンソールで確認した共有シークレット1>
add peer=oci-vpn2 policy-template-group=oci-vpn my-id=address:165.100.177.79 remote-id=ignore auth-method=pre-shared-key secret=<OCIコンソールで確認した共有シークレット2>

# IPSec適用ポリシーの設定
/ip ipsec policy
add peer=oci-vpn1,oci-vpn2 dst-address=192.168.128.0/17 src-address=192.168.0.0/17 proposal=oci-ipsec tunnel=yes

# VPNを通る場合のMSSを
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
