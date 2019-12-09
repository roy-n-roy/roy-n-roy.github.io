# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import random
import sys
import subprocess
import glob
import re
from urllib.parse import urlparse, quote

from bs4 import BeautifulSoup
import requests
import asyncio
import aiohttp

def test_urls():
	"""
	urlをダウンロードして、bs4を解析して
	全リンクのステータスチェックする
	"""

	base_url = "http://localhost:8000/"
	proc = None

	if sys.platform == 'win32':
		asyncio.set_event_loop(asyncio.ProactorEventLoop())

	proc = None
	# Serverが起動しているかチェック
	try:
		requests.get(base_url)
	except requests.exceptions.ConnectionError:
		# 接続できない場合はmkdocs serveを起動
		proc = subprocess.Popen(['mkdocs', 'serve'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
		while proc.returncode is None:
			if 'Start detecting changes' in proc.stdout.readline():
				break

	target_urls = []
	for md in glob.glob('docs/**/*.md', recursive=True):
		target_urls.append(base_url + re.sub(r'^docs\\|\.md$|index\.md$', '', md).replace('\\', '/'))

	test_urls = []
	errors = []
	def extend_test_urls(url_list):
		test_urls.extend(url_list)

	def set_error(result):
		errors.append(result)

	# パース対象URLからリンクを取得
	asyncio.get_event_loop().run_until_complete(
		asyncio.wait([
			request_and_parse(target_url, extend_test_urls, set_error) for target_url in target_urls
		])
	)
	assert len(errors) == 0, errors
	
	# 重複排除
	test_urls = list(set(test_urls))

	errors = []
	# リンクの生死チェック(非同期実行)
	asyncio.get_event_loop().run_until_complete(
		asyncio.wait([
			check_url(test_url, set_error) for test_url in test_urls
		])
	)
	assert len(errors) == 0, errors

	if proc is not None:
		proc.kill()
		proc = None

async def request_and_parse(target_url, result_callback, error_callback):
	"""
	html文字列からリンクを取り出してリンクの一覧を返す
	:param host: 対象とするホスト名
	:param html: パース対象のHTMLテキスト
	"""
	async with aiohttp.ClientSession() as session:
		async with session.get(target_url) as response:
			# 指定されたURLをGETして解析
			status_code = response.status
			if status_code == 200:
				result_callback(get_links(target_url, await response.text()))
			else:
				error_callback('{}:{}'.format(str(status_code), target_url))

def get_links(target_url, html) -> list:
	soup = BeautifulSoup(html, "lxml")
	test_urls = []
	for a in soup.find_all("a"):
		href = a.get("href")

		url = urlparse(target_url)
		if '://' in href:
			if url.scheme == 'http' or url.scheme == 'https':
				if url.netloc in href:
					# 絶対リンクかつ、同一ドメイン
					test_urls.append(quote(href), safe='/:', encoding='utf-8')
				else:
					# 外部サイトリンクはテストしない
					print('IGNORE:{}'.format(href))
			else:
				# http, https以外はテストしない
				print('IGNORE:{}'.format(href))
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

			test_urls.append(quote('{}://{}{}{}'.format(url.scheme, url.netloc, path, href), safe='/:', encoding='utf-8'))

	# 重複排除
	test_urls = list(set(test_urls))
	return test_urls


async def check_url(url, error_callback):
	"""
	非同期でURLをチェックして、HTTP STATUSが200を応答することをチェック
	:param url: str
	"""
	async with aiohttp.ClientSession() as session:
		async with session.get(url) as response:
			status_code = response.status
			if status_code != 200:
				error_callback('{}:{}'.format(str(status_code), url))

test_urls()