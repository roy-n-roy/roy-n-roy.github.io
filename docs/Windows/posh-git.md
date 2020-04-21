# PowerShellでGitのタブ補完を有効化する

UbuntuではaptからGitをインストールすると、デフォルトでbashでのタブ補完が有効化されます。  

しかし、WindowsではGit for Windowsをインストールしただけでは、タブ補完を利用することは出来ません。  

そこで、posh-git ([GitHub - dahlbyk/posh-git: A PowerShell environment for Git](https://github.com/dahlbyk/posh-git)) をインストールすると、Windows 10上のPowerShellでタブ補完を利用できるようになります。  

## インストール
以下のコマンドでPowerShell Galleryからposh-gitをインストールし、
PowerShellの起動時にモジュールが自動で読み込まれるように設定します。

!!! info "posh-gitのインストール"
	``` pwsh
	Install-Module -Name posh-git -AllowPrerelease
	"Import-Module posh-git" | Add-Content $PROFILE
	```

PowerShellを開き直すと、gitコマンドのタブ補完が有効化されます。

## アップデート
posh-gitを更新するには、以下のコマンドを実行します。


!!! info "posh-gitのアップデート"
	``` pwsh
	Update-Module -Name posh-git -AllowPrerelease
	```
