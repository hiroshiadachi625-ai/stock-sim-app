# -*- coding: utf-8 -*-
"""
デフォルトのウォッチリスト。
政治・政策の影響を受けやすいセクターを中心に、日本株・米国株を登録している。
ticker は yfinance の形式(日本株は末尾に .T)。
セクタータグは news_fetch / scoring でニュースとの関連付けに使う。
"""

DEFAULT_WATCHLIST = [
    # --- 日本株 ---
    {"ticker": "7011.T", "name": "三菱重工業", "market": "JP", "sectors": ["防衛", "安全保障", "宇宙"]},
    {"ticker": "7013.T", "name": "IHI", "market": "JP", "sectors": ["防衛", "エネルギー"]},
    {"ticker": "6301.T", "name": "コマツ", "market": "JP", "sectors": ["インフラ", "建設機械"]},
    {"ticker": "9501.T", "name": "東京電力ホールディングス", "market": "JP", "sectors": ["エネルギー", "電力", "原発"]},
    {"ticker": "9502.T", "name": "中部電力", "market": "JP", "sectors": ["エネルギー", "電力", "原発"]},
    {"ticker": "1605.T", "name": "INPEX", "market": "JP", "sectors": ["エネルギー", "資源"]},
    {"ticker": "8035.T", "name": "東京エレクトロン", "market": "JP", "sectors": ["半導体", "経済安全保障"]},
    {"ticker": "6857.T", "name": "アドバンテスト", "market": "JP", "sectors": ["半導体"]},
    {"ticker": "9433.T", "name": "KDDI", "market": "JP", "sectors": ["通信", "インフラ"]},
    {"ticker": "9432.T", "name": "日本電信電話(NTT)", "market": "JP", "sectors": ["通信", "インフラ"]},
    {"ticker": "1802.T", "name": "大林組", "market": "JP", "sectors": ["インフラ", "建設", "公共事業"]},
    {"ticker": "5411.T", "name": "JFEホールディングス", "market": "JP", "sectors": ["インフラ", "資源"]},

    # --- 米国株 ---
    {"ticker": "LMT", "name": "Lockheed Martin", "market": "US", "sectors": ["防衛", "安全保障"]},
    {"ticker": "RTX", "name": "RTX Corporation", "market": "US", "sectors": ["防衛", "安全保障"]},
    {"ticker": "NOC", "name": "Northrop Grumman", "market": "US", "sectors": ["防衛", "宇宙"]},
    {"ticker": "XOM", "name": "ExxonMobil", "market": "US", "sectors": ["エネルギー", "資源"]},
    {"ticker": "CVX", "name": "Chevron", "market": "US", "sectors": ["エネルギー", "資源"]},
    {"ticker": "NVDA", "name": "NVIDIA", "market": "US", "sectors": ["半導体", "経済安全保障", "AI規制"]},
    {"ticker": "INTC", "name": "Intel", "market": "US", "sectors": ["半導体", "経済安全保障"]},
    {"ticker": "TSM", "name": "Taiwan Semiconductor (ADR)", "market": "US", "sectors": ["半導体", "地政学", "台湾"]},
]


def get_watchlist():
    """現在のウォッチリストを返す(将来的にはユーザー設定で追加・削除できるようにする想定)。"""
    return DEFAULT_WATCHLIST
