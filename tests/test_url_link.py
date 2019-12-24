import sys
import os
import subprocess
import glob
import re

from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, quote
import asyncio
import aiohttp

def test_urls():
    """
    docs配下のMarkdownファイルを対象として
    全リンクのステータスチェックする
    """

    # mkdocs serve実行時のURL
    mkdocs_url = 'http://127.0.0.1:8000/'
    
    # 並列実行数
    max_access_count = 100

    # mkdocs serveが起動しているかチェックし、起動していない場合は起動
    proc = check_and_start_mkdocs(mkdocs_url)

    # テスト対象URLのリスト
    target_urls = []
    # docs配下の*.mdファイルを検索し、対象URLリストを作成
    for md in glob.glob('release/docs/**/*.md', recursive=True):
        target_urls.append(mkdocs_url + re.sub(r'^docs\\|\.md$|index\.md$', '', md).replace(os.sep, '/'))

    check_urls = []
    errors = []
    # 成功時コールバック関数
    def extend_test_urls(future):
        check_urls.extend(future.result())

    # エラー時コールバック関数
    def set_error(result):
        errors.append(result)

    # 並列アクセス数制限用セマフォ
    sem = asyncio.Semaphore(max_access_count)

    # パース対象URLからリンクを取得
    asyncio.get_event_loop().run_until_complete(
        fetch_and_parse(target_urls, extend_test_urls, set_error, sem)
    )
    # error数が0でない場合はNG
    assert len(errors) == 0, errors
    
    # 重複排除
    check_urls = list(set(check_urls))

    errors = []
    # リンクの生死チェック(非同期実行)
    asyncio.get_event_loop().run_until_complete(
        check_url(check_urls, set_error, sem)
    )
    # error数が0でない場合はNG
    assert len(errors) == 0, errors

    # mkdocs serveを起動した場合は、プロセスを終了させる
    if proc is not None:
        proc.kill()
        proc = None

def check_and_start_mkdocs(mkdocs_url) -> subprocess.Popen:
    """
    mkdocs serveのURLへアクセスし、起動していない場合は起動する
    :param mkdocs_url: mkdocs serveが起動しているURL
    """
    proc = None
    try:
        # mkdocs serveが起動しているかチェック
        requests.get(mkdocs_url)
    except requests.exceptions.ConnectionError:
        # 接続できない場合はmkdocs serveを起動
        proc = subprocess.Popen(
                ['mkdocs', 'serve'],
                cwd='release',
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
        while proc.returncode is None:
            if 'Start detecting changes' in proc.stdout.readline():
                break
    return proc


async def fetch_and_parse(target_urls, result_callback, error_callback, semaphore):
    """
    URLからHTMLを取得し、リンクの一覧を抽出してコールバックに渡す
    :param target_urls: 対象とするURLのリスト
    :param result_callback: 成功時のリンクを渡すコールバック
    :param error_callback: エラー時のコールバック
    """
    tasks = []
    async def fetch(s, url):
        async with semaphore:
            async with s.get(url) as res:
                # 指定されたURLをGETして解析
                status_code = res.status
                if status_code != 200:
                    error_callback('{}:{}'.format(str(status_code), url))
                return await get_links(url, await res.text())

    async with aiohttp.ClientSession() as session:
        for target_url in target_urls:
            task = asyncio.ensure_future(fetch(session, target_url))
            task.add_done_callback(result_callback)
            tasks.append(task)
        return await asyncio.wait(tasks)

async def get_links(target_url, html) -> list:
    soup = BeautifulSoup(html, "lxml")
    test_urls = []
    for a in soup.find_all("a"):
        href = a.get("href")

        url = urlparse(target_url)
        if '://' in href:
            if url.scheme == 'http' or url.scheme == 'https':
                if url.netloc in href and len(url.netloc) > 0:
                    # 絶対リンクかつ、同一ドメイン
                    test_urls.append(quote(href, safe='./:', encoding='utf-8'))
                else:
                    # 外部サイトリンクはテストしない
                    #print('IGNORE:{}'.format(href))
                    pass
            else:
                # http, https以外はテストしない
                #print('IGNORE:{}'.format(href))
                pass
        elif href[0] == '#':
            # フラグメント指定は無視
            pass
        else:
            # ドメイン指定なし
            if href[0] == '/':
                path = ''
            elif url.path.endswith('/'):
                path = url.path
            else:
                path = url.path + '/'

            test_urls.append(quote('{}://{}{}{}'.format(url.scheme, url.netloc, path, href), safe='./:', encoding='utf-8'))

    # 重複排除
    test_urls = list(set(test_urls))
    return test_urls


async def check_url(check_urls, error_callback, semaphore):
    """
    非同期でURLをチェックして、HTTP STATUSが200を応答することをチェック
    :param check_urls: str
    :param error_callback: Func
    """
    tasks = []
    async def check(s, url):
        async with semaphore:
            try:
                async with s.get(url) as res:
                    # 指定されたURLをGETして解析
                    status_code = res.status
                    if status_code != 200:
                        error_callback('{}:{}'.format(str(status_code), url))
            except:
                error_callback('{}:{}'.format(sys.exc_info() ,url))

    async with aiohttp.ClientSession() as session:
        for url in check_urls:
            task = asyncio.ensure_future(check(session, url))
            tasks.append(task)
        return await asyncio.wait(tasks)
