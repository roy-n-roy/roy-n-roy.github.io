# WSLでscreenFetchを実行させる
WSLで簡単にディストリビューションの実行を確認したい。  
※この記事は、特に中身がありません。  


``` bash
> (curl.exe -s https://raw.githubusercontent.com/KittyKatt/screenFetch/master/screenfetch-dev) -join "`n" | wsl -d Ubuntu -u root
```

各ディストリビューションにデフォルトでcurlがインストールされていない場合があるため、Windows10上のcurl.exeを利用します。  
curl.exeで取得したスクリプトをWSLへパイプします。

![windows_wsl_screenfetch_ubuntu](/imgs/windows_wsl_screenfetch_ubuntu.png)
![windows_wsl_screenfetch_centos](/imgs/windows_wsl_screenfetch_centos.png)
![windows_wsl_screenfetch_fedora](/imgs/windows_wsl_screenfetch_fedora.png)
![windows_wsl_screenfetch_gentoo](/imgs/windows_wsl_screenfetch_gentoo.png)

少し、おかしいところも有りますが[^1][^2]実行できました。  
※Alpine Linuxではデフォルトでbashがインストールされていないため、実行できませんでした。

[^1]: 'Shell'がinitになっていますね。
[^2]: 何かが': numeric argument required'と言っていますね。