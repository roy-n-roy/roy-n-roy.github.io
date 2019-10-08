## Firewallの設定

### 日本国外からの通信の遮断
日本国内に割り当てられているIPアドレスからの通信のみを許可するよう設定する。  
また、割当てIPアドレスの更新に対応する。  

#### JPアドレスグループの作成
セットアップスクリプトをGithub Gistsからダウンロード

!!! example "setup_and_exec.sh"
	<script src="https://gist.github.com/roy-n-roy/cc49d45e0d8f35d905cbbbd3f685d4ee.js?file=setup_and_exec.sh"></script>

``` bash
curl -L -O https://gist.githubusercontent.com/roy-n-roy/cc49d45e0d8f35d905cbbbd3f685d4ee/raw/setup_and_exec.sh
```


* 下記の2行をルーターのIPアドレス、adminユーザのパスワードに書き換える

!!! note "setup_and_exec.sh"
	```
	ipAddress="192.168.XXX.XXX"
	password="Passw0rd"
	```

* 実行

``` bash
chmod +x setup_and_exec.sh
./setup_and_exec.sh
```

!!! success "Result"
	```
	% Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
									Dload  Upload   Total   Spent    Left  Speed
	100    27  100    27    0     0    519      0 --:--:-- --:--:-- --:--:--   519
	% Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
									Dload  Upload   Total   Spent    Left  Speed
	100  1210  100  1210    0     0  35588      0 --:--:-- --:--:-- --:--:-- 36666
	% Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
									Dload  Upload   Total   Spent    Left  Speed
	100   131  100   131    0     0   3742      0 --:--:-- --:--:-- --:--:--  3638
	New Vault password:                           <- ルーターのログインパスワード保管用鍵となるパスワードを入力する
	Confirm New Vault password:                   <- 同じパスワードを再入力（保管時の確認）
	Encryption successful
	Vault password:                               <- 同じパスワードを再入力（スクリプト実行）

	PLAY [localhost] *****************************************************************************************************
	TASK [Gathering Facts] ***********************************************************************************************
	ok: [localhost]

	TASK [Download IP Address List] **************************************************************************************

	(...中略...)

	skipping: [192.168.XXX.XXX] => (item=apnic|BD|asn|139622|1|20190829|allocated|A91E773E)
	skipping: [192.168.XXX.XXX] => (item=apnic|AU|asn|139623|1|20190830|allocated|A919337F)
	skipping: [192.168.XXX.XXX] => (item=apnic|IN|asn|139624|1|20190830|allocated|A9114899)
	skipping: [192.168.XXX.XXX] => (item=apnic||asn|139625|2001||available|)

	PLAY RECAP ***********************************************************************************************************
	192.168.XXX.XXX            : ok=3    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
	localhost                  : ok=2    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
	```

#### 2回目以降の実行
`ansible-playbook -i hosts set_firewalls.yml`

#### setup_and_exec.shでダウンロードされるファイル

!!! example "set_firewalls.yml"
	<script src="https://gist.github.com/roy-n-roy/cc49d45e0d8f35d905cbbbd3f685d4ee.js?file=set_firewalls.yml"></script>

!!! example "group_vars_routeros_login.yml"
	<script src="https://gist.github.com/roy-n-roy/cc49d45e0d8f35d905cbbbd3f685d4ee.js?file=group_vars_routeros_login.yml"></script>

!!! example "hosts"
	<script src="https://gist.github.com/roy-n-roy/cc49d45e0d8f35d905cbbbd3f685d4ee.js?file=hosts"></script>
