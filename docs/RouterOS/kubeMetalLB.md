# RouterOSでk8sロードバランサー

GKEやAKS、EKS等のクラウドプロバイダのKubernetesクラスター上で
L4ロードバランサーを使用する場合、Kubernetes ServiceのタイプをLoadBalancerに設定すると
クラウドプロバイダが提供するGoogle Cloud Load Balancerや、Azure Load Balancerなどの
外部ロードバランサーサービスと連携して、負荷分散と可用性向上をしてくれます。

しかし、クラウドプロバイダではない、自身で構築したKubernetesクラスタでロードバランシングしたい場合は、
外部連携するロードバランサーを用意する必要があります。

今回は、RouterOSと[MetalLB][1]を使用して、
ベアメタルKubernetesクラスターでロードバランサーを利用できるようにします。

## MetalLB
[MetalLB][1][^1] は、ベアメタル環境のKubernetesでLoadBalancerタイプのServiceを使用するための実装です。
BGPまたは、ARPやNDPなどの標準的なプロトコルを使用して、Kubernetes上でロードバランサー機能を提供することができます。

![](/imgs/routeros_kube_metallb.svg)

## KubernetesのService

MetalLBをインストールする前に、KubernetesのServiceについて説明します。
今すぐMetalLBを使用したい方は、[MetalLBのインストール](#metallb_1)まで読み飛ばしてください。

Kubernetesでアプリケーションを外部へ公開する場合には、Serviceというものを利用します。

Serviceにはいくつかのタイプがあり、外部からKubernetesクラスター内部へのアクセスを提供するには
NodePortタイプもしくは、LoadBalancerタイプのServiceを使用します。[^2]

NodePortタイプのServiceでは、アプリケーションのPodが動作しているノードのIPアドレスにTCP/UDPポートが割り当てられます。  
複数のノードが存在する場合にどのノードへ割り当てられるかは、デプロイされるまで分かりません。
もし、NodePortタイプのServiceで公開する場合には、以下のような構成にする必要があります。

* シングルノードで構成する  
* デプロイするノードを事前に割り当てておく  
* 動的にDNSやDestination NATを設定する仕組みを用意する  

そのため、マルチノードで高可用性の構成にしたい場合は、あまり現実的でない選択肢になります。  


もう一方のLoadBalancerタイプのServiceでは、Kubernetesクラスターの外部にあるロードバランサーが必要になります。
通常、クラウドプロバイダーが提供でするロードバランサー機能と連携して、アプリケーションへのアクセスを提供します。

もし、マルチノード環境かつ、クラウドではなくベアメタル環境で、
アプリケーションを外部へ公開するには、LoadBalancerタイプのServiceと連携する
外部ロードバランサーにあたる機能を自身で用意する必要があります。

そこで、MetalLBは標準的なBGPルーティングやARP/NDPといったLayer2プロトコルを利用して、
市販のルーターと連携し、一般的なベアメタル環境でのロードバランシングを実現をします。

## MetalLBのインストール

MetalLB　公式サイトの[Manifestからのインストール方法](https://metallb.universe.tf/installation/#installation-by-manifest)に従って
インストールします。

!!! info "MetalLBのインストール"
    ```
    METALLB_VERSION="v0.9.3"
    kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/${METALLB_VERSION}/manifests/namespace.yaml
    kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/${METALLB_VERSION}/manifests/metallb.yaml
    # On first install only
    kubectl create secret generic -n metallb-system memberlist --from-literal=secretkey="$(openssl rand -base64 128)"
    ```

続いて、BGPで対向ルータの `192.168.5.1` と通信するよう設定を追加します。
MetalLBのAS番号は65001、対向ルータのAS番号は65000のプライベートAS番号を設定しています。

!!! info "metallb/config-map.yaml"
    ```
    apiVersion: v1
    kind: ConfigMap
    metadata:
      namespace: metallb-system
      name: config
    data:
      config: |
        peers:
        - peer-address: 192.168.5.1
          peer-asn: 65000
          my-asn: 65001
        address-pools:
        - name: default
          protocol: bgp
          avoid-buggy-ips: true
          addresses:
          - 192.168.128.0/24
    ```

上記の設定後、しばらくするとMetalLBに設定したレンジのIPアドレスが、Ingressなどに表示されるようになります。  
ここでは、すでに作成済みのアプリケーションが2つのIPアドレスに、 `192.168.128.1` が表示されています。

!!! info "IngressへのIPアドレス割り当て確認"
    ```
    > kubectl get ingress
    NAME           CLASS    HOSTS                         ADDRESS         PORTS     AGE
    api-ingress    <none>   api.roy-n-roy.test            192.168.128.1   80, 443   26d
    web-ingress    <none>   www.roy-n-roy.test            192.168.128.1   80, 443   26d
    ```


## RouterOSでのBGP設定

今度はRouterOS側で、各Kubernetesノードと通信するための設定を追加します。
対向のノードは4台で、192.168.5.250～254としています。

!!! info "BGP設定"
    ```
    /routing bgp instance
    add name=private as=65000 router-id=192.168.5.1
    /routing bgp peer
    add multihop=yes name=kube-metallb-worker1 remote-address=192.168.5.253 \
        remote-as=65001 ttl=private
    add multihop=yes name=kube-metallb-worker2 remote-address=192.168.5.252 \
        remote-as=65001 ttl=private
    add multihop=yes name=kube-metallb-worker3 remote-address=192.168.5.251 \
        remote-as=65001 ttl=private
    add multihop=yes name=kube-metallb-worker4 remote-address=192.168.5.250 \
        remote-as=65001 ttl=private
    ```


正常に設定されると、動的ルーティングが確認できるようになります。


!!! info "BGP ルーティング確認"
    ```
    # BGP広告の表示
    /routing bgp advertisements print
    PEER     PREFIX               NEXTHOP          AS-PATH                          ORIGIN     LOCAL-PREF
    kube-... 192.168.128.1/32     192.168.5.1      65001                            incomplete
    kube-... 192.168.128.1/32     192.168.5.1      65001                            incomplete
    kube-... 192.168.128.1/32     192.168.5.1      65001                            incomplete

    # ルーティングテーブルを表示
    # Kubernetes上のIngressのClusterIP(192.168.128.1/32)への動的ルーティングとして
    # 192.168.5.251と.253がDynamicで表示され、.251がActiveになっている。
    /ip route print  
    Flags: X - disabled, A - active, D - dynamic, 
    C - connect, S - static, r - rip, b - bgp, o - ospf, m - mme, 
    B - blackhole, U - unreachable, P - prohibit 
    #      DST-ADDRESS        PREF-SRC        GATEWAY            DISTANCE
    0 ADS  0.0.0.0/0                          pppoe-out1                1
      ･･･
    4 ADb  192.168.128.1/32                   192.168.5.251            20
    5  Db  192.168.128.1/32                   192.168.5.253            20
    ```

この段階で、確認のためにhostsなどへ名前解決を登録して
ブラウザからアクセスすると、Ingressで設定したサービスが表示されます。

以下の例では、2つのURLに `192.168.128.1` を設定しています。

!!! info "/etc/hosts もしくは C:\Windows\System32\drivers\etc\hosts"
    ```
    192.168.128.1       api.roy-n-roy.test
    192.168.128.1       www.roy-n-roy.test
    ```

## RouterOSにリバースNATを設定

最後に、外部へのアクセスにNATを使用している場合は、アプリケーションをインターネットに公開するために
HTTP(S)アクセスをKubernetes IngressサービスのIPアドレスへ転送する設定をします。

!!! info "リバースNAT設定"
    ```
    # ether1のPort 80,443(HTTP(S))アクセスを192.168.128.1へ転送
    /ip firewall nat add action=dst-nat chain=dstnat in-interface=ether1 protocol=tcp port=80 to-addresses=192.168.128.1
    /ip firewall nat add action=dst-nat chain=dstnat in-interface=ether1 protocol=tcp port=443 to-addresses=192.168.128.1
    ```

[^1]: [MetalLB, bare metal load-balancer for Kubernetes][1]
[^2]: [Service | Kubernetes](https://kubernetes.io/ja/docs/concepts/services-networking/service/)

[1]: https://metallb.universe.tf/
