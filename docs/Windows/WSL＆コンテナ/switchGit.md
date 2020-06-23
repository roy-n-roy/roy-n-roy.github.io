# WSL内のgitリポジトリをWindows上で操作する

WSLでは、ホストのWindowsマシンとWSL内部で、Plan9 protocol(9p)を通してファイルを読み書きできますが、パーミッションやシンボリックリンク等のファイルシステム情報の一部は、9pを通して扱うことができません。  
そのため、WSL内に配置したgitリポジトリは、WSL内のgitコマンドで操作する必要があります。  

WSL内のgitをWindows上から実行するツールがwslgit[^1]というプロジェクトで開発されています。  
このツールを使用すると、WindowsとWSLのパスの変換した上でWSL内のgitを起動してくれます。

つまり、`\\wsl$\`から始まるWSL内に配置されたリポジトリではwslgitを使用し、
その他のCドライブ上などではGit for Windowsを使用するよう切り替えて実行すれば、
ファイルシステムの差異を気にせずにgitリポジトリを操作することができます。


[^1]: [andy-5/wslgit - GitHub](https://github.com/andy-5/wslgit)
