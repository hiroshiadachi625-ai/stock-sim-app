# -*- coding: utf-8 -*-
"""
仮想ポートフォリオ(買ったつもり)管理モジュール。
実際の資金は動かさず、SQLiteに取引記録を保存するだけのシンプルな実装。
"""
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

DB_PATH = "portfolio.db"


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _connect()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            name TEXT NOT NULL,
            market TEXT NOT NULL,
            quantity REAL NOT NULL,
            buy_price REAL NOT NULL,
            buy_date TEXT NOT NULL,
            reason TEXT,
            status TEXT NOT NULL DEFAULT 'open',  -- 'open' or 'closed'
            sell_price REAL,
            sell_date TEXT
        )
        """
    )
    conn.commit()
    conn.close()


@dataclass
class Trade:
    id: int
    ticker: str
    name: str
    market: str
    quantity: float
    buy_price: float
    buy_date: str
    reason: str
    status: str
    sell_price: Optional[float]
    sell_date: Optional[str]


def add_virtual_buy(ticker: str, name: str, market: str, quantity: float, buy_price: float, reason: str = ""):
    """「買ったつもり」記録を追加する。実際の発注は一切行わない。"""
    conn = _connect()
    conn.execute(
        """
        INSERT INTO trades (ticker, name, market, quantity, buy_price, buy_date, reason, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'open')
        """,
        (ticker, name, market, quantity, buy_price, datetime.now().isoformat(timespec="seconds"), reason),
    )
    conn.commit()
    conn.close()


def close_trade(trade_id: int, sell_price: float):
    """「売ったつもり」で取引をクローズし、損益を確定させる。"""
    conn = _connect()
    conn.execute(
        """
        UPDATE trades SET status = 'closed', sell_price = ?, sell_date = ?
        WHERE id = ? AND status = 'open'
        """,
        (sell_price, datetime.now().isoformat(timespec="seconds"), trade_id),
    )
    conn.commit()
    conn.close()


def get_all_trades() -> List[Trade]:
    conn = _connect()
    rows = conn.execute("SELECT * FROM trades ORDER BY buy_date DESC").fetchall()
    conn.close()
    return [Trade(**dict(row)) for row in rows]


def get_open_trades() -> List[Trade]:
    return [t for t in get_all_trades() if t.status == "open"]


def get_closed_trades() -> List[Trade]:
    return [t for t in get_all_trades() if t.status == "closed"]


def summarize_performance():
    """成績サマリー(実現損益、勝率、取引回数など)を計算する。"""
    closed = get_closed_trades()
    total_trades = len(closed)
    if total_trades == 0:
        return {
            "total_trades": 0,
            "win_rate": None,
            "total_realized_pnl": 0.0,
        }

    wins = 0
    total_pnl = 0.0
    for t in closed:
        pnl = (t.sell_price - t.buy_price) * t.quantity
        total_pnl += pnl
        if pnl > 0:
            wins += 1

    return {
        "total_trades": total_trades,
        "win_rate": wins / total_trades * 100,
        "total_realized_pnl": total_pnl,
    }
