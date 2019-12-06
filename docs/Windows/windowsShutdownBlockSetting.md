
# Windows10 シャットダウンブロックの設定

Window10ではOSのシャットダウン時に、終了確認ダイアログが表示されるアプリケーションなどが開いたままになっていたり、未保存のファイルを保存するか確認するダイアログが開いたままになっていると、シャットダウンをブロックして待機するようになっています。  

しかし、「シャットダウンしたつもりで寝て起きたらPCがつきっぱなしだった」といったことが度々あるため、できればそのままシャットダウンして欲しいです。  

## 特定のアプリケーションだけを終了させたい
もし、「特定のアプリケーションは終了しても良いが、ExcelやWordで未保存のファイルがある場合など、他のアプリケーションは強制終了して欲しくない。」  
といった場合は、全てのアプリケーションが強制終了させると未保存のデータが失われてしまうことになるため、それは困ります。  

そういった場合は、タスクスケジューラで下記のようなタスクを新規作成します。

* [タスクの作成]
	* [全般]タブ > [セキュリティ オプション]  
		* [ユーザがログオンしているどうかにかかわらず実行する] を選択  
		* [パスワードを保存しない] をチェック  

	<a href="/imgs/windows_shutdown_application_stop_task.png" data-lightbox="task"><img src="/imgs/windows_shutdown_application_stop_task.png" width="50%" /></a>  


	* [トリガー]タブ > [新規]  
		下記のように設定します。  

		| | |
		|-|-|
		| [タスクの開始] | イベント時 |
		| [設定] | 基本 |
		| [ログ] | Application |
		| [ソース] | Winsrv |
		| [イベント ID] | 10001 |


	* [操作]タブ > [新規]  
		下記のように設定します。  
		`[プログラム名]` の箇所は、強制終了させたいプログラムのファイル名を指定してください。
		複数を指定することも可能です。

		| | |
		|-|-|
		| [操作] | プログラムの開始 |
		| [プログラム] | powershell.exe |
		| [引数の追加] | `-Command "(Get-Process -Name @(\"[プログラム名]\")).Kill();"` |

		!!! example
			「メモ帳」と「ワードパッド」を強制終了させたい場合は  
			`-Command "(Get-Process -Name @(\"notepad\", \"wordpad\")).Kill();"`  
			と指定する。

	<a href="/imgs/windows_shutdown_application_stop_trigger.png" data-lightbox="task"><img src="/imgs/windows_shutdown_application_stop_trigger.png" width="45%" /></a>
	<a href="/imgs/windows_shutdown_application_stop_action.png" data-lightbox="task"><img src="/imgs/windows_shutdown_application_stop_action.png" width="45%" /></a>

これで、設定したアプリケーションのみをシャットダウン時に強制終了させることができます。

## すべてのアプリケーションを強制終了させたい
全てのアプリケーションを強制終了して良い場合は、グループポリシーで設定することでシャットダウンのブロック自体を無効にすることができます。  

<figure>
<a href="/imgs/windows_shutdown_block_group_policy.png" data-lightbox="group_policy"><img src="/imgs/windows_shutdown_block_group_policy.png" width="70%" /></a>
<figcaption style="font-size: smaller;">[コンピュータの構成] > [管理用テンプレート] > [システム] > [シャットダウンオプション] ><br> [シャットダウンをブロックするか取り消すアプリケーションの自動終了をオフにする] で、<br>ブロックの有効/無効を設定することができる。</figcaption>
</figure>

