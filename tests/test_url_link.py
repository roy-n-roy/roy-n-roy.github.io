import asyncio
import glob
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote, urlparse
import time

import aiohttp
import requests
from bs4 import BeautifulSoup
import pytest
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# mkdocs serve実行時のURL
mkdocs_url = 'http://127.0.0.1:7160/'


@pytest.fixture(scope="module")
def start_mkdocs(request):
    """
    mkdocs serveのURLへアクセスし、起動していない場合は起動する
    """
    proc = None
    try:
        # mkdocs serveが起動しているかチェック
        requests.get(mkdocs_url)
        assert False, "mkdocs already started."
    except requests.exceptions.ConnectionError:
        # 接続できない場合はmkdocs serveを起動
        proc = subprocess.Popen(
                ['mkdocs', 'serve', '-a', urlparse(mkdocs_url).netloc],
                cwd=Path(__file__).parents[1].relative_to(os.getcwd()),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
        
        session = requests.Session()
        retries = Retry(
                total=5,
                backoff_factor=1,
                status_forcelist=[500, 502, 503, 504]
            )
        session.mount("http://", HTTPAdapter(max_retries=retries))
        session.get(url=mkdocs_url, timeout=(6.0, 15.0))

    def stop_process():
        if proc:
            proc.kill()

    request.addfinalizer(stop_process)


def test_urls(start_mkdocs):
    """
    docs配下のMarkdownファイルを対象として
    全リンクのステータスチェックする
    """

    # 並列実行数
    max_access_count = 100

    release_dir = str(Path(__file__).parents[1].relative_to(os.getcwd()))
    # テスト対象URLのリスト
    target_urls = []
    # docs配下の*.mdファイルを検索し、対象URLリストを作成
    for md in glob.glob(release_dir + '/docs/**/*.md', recursive=True):
        target_urls.append(
            mkdocs_url +
            re.sub(
                r'^%s/docs/|\.md$|index\.md$' % release_dir, '',
                md.replace(os.sep, '/')
            )
        )

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


async def fetch_and_parse(
            target_urls,
            result_callback,
            error_callback,
            semaphore
        ):
    """
    URLからHTMLを取得し、リンクの一覧を抽出してコールバックに渡す
    :param target_urls: 対象とするURLのリスト
    :param result_callback: 成功時のリンクを渡すコールバック
    :param error_callback: エラー時のコールバック
    :param semaphore: 並列実行数制限に使用するセマフォ
    """
    tasks = []

    async def fetch(s, url):
        async with semaphore:
            async with s.get(url) as res:
                # 指定されたURLをGETして解析
                status_code = res.status
                if status_code != 200:
                    error_callback(f'{str(status_code)}:{url}')
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
            if url.scheme in ['http', 'https']:
                if url.netloc in href and len(url.netloc) > 0:
                    # 絶対リンクかつ、同一ドメイン
                    test_urls.append(quote(
                        href, safe='./:#%', encoding='utf-8'
                    ))
                else:
                    # 外部サイトリンクはテストしない
                    pass
            else:
                # http, https以外はテストしない
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

            test_urls.append(quote(
                f'{url.scheme}://{url.netloc}{path}{href}',
                safe='./:#%', encoding='utf-8'
            ))

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
                        error_callback(f'{str(status_code)}:{url}')
            except Exception:
                error_callback(f'{sys.exc_info()}:{url}')

    async with aiohttp.ClientSession() as session:
        for url in check_urls:
            task = asyncio.ensure_future(check(session, url))
            tasks.append(task)
        return await asyncio.wait(tasks)
