# -*- coding: utf-8 -*-
"""
銘柄スコアリングロジック(簡易ルールベース)。

方針:
- 「なぜこの銘柄が推奨されているか」を必ず説明できるようにする(ブラックボックス化しない)。
- 政治・ニュース関連の見出しにセクターキーワードがヒットした数と、
  直近の値動き(モメンタム)を組み合わせて単純なスコアを算出する。
- 高度な機械学習モデルではなく、あくまで「情報を整理して見せる」ためのルールベース実装。
  将来的にアルゴリズムを差し替えやすいよう、関数を分離している。
"""
from dataclasses import dataclass, field
from typing import List

from data_fetch import PriceInfo
from news_fetch import NewsItem


@dataclass
class Recommendation:
    ticker: str
    name: str
    market: str
    score: float
    price_info: PriceInfo
    matched_news: List[NewsItem] = field(default_factory=list)
    reason: str = ""


def _news_score(sectors: List[str], news_items: List[NewsItem]):
    matched = []
    for item in news_items:
        for sector in sectors:
            if sector in item.title:
                matched.append(item)
                break
    return matched


def _momentum_score(price_info: PriceInfo) -> float:
    if price_info.change_5d_pct is None:
        return 0.0
    # 値動きの大きさをそのままスコアに反映(符号は問わず、動きが大きいほど注目度が高いとみなす)
    return abs(price_info.change_5d_pct)


def score_watchlist(watchlist, price_map, news_items: List[NewsItem]) -> List[Recommendation]:
    """ウォッチリスト全体をスコアリングし、スコアの高い順に並べて返す。"""
    recommendations = []

    for item in watchlist:
        ticker = item["ticker"]
        price_info = price_map.get(ticker)
        if price_info is None:
            continue

        matched_news = _news_score(item["sectors"], news_items)
        news_pts = len(matched_news) * 5.0  # ニュース1件ヒットにつき5点
        momentum_pts = _momentum_score(price_info)
        total_score = news_pts + momentum_pts

        reason_parts = []
        if matched_news:
            reason_parts.append(f"関連ニュース{len(matched_news)}件ヒット(セクター: {', '.join(item['sectors'])})")
        if price_info.change_5d_pct is not None:
            reason_parts.append(f"直近5営業日で{price_info.change_5d_pct:+.1f}%の値動き")
        if not reason_parts:
            reason_parts.append("特筆すべき材料は検出されませんでした")

        recommendations.append(
            Recommendation(
                ticker=ticker,
                name=item["name"],
                market=item["market"],
                score=total_score,
                price_info=price_info,
                matched_news=matched_news,
                reason=" / ".join(reason_parts),
            )
        )

    recommendations.sort(key=lambda r: r.score, reverse=True)
    return recommendations
