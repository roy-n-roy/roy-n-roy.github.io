# バッチでループバックインターフェースを作成

Windowsでループバックインターフェースを作成し、IPアドレスを設定するバッチファイルです。

ネットワークインターフェースを作成するために、Windows Driver Kitに付属する DevCon [^1] が必要なため、Microsoftのダウンロードサイトから取得の上で使用しています。


!!! example "INSTALL_LOOPBACK_INTERFACE.bat"
	<script src="https://gist.github.com/roy-n-roy/eb5e11e82e8cefa8b6a0ea72f96cedc2.js?file=INSTALL_LOOPBACK_INTERFACE.bat"></script>

[^1]: [Windows デバイス コンソール (Devcon.exe)](https://docs.microsoft.com/ja-jp/windows-hardware/drivers/devtest/devcon)
