# GitHub Actionsを利用したMkDocsの自動デプロイ

MkDocsでWebページを編集する際、下記の図のようなワークフローを採っています。  

今回は、GitHub Actionsを利用して、DkDocsでのGitHub Pagesへのページ公開を自動化しました。  

<a href="/imgs/mkdocs_github_actions_workflow.png" data-lightbox="image">
<img src="/imgs/mkdocs_github_actions_workflow.png" /></a>  

## Github Actionsを利用するには
2020年2月時点で、GitHubのユーザであれば、Github Actionsを利用でき、
Freeプランでは、2,000分/月の実行時間内であれば無料で利用できます。  

詳細については、Github Actionsのページ[^1]やヘルプ[^2]を参照するとよいでしょう。

Github Actionsを利用するには、対象のリポジトリのいずれかのブランチに
`.github/workflow/[適当なファイル名].yml` を作成して、その中にワークフローをYaml形式で定義します。  

Github Actionsのヘルプ[^1]内にリファレンスがあるので、そちらを参照して作成しましょう。  

## ワークフロー作成
今回は下記のような定義を作成しました。  

Github Actionsでは、実行環境をWindows/MacOS/Ubuntuから選択できますが、  
今回はWindows上のVSCodeで編集/MkDocsを実行しているので、デプロイ時の環境もWindowsを選択しました。  
ワークフロー内の各ステップについては、Yamlファイル内のコメントで説明しています。

<script src="https://gist-it.appspot.com/https://github.com/roy-n-roy/roy-n-roy.github.io/blob/edit/.github/workflows/mkdocs-deploy.yml?footer=minimal"></script>


[^1]:[GitHub Actionsについて - GitHubヘルプ](https://help.github.com/ja/actions/getting-started-with-github-actions/about-github-actions)
[^2]:[Actions - GitHub](https://github.co.jp/features/actions)
