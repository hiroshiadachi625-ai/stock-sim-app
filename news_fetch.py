# -*- coding: utf-8 -*-
"""
ニュース(政治・経済)取得モジュール。
RSSフィードから見出しを取得し、後段のスコアリングで銘柄との関連付けに使う。

注意:
開発環境(クラウドサンドボックス)ではネットワーク制限によりRSS取得の動作確認ができていない。
実際の動作確認はローカルPCで行うこと。フィードが取得できない場合も
アプリ全体が落ちないよう、失敗したフィードは黙ってスキップする設計にしている。
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List
import time

import feedparser

# デフォルトのニュースソース(RSS)。
# 政治・経済関連のニュースを広く拾うことを想定。必要に応じて追加・変更してよい。
DEFAULT_FEEDS = [
    {"name": "NHKニュース(政治)", "url": "https://www3.nhk.or.jp/rss/news/cat4.xml"},
    {"name": "NHKニュース(経済)", "url": "https://www3.nhk.or.jp/rss/news/cat5.xml"},
    {"name": "Yahoo!ニュース(国内)", "url": "https://news.yahoo.co.jp/rss/topics/domestic.xml"},
    {"name": "Yahoo!ニュース(経済)", "url": "https://news.yahoo.co.jp/rss/topics/business.xml"},
    {"name": "Reuters Politics (English)", "url": "https://feeds.reuters.com/Reuters/PoliticsNews"},
]


@dataclass
class NewsItem:
    title: str
    link: str
    source: str
    published: datetime


def _parse_time(entry) -> datetime:
    for key in ("published_parsed", "updated_parsed"):
        val = getattr(entry, key, None)
        if val:
            try:
                return datetime(*val[:6])
            except Exception:
                pass
    return datetime.now()


def fetch_recent_news(feeds=None, max_age_hours: int = 72, per_feed_limit: int = 30) -> List[NewsItem]:
    """登録済みRSSフィードから直近のニュース見出しを取得する。

    取得に失敗したフィードはスキップし、全体としては可能な範囲の結果を返す。
    """
    if feeds is None:
        feeds = DEFAULT_FEEDS

    cutoff = datetime.now() - timedelta(hours=max_age_hours)
    items: List[NewsItem] = []

    for feed in feeds:
        try:
            parsed = feedparser.parse(feed["url"])
            entries = getattr(parsed, "entries", []) or []
            for entry in entries[:per_feed_limit]:
                title = getattr(entry, "title", None)
                link = getattr(entry, "link", "")
                if not title:
                    continue
                published = _parse_time(entry)
                if published < cutoff:
                    continue
                items.append(NewsItem(title=title, link=link, source=feed["name"], published=published))
        except Exception:
            # フィード単位の失敗はアプリ全体を止めない
            continue

    items.sort(key=lambda x: x.published, reverse=True)
    return items
