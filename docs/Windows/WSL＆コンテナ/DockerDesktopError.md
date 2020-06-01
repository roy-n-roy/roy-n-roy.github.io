# WSL2上のdocker-composeで認証エラー

WSL2とDocker Desktop for Windowsで、WSL Integrationを使用して
WSL内のUbuntuから`docker-compose up`を実行すると下記のようなエラーが起きました。

!!! info "docker-compose up でのエラー"

	``` python
	> docker-compose up -d
	Traceback (most recent call last):
	  File "bin/docker-compose", line 6, in <module>
	  File "compose/cli/main.py", line 72, in main
	  File "compose/cli/main.py", line 128, in perform_command
	  File "compose/cli/main.py", line 1078, in up
	  File "compose/cli/main.py", line 1074, in up
	  File "compose/project.py", line 548, in up
	  File "compose/service.py", line 351, in ensure_image_exists
	  File "compose/service.py", line 1106, in build
	  File "site-packages/docker/api/build.py", line 261, in build
	  File "site-packages/docker/api/build.py", line 308, in _set_auth_headers
	  File "site-packages/docker/auth.py", line 301, in get_all_credentials
	  File "site-packages/docker/auth.py", line 287, in _get_store_instance
	  File "site-packages/docker/credentials/store.py", line 25, in __init__
	docker.credentials.errors.InitializationError: docker-credential-desktop.exe not installed or not available in PATH
	[2598] Failed to execute script docker-compose
	```

エラーメッセージの通り、`docker-credential-desktop.exe`がPATH環境変数の中から見つからないようです。

どうやらWSL Integrationを使用している場合は、Linux側で`docker login`をしなくても、
Windows側のDocker Desktopでログインしている認証情報を使用するようです。

## 原因

bashのタブ補完で待たされるのが嫌なので、
`wsl.conf`ファイルでWindowsのPATH環境変数をUbuntuに引き継がないように設定していました。  

WindowsのPATHで設定されている`C:\Program Files\Docker\Docker\resources\bin`というフォルダに
`docker-credential-desktop.exe`があったようです。

!!! info "/etc/wsl.conf"
	```
	[interop]
	enabled=true                # WSL内からWindowsプログラムの起動をサポートする (ver1809以降)
	appendWindowsPath=false     # WSL内のPATH環境変数に、WindowsのPATH環境変数を追加する (ver1809以降)
	```

## 対応

Ubuntu上の`~/.profile`で前述のフォルダをPATH環境変数に追加すると、エラーが解消しました。

!!! info "~/.profile"

	``` bash
	echo 'export PATH="$PATH:/mnt/c/Program Files/Docker/Docker/resources/bin:/mnt/c/ProgramData/DockerDesktop/version-bin"' >> ~/.profile
	tail ~/.profile
	```
