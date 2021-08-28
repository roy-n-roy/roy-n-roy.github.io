# Setup
以下のコマンドを実行する

git worktree add release release
pushd release
git submodule init
git submodule update
popd

sudo apt update
sudo apt install python3 python3-venv python-is-python3
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -


# Docker Desktop for Windows
現行Docker engineとWSL2 based engineの違い
WSL2内からのDockerアクセス

# EPUBとPDF
EPUBとPDFの仕様について  
Kindle風 電子書籍リーダーの仕様  

# pymdownx.superfencesの移行
SuperFencesからTabbedへの移行
https://facelessuser.github.io/pymdown-extensions/extensions/superfences/