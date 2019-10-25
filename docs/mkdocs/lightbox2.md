
## lightbox2を使用して、画像をギャラリー表示する
Lightbox2とは、jQueryで写真ギャラリー的に良い感じに表示してくれるやつです。  
詳細は下記参照。  
[Lightbox 2 - Lokesh Dhakar](https://lokeshdhakar.com/projects/lightbox2/)

### mkdocsのリポジトリのサブモジュールとしてlithgbox2を追加する
submoduleとして追加して、docsの中からシンボリックリンクとして参照できるようにします。  

```
mkdir submodules
git submodule add -b master https://github.com/lokesh/lightbox2.git submodules/lightbox2
cd submodules/lightbox2

# 使用するバージョンを指定
git checkout v2.11.1 
cd ../../
git add submodules/lightbox2
git commit -m "Add lightbox2 v2.11.1"
cd docs

# for command prompt
git config core.symlinks true
mklink /D lightbox2 ..\submodules\lightbox2\dist

# for bash
ln -s submodules/lightbox2/dist lightbox2
```

### mkdocsの設定ファイルにlightbox2を読み込むよう設定を追加する
Visual Studio Codeで設定ファイルを開いて、下記の4行を追加します。

```
code mkdocs.yml
```

!!! example "mkdocs.yml"
	```
	extra_javascript:
		- 'lightbox2/js/lightbox-plus-jquery.min.js'
	extra_css:
		- 'lightbox2/css/lightbox.min.css'
	```

### 使用方法
lightbox2を使用するときは下記のようにhtmlのaタグで記入します。  
`data-lightbox`で指定した値が同じ場合は同一のギャラリーとして表示されます。
`data-title`で指定した値はキャプションとして表示されます。

``` html
<a href="/images/image_1.jpg" data-lightbox="image" data-title="Caption1">
	<img src="/images/thumb_1.jpg" />
</a>
<a href="/images/image_2.jpg" data-lightbox="image">
	<img src="/images/thumb_2.jpg" />
</a>
```