
## ロゴマークを作成  
今回はInkspaceを使って、下記の様なオリジナルロゴマークのSVGファイルを作成しました。  
![](/imgs/logo.svg)  

[Getting started - Material for MkDocs](https://squidfunk.github.io/mkdocs-material/getting-started/#logo) によると、最低でも128x128以上のサイズである方が良いようです。
> Your logo should have rectangular shape with a minimum resolution of 128x128, leave some room towards the edges and be composed of high contrast areas on a transparent ground, as it will be placed on the colored header bar and drawer.

## favicon.icoを作成  
まず、faviconを作成するために、InkspaceでPNGファイルにエクスポートします。この時にPNGファイルのサイズを指定することができます。  
今回は、16x16、24x24、32x32、48x48、64x64、96x96、128x128、144x144、152x152の合計9ファイルを作成しました。  

これらのファイルをマルチサイズfaviconに変換するのですが、変換方法についてはここでは割愛します。  

## mkdocs.ymlの設定  
作成したSVGファイルとfavicon.icoファイルをmkdocsのdocsフォルダ配下に配置します。  
その後、`mkdocs.yml`ファイルを編集し、下記の様に配置したファイルの相対パスを指定します。

```
theme:
  logo: 'imgs/logo.svg'
  favicon: 'favicon.ico'
```

後は、ローカル環境で左上のロゴとfaviconが変わっていることを確認、デプロイして完了です。