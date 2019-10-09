# RouterOS

## RouterOS とは
[MikroTik社](https://mikrotik.com/)の開発する低コストなネットワーク製品「RouterBoard」向けに開発されているオペレーティングシステム。  
Linuxベース  

また、PCや仮想マシンへインストールすることも可能であり、各種仮想環境向けのイメージも配布されている。  
[MikroTik Routers and Wireless - Software Download](https://mikrotik.com/download#chr)

## 機能
かなりの高機能です。  

|                      |                         |
| -------------------- | ----------------------- |
| 管理                | Web Browser/SSH/telnet/Serial console/REST API/<br>Winbox(Windowsアプリ)/MikroTikアプリ(Android/iOS) |
| IPv4ルーティング     | Static/BFD/BGP/RIPv1/RIPv2/OSPF/MME |
| IPv6ルーティング     | Static/BGP/RIPng/OSPF |
| Layer2 VPN          | VPLS            |
| Layer3 VPN          | L2TP/IPSec/PPTP |
| Firewall            | port based/tag based/address list/L7 Firewall(Regexp) |
| その他機能           | Bonding/VLAN(802.1Q)/Authentication(802.1X, RADIUS)/NAT/IP Masquerade/<br>DHCP Server/DHCP Client/DHCP Relay/SMB Server/<br>SSH Client/Scheduler/Scripting/SNMP/rsyslog... |

## ライセンス
2019/10現在、ライセンスは **買い切り制**、しかもかなりの親切価格。  
仮想環境向けイメージからインストールした場合はCHR(Cloud Hosted Router)ライセンスと呼ばれるものが適用される。  

CHRライセンスには、下記の5種類が存在する。  

| 種類                                 | 通信速度制限 | 価格  |
| ------------------------------------ | ----------- | ----- |
| Free                                 | 1Mbit/s     | 無償  |
| P1 (perpetual-1)                     | 1Gbit/s     | $45   |
| P10 (perpetual-10)                   | 10Gbit/s    | $95   |
| P-Unlimited (perpetual-unlimited)    | なし        | $250  |
| 60-day trial                         | なし        | 無償  |

ただし、「60-day trial」は、ライセンスの有効化後60日間のみ利用可能なライセンスである。  

## 対応環境/インストール方法
2019/10現在、サポートされている環境は下記の通り。

* VMWare Fusion / Workstation and ESXi 6.5
* VirtualBox
* Hyper-V
* Amazon Web Services (AWS)
* Hetzner Cloud
* Linode
* Google Compute Engine
* ProxMox

最新情報は [Manual:CHR - MikroTik Wiki](https://wiki.mikrotik.com/wiki/Manual:CHR#How_to_Install_CHR) を参照されたい。  

## その他情報
* RouterBoard User Group  
非公式ながらも、最新情報をこと細かに公開されており、  
RouterOS関連情報のキャッチアップに非常にお世話になっております。  
<a class="twitter-timeline" data-lang="ja" data-width="400" data-height="500" data-dnt="true" href="https://twitter.com/RBUG_JP?ref_src=twsrc%5Etfw">Tweets by RBUG_JP</a> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script> 
