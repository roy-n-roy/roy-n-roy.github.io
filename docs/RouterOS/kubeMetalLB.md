# RouterOSとMetalLBでk8sをBGPロードバランスする

kubernetesをベアメタルで動かす際に

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