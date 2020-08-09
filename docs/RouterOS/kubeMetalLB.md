# RouterOSとMetalLBでk8sをBGPロードバランスする


## KubernetesのService

Kubernetesでアプリケーションを外部へ公開する場合には、Kubernetes Serviceを利用します。

Serviceにはいくつかのタイプがあり、外部からKubernetesクラスター内部へのアクセスを提供するには
LoadBalancerタイプもしくは、NodePortタイプのServiceを使用します。[^1]

NodePortタイプのServiceでは、アプリケーションのPodが動作しているノードのIPアドレスにTCP/UDPポートが割り当てられます。  
複数のノードが存在する場合、どのIPアドレスが割り当てられるかデプロイされるまで分かりません。
もし、NodePortタイプのServiceで公開する場合には、
* シングルノードで構成する
* デプロイするノードを事前に割り当てておく
* 動的にDNSやDestination NATを設定する仕組みを用意する
等が必要になるため、マルチノードで高可用性の構成にする場合には、あまり現実的でない選択肢になります。  


LoadBalancerタイプのServiceでは、Kubernetesクラスターの外部にあるクラウドプロバイダーが提供でするロードバランサーと連携して、アプリケーションへのアクセスを提供します。
そのためベアメタル環境等で使用したい場合は、MetalLB[^2]などのソフトウェアロードバランサーを使用する必要があります。

# MetalLB

![](/imgs/routeros_kube_metallb.svg)

```
peers:
- peer-address: 192.168.5.1
  peer-asn: 65000
  my-asn: 65001
address-pools:
- name: default
  protocol: bgp
  avoid-buggy-ips: true
  addresses:
  - 192.168.10.0/24
```

[^1]: [Service | Kubernetes](https://kubernetes.io/ja/docs/concepts/services-networking/service/)
[^2]: [MetalLB, bare metal load-balancer for Kubernetes](https://metallb.universe.tf/)
