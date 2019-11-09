# .Net CoreでのDLL埋め込み  

## C# 8.0 と .Net Core 3.0
2019/9にC# 8.0がリリースされました。C# 8.0ではインターフェースのデフォルト実装やswitchのパターンマッチングなどの新機能が追加されていますが、一部の機能は既存の.Net Framework4.8では対応しておらず、.Net Core 3.0/.Net Standard 2.1以降が必要となります。[^1]  

## .Net Coreと実行ファイルの展開
.Net Frameworkアプリケーションを公開(Publish)する際、外部ライブラリへの参照があるプログラムだと、実行ファイル(*.exe)とともにDLLファイル(*.dll)と呼ばれる動的リンクライブラリのファイル群などが配置されます。  
インストーラパッケージを利用して配布する場合は問題ないのですが、実行ファイルを単体で配布する場合、ファイル数が多いと面倒です。
そういった場合は、実行ファイルにDLLファイルを埋め込むこみ、単一の実行ファイルとして生成することで、1ファイルのみで実行出来るプログラムを生成することができます。  

.Net Frameworkを利用したアプリケーションを単一のの場合はILMergeや、Costura.Fodyといった、ツールを利用する必要がありました。
しかし、.Net Core 3.0ではSDKの標準機能として、単一実行ファイル[^2]を生成することが出来るようになりました。  


## 発行プロファイルの作成と設定
.Net Core 3.0のプロジェクトで、DLLを埋め込んだ単一実行ファイルを生成するには、「発行プロファイル」と呼ばれる設定ファイルを使用します。
発行プロファイルは下記の手順で作成することができます。

1. 公開したい対象のプロジェクトを右クリックし「発行」を選択。
1. 発行先で「フォルダー」を選択し、「プロファイルの作成」ボタンをクリック。
1. 「発行」画面を一度閉じる。
1. 対象プロジェクトの `Properties/PublishProfiles` フォルダ内に `FolderProfile.pubxml` というファイルが作成されているので、ダブルクリックして開く。
1. `PropertyGroup`ブロック内に下記2行を設定する。
	`RuntimeIdentifier`については適宜設定してください。

	```
		<RuntimeIdentifier>win10-x64</RuntimeIdentifier>
		<PublishSingleFile>true</PublishSingleFile>
	```

1. 再度、「発行」画面を開いて`FolderProfile`右の「発行」ボタンをクリック。

以上で、発行のターゲットに設定されているフォルダに実行ファイルが作成されていますので、取り出して配布ができます。

## .Net Core 3.0 「単一実行ファイルの生成」の問題
前述の手順でDLLを埋め込んだ実行ファイル(*.exe)が生成できるのですが、ILMergeやCostura.Fodyでのファイル生成と比較して、1点問題があります。  

それは「発行の際にプラットフォームを限定する必要がある」[^3]という点です。  

.Net Framework4.5以降ではターゲットプラットフォームにanycpuを指定することで、x86, x64, Itanium, ARMの4種類のCPUアーキテクチャ上のWindows OS上で動作させるバイナリを生成することが出来ました。  

.Net Core 3.0ではOSの垣根を越えて、Mac OS X-x64, Linux-x64, Linux-ARM32, Linux-ARM64がサポートされるようになりました。  

もし、.Net Core

[^1]: [C# 8.0 の新機能 - C# によるプログラミング入門 | ++C++; // 未確認飛行 C](https://ufcpp.net/study/csharp/cheatsheet/ap_ver8/)
[^2]: 単一ファイルの実行可能ファイル [.Net Core 3.0 の新機能 | Microsoft Docs](https://docs.microsoft.com/ja-jp/dotnet/core/whats-new/dotnet-core-3-0#single-file-executables)
[^3]: この点については、Costura.FodyのGitHub上でも議論されています。 [Sunset/Obsolete Costura?  Issue #442 - Fody/Costura](https://github.com/Fody/Costura/issues/442)