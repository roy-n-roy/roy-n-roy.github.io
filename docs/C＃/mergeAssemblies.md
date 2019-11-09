# .Net CoreでのDLL埋め込み  

## C# 8.0 と .Net Core 3.0
2019/9にC# 8.0がリリースされました。C# 8.0ではインターフェースのデフォルト実装やswitchのパターンマッチングなどの新機能が追加されていますが、一部の機能は既存の.Net Framework4.8では対応しておらず、.Net Core 3.0/.Net Standard 2.1以降が必要となります。[^1]  
また、.Net Frameworkは4.8が最後となり、今後は.Net Coreに移っていくそうです。  

## .Net Coreと実行ファイルの展開
.Net Frameworkを利用したアプリケーションでDLLをマージした単一実行ファイル(*.exe)を作成する場合はILMergeや、Costura.Fodyといった、ツールを利用する必要がありました。  
しかし、.Net Core 3.0ではSDKの標準機能として、単一実行ファイル[^2]を生成することが出来るようになりました。  


## 発行プロファイルの作成と設定
.Net Core 3.0のプロジェクトで、DLLを埋め込んだ単一実行ファイルを生成するには、「発行プロファイル」と呼ばれる設定ファイルを使用します。
発行プロファイルは下記の手順で作成することができます。

1. 公開したい対象のプロジェクトを右クリックし「発行」を選択。
1. 発行先で「フォルダー」を選択し、「プロファイルの作成」ボタンをクリック。
1. 「発行」画面を一度閉じる。
1. 対象プロジェクトの `Properties/PublishProfiles` フォルダ内に `FolderProfile.pubxml` というファイルが作成されているので、ダブルクリックして開く。
1. `PropertyGroup`ブロック内に下記2行を設定する。
	`RuntimeIdentifier`については適宜設定する。

	```
		<RuntimeIdentifier>win10-x64</RuntimeIdentifier>
		<PublishSingleFile>true</PublishSingleFile>
	```

	<a href="/imgs/csharp_dotnet_core_binary_marge.png" data-lightbox="csharp_dotnet_core_binary_marge"><img src="/imgs/csharp_dotnet_core_binary_marge.png"></a>

1. 再度、「発行」画面を開いて`FolderProfile`右の「発行」ボタンをクリック。


以上で、発行のターゲットに設定されているフォルダに実行ファイルが作成されていますので、取り出して配布ができます。

## .Net Core 3.0 「単一実行ファイルの生成」の問題
前述の手順でDLLを埋め込んだ実行ファイル(*.exe)が生成できるのですが、ILMergeやCostura.Fodyでのファイル生成と比較して、1点問題があります。  

それは「発行の際にプラットフォームを限定する必要がある」[^3]という点です。  

.Net Framework4.5以降ではターゲットプラットフォームにAnyCpuを指定することで  
x86, x64, Itanium, ARM32 の4種類のCPUアーキテクチャ上のWindows OS上で動作させられるバイナリを生成し、Fody.Costuraなどを利用して単一実行ファイルにすることが出来ました。  

しかし、現時点の .Net Core 3.0では、x86バイナリとしてコンパイルするしか、単一実行ファイルで発行する方法はなさそうです。[^4]  
x86バイナリの場合ユーザメモリ空間サイズの制限などがありますが、大量のメモリ空間が必要な場面であればARMを対象から外してx64を対象としておけば良いと思うので、個人的にはそこまで問題にはならないのかなと思います[^5]。

なお .Net Core 3.0ではWindows-Itaniumのサポートは削除されています[^6]。

また、 .Net Core 3.0では、OSの垣根を越えて Mac OS X-x64, Linux-x64, Linux-ARM32, Linux-ARM64 がサポートされるようになりました。  
しかし、WPFなどを利用するGUIアプリケーションやネイティブライブラリを参照しているアプリは、Windows以外では動作しないため、フロントエンド辺りはXamarinなどを駆使してOS毎にやっていく感じなんだと思います。  

[^1]: [C# 8.0 の新機能 - C# によるプログラミング入門 | ++C++; // 未確認飛行 C](https://ufcpp.net/study/csharp/cheatsheet/ap_ver8/)
[^2]: 単一ファイルの実行可能ファイル [.Net Core 3.0 の新機能 | Microsoft Docs](https://docs.microsoft.com/ja-jp/dotnet/core/whats-new/dotnet-core-3-0#single-file-executables)
[^3]: この点については、Costura.FodyのGitHub上でも指摘されています。 [Sunset/Obsolete Costura?  Issue #442 - Fody/Costura](https://github.com/Fody/Costura/issues/442)
[^4]: Win-x86実行ファイルはWindows on ARMでもバイナリトランスレーションで動作させることができます
[^5]: Windows on ARMがサーバ用途にも進出してくると話は変わってきますが…
[^6]: [.NET Core 3.0 - Supported OS versions - dotnet/core](https://github.com/dotnet/core/blob/master/release-notes/3.0/3.0-supported-os.md)
