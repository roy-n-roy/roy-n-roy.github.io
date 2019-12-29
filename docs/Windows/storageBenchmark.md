# ストレージの速度

自宅デスクトップPC/ノートPC/サーバについて、ストレージの速度を測定したので記録しておきます。  

測定ソフト: CrystalDiskMark 7.0.0g x64 (ADMINモード)

|         機種名 | 対象ストレージ       |          接続I/F | Sequential<br>Read | Sequential<br>Write | Random<br>Read | Random Write(MB/s) | 
| -------------- | -------------------- | ---------------- | ---------- | ----------- |
| デスクトップPC | CFD CSSD-M2B1TBG3VNF | PCIe4.0 x4(NVMe) |   4991.864 |    1021.249 |
|                | INTEL SSDPE2MW400G4  | PCIe3.0 x4(NVMe) |   2312.482 |    1033.822 |
|                | Ram Disk: DDR4-3200<br>(Primo Ramdisk: Direct-IO mode) |   22784.540 |   23415.746 |
|                | NAS(おうちサーバ)    | 1Gbps Ethernet   |    116.039 |     116.368 |
| Surface GO     | TOSHIBA KBG30ZPZ128G | PCIe3.0 x4(NVMe) |   1314.798 |     125.391 |
| おうちサーバ   | 記憶域スペース[^1]   | 記事参照[^1]     |   1219.595 |     648.890 |

[^1]: [記憶域スペースの記事](/Windows/%E8%A8%98%E6%86%B6%E5%9F%9F%E3%82%B9%E3%83%9A%E3%83%BC%E3%82%B9/#_10)で構築した、記憶域海藻あり・ReFSのボリューム
