# -*- coding: utf-8 -*-
"""
株価データ取得モジュール。
yfinance を使って現在値・直近の値動きを取得する。

注意:
このモジュールはインターネット上の Yahoo Finance にアクセスする。
開発環境(クラウドサンドボックス)ではネットワーク制限により動作確認できていないため、
実際の動作確認はローカルPC(通常のインターネット接続がある環境)で行うこと。
"""
from dataclasses import dataclass
from typing import Optional
import time

import yfinance as yf


@dataclass
class PriceInfo:
    ticker: str
    current_price: Optional[float]
    change_5d_pct: Optional[float]  # 直近5営業日の変化率(%)
    currency: Optional[str]
    error: Optional[str] = None


def fetch_price_info(ticker: str, retries: int = 2, sleep_sec: float = 1.0) -> PriceInfo:
    """1銘柄分の現在値と直近5日騰落率を取得する。取得失敗時は error にメッセージを入れて返す。"""
    last_err = None
    for attempt in range(retries + 1):
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="10d", interval="1d")
            if hist is None or hist.empty:
                last_err = "価格データが取得できませんでした"
                time.sleep(sleep_sec)
                continue

            closes = hist["Close"].dropna()
            if len(closes) == 0:
                last_err = "終値データが空です"
                time.sleep(sleep_sec)
                continue

            current_price = float(closes.iloc[-1])
            if len(closes) >= 6:
                base_price = float(closes.iloc[-6])
            else:
                base_price = float(closes.iloc[0])

            change_pct = None
            if base_price:
                change_pct = (current_price - base_price) / base_price * 100

            currency = None
            try:
                currency = t.fast_info.get("currency")
            except Exception:
                pass

            return PriceInfo(
                ticker=ticker,
                current_price=current_price,
                change_5d_pct=change_pct,
                currency=currency,
            )
        except Exception as e:  # noqa: BLE001
            last_err = str(e)
            time.sleep(sleep_sec)

    return PriceInfo(ticker=ticker, current_price=None, change_5d_pct=None, currency=None, error=last_err)


def fetch_prices_for_watchlist(watchlist):
    """ウォッチリスト全銘柄の価格情報を辞書 {ticker: PriceInfo} で返す。"""
    result = {}
    for item in watchlist:
        result[item["ticker"]] = fetch_price_info(item["ticker"])
    return result
