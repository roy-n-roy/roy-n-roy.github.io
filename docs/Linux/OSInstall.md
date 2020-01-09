# Linuxインストール時の作業
Linuxディストリビューションのインストール時に実施している設定作業を記載しています。  
内容は個人の見解です。  

## ディストリ共通
### タイムゾーンの設定

```
timedatectl set-timezone Asia/Tokyo
```

### SSH公開鍵認証

```
ssh <USER>@<SERVER_NAME> "mkdir ~/.ssh && chmod 700 ~/.ssh"
scp -p .ssh/id_ed25519.pub <USER>@<SERVER_NAME>:~/.ssh/.
```

### ロケール設定

```
localectl set-x11-keymap jp pc105

# JPロケールにする必要がある場合(あまりしない)
localectl set-locale LANG=ja_JP.UTF-8
```

## Ubuntu
### カーネルライブパッチの有効化

```
sudo snap install canonical-livepatch
sudo canonical-livepatch enable XXXXXXXXXXXXXXXXXXXXXX
```

### 固定IPアドレス設定

```
cat <<EOL >> /etc/netplan/90-static.yaml
network:
  ethernets:
    eth0:
      addresses:
      - 192.168.XXX.XXX/24
      gateway4: 192.168.XXX.YYY
      nameservers:
        addresses:
        - 192.168.XXX.YYY
  version: 2
EOL
```

## CentOS
### sudoers設定

```
usermod -aG wheel <USER>
```

### Vimインストール
初期ではvim-minimalしかインストールされておらず不便なため、 `vim-enhanced` をインストール

```
yum -y install vim-enhanced 
```

### 固定IPアドレス設定

```
nmcli connection modify ens0 ipv4.addresses 192.168.XXX.XXX/24
nmcli connection modify ens0 ipv4.gateway 192.168.XXX.YYY
nmcli connection modify ens0 ipv4.dns 192.168.XXX.YYY
nmcli connection modify ens0 ipv4.method manual
nmcli connection down ens0; nmcli connection up ens0
```
