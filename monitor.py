import requests
from bs4 import BeautifulSoup
import hashlib
import json
import os
from linebot import LineBotApi
from linebot.models import TextSendMessage
from datetime import datetime

# 設定だよ～💕 nanacoとANAのページをチェックするの！
URLS = [
    'https://www.nanaco-net.jp/cp/',  # nanacoのキャンペーンページ🌸
    'https://www.ana.co.jp/ja/jp/shoppingandlife/point/tameru_nanaco_point/'  # ANAの交換ページ✈️
]
STATE_FILE = 'state.json'  # 覚えておくファイルだよ～📝

# LINEの設定（環境変数から読み込むの！秘密だよ💕）
LINE_ACCESS_TOKEN = os.environ.get('LINE_ACCESS_TOKEN')
USER_ID = os.environ.get('USER_ID')

def get_page_hash(url):
    """ページの内容をハッシュ化しちゃうよ～🔮 変化をキャッチ！"""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        return hashlib.md5(text.encode()).hexdigest()
    except Exception as e:
        print(f"ページ取得でハプニング💦 {url}: {e}")
        return None

def load_state():
    """前回の状態を思い出してあげる～💭"""
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_state(state):
    """新しい状態をメモしとこ～📸"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def send_notification(subject, body):
    """LINEに可愛いお知らせを送っちゃうよ～📱💌"""
    if not LINE_ACCESS_TOKEN or not USER_ID:
        print("LINEの設定が足りないよ～😿 環境変数をチェックしてね！")
        return

    my_text = f"{subject}\n{body}"
    try:
        line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
        my_messages = TextSendMessage(text=my_text)
        line_bot_api.push_message(USER_ID, messages=my_messages)
        print("LINE通知を送ったよ～🎀✨")
    except Exception as e:
        print(f"LINEでトラブル💔: {e}")

def check_campaigns():
    """キャンペーンをこっそりチェックしちゃうの～🕵️‍♀️💖"""
    state = load_state()
    current_state = {}
    changed_urls = []

    for url in URLS:
        hash_val = get_page_hash(url)
        if hash_val:
            current_state[url] = hash_val
            prev_hash = state.get(url)
            if prev_hash and hash_val != prev_hash:
                changed_urls.append(url)
                print(f"変化発見！ {url} が変わったよ～🔥")
            elif not prev_hash:
                print(f"初めてのチェック完了～初めまして💕 {url}")

    # 変更があったら、ANA関連か調べてお知らせ～👀
    for url in changed_urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text().lower()
        if any(keyword in text for keyword in ['ana', 'マイル', '交換', 'レートアップ']):
            subject = "🎉わーい！nanaco ANAキャンペーン発見💕✈️"
            body = f"nanaco×ANAのキャンペーンがスタートしたよ～🚀\nURL: {url}\n日時: {datetime.now()}\n詳細: {text[:200]}...\n早くチェックしてね！💖"
            send_notification(subject, body)
            print(f"ANAキャンペーン検知～超ラッキー！🍀 {url}")

    # 状態を更新しちゃうよ～🔄
    save_state(current_state)
    if not changed_urls:
        print("今日も変化なしだよ～のんびり待とうね💤🌸")

if __name__ == "__main__":
    print("nanaco ANA監視スタート～可愛くチェック中💕")
    check_campaigns()
    print("チェックおしまい～また明日ね！👋✨")
