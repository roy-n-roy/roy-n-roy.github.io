# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import random
import sys
from urllib.parse import urlparse, quote

from bs4 import BeautifulSoup
import requests
import asyncio
import aiohttp

def test_urls():
	url_list = [
		"http://localhost:8000"
	]
	for url in url_list:
		parse_and_request(url)


def parse_and_request(url):
	"""
	urlをダウンロードして、bs4を解析して
	全リンクのステータスチェックする
	"""
	# urlをパース
	o = urlparse(url)
	host = o.netloc

	# 指定されたURLをGETして解析
	res = requests.get(url)
	assert res.status_code == 200
	test_urls = parse_and_get_links(host, res.text)
	# リンクが生きているか非同期実行してチェック
	asyncio.get_event_loop().run_until_complete(
		asyncio.wait([check_url(test_url) for test_url in test_urls])
	)

def parse_and_get_links(host, html):
	"""
	htmlをパースからリンクを取り出してリンクの一覧を返す
	:param host: 対象とするホスト名
	:param html: パース対象のHTMLテキスト
	"""
	soup = BeautifulSoup(html, "lxml")
	test_urls = []
	for a in soup.find_all("a"):
		href = a.get("href")
		if href[0] == '#':
			pass
		elif href[0] == '/':
			# 相対リンク
			test_urls.append(quote('http://{}{}'.format(host, href), safe='/:', encoding='utf-8'))
		elif host in href:
			# 絶対リンクかつ、同一ドメイン
			test_urls.append(quote(href), safe='/:', encoding='utf-8')
		elif not href.startswith('http://') and not href.startswith('https://'):
			# 相対リンク
			test_urls.append(quote('http://{}/{}'.format(host, href), safe='/:', encoding='utf-8'))
		else:
			# 外部サイトリンクはテストしない
			print('IGNORE:{}'.format(href))

	# 重複排除
	test_urls = list(set(test_urls))
	print(test_urls)
	return test_urls


async def check_url(url):
	"""
	非同期でURLをチェックして、HTTP STATUSが200を応答することをチェック
	:param url: str
	"""
	async with aiohttp.ClientSession() as session:
		async with session.get(url) as response:
			status_code = response.status
			assert status_code == 200, '{}:{}'.format(str(status_code), url)
			print( status_code == 200, '{}:{}'.format(str(status_code), url))

test_urls()
