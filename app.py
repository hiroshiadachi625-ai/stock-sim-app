# -*- coding: utf-8 -*-
"""
株式投資 情報表示・仮想売買シミュレーションゲーム(個人利用専用)

このアプリは実際の証券口座には一切接続しない。
「買ったつもり」ボタンはローカルのSQLiteに記録を残すだけで、実資金は動かない。
教育・娯楽目的のシミュレーションであり、投資助言ではない。

起動方法:
    pip install -r requirements.txt
    streamlit run app.py
"""
import streamlit as st

from watchlist import get_watchlist
import auth
import data_fetch
import news_fetch
import scoring
import portfolio

st.set_page_config(page_title="株式シミュレーションゲーム(個人用)", page_icon="📈", layout="wide")
auth.require_password()
portfolio.init_db()

st.title("📈 株式投資 情報表示・仮想売買シミュレーション")
st.caption(
    "個人利用専用のツールです。実際の証券口座には接続しておらず、"
    "『買ったつもり』ボタンは仮想の記録を残すだけで実資金は動きません。"
    "投資助言ではなく、教育・娯楽目的のシミュレーションです。"
)

tab_reco, tab_portfolio, tab_watchlist = st.tabs(["🔍 おすすめ銘柄", "💼 ポートフォリオ(買ったつもり)", "⚙️ ウォッチリスト"])


@st.cache_data(ttl=600, show_spinner="株価データを取得中...")
def load_prices(tickers_tuple):
    watchlist = get_watchlist()
    return data_fetch.fetch_prices_for_watchlist(watchlist)


@st.cache_data(ttl=600, show_spinner="ニュースを取得中...")
def load_news():
    return news_fetch.fetch_recent_news()


with tab_reco:
    col_refresh, _ = st.columns([1, 5])
    with col_refresh:
        if st.button("🔄 最新データに更新"):
            load_prices.clear()
            load_news.clear()
            st.rerun()

    watchlist = get_watchlist()
    tickers_tuple = tuple(sorted(w["ticker"] for w in watchlist))

    try:
        price_map = load_prices(tickers_tuple)
    except Exception as e:
        st.error(f"株価データの取得に失敗しました: {e}")
        price_map = {}

    try:
        news_items = load_news()
    except Exception as e:
        st.warning(f"ニュースの取得に失敗しました(推奨は値動きのみで計算されます): {e}")
        news_items = []

    recos = scoring.score_watchlist(watchlist, price_map, news_items)

    if not recos:
        st.info("表示できる銘柄がありません。ネットワーク接続や株価データ取得を確認してください。")

    for reco in recos:
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 2, 2])
            with c1:
                st.subheader(f"{reco.name} ({reco.ticker}) [{reco.market}]")
                st.write(reco.reason)
                if reco.matched_news:
                    with st.expander("関連ニュースを見る"):
                        for n in reco.matched_news[:5]:
                            st.markdown(f"- [{n.title}]({n.link})  \n  _{n.source} / {n.published:%Y-%m-%d %H:%M}_")
            with c2:
                if reco.price_info.error:
                    st.error(f"価格取得エラー: {reco.price_info.error}")
                else:
                    st.metric(
                        "現在値",
                        f"{reco.price_info.current_price:,.1f} {reco.price_info.currency or ''}",
                        f"{reco.price_info.change_5d_pct:+.1f}% (5日)" if reco.price_info.change_5d_pct is not None else None,
                    )
                st.caption(f"スコア: {reco.score:.1f}")
            with c3:
                default_qty = 100 if reco.market == "JP" else 1
                qty = st.number_input(
                    "株数", min_value=1, value=default_qty, step=1, key=f"qty_{reco.ticker}"
                )
                buy_disabled = reco.price_info.error is not None or reco.price_info.current_price is None
                if st.button("✅ 買ったつもり", key=f"buy_{reco.ticker}", disabled=buy_disabled, use_container_width=True):
                    portfolio.add_virtual_buy(
                        ticker=reco.ticker,
                        name=reco.name,
                        market=reco.market,
                        quantity=qty,
                        buy_price=reco.price_info.current_price,
                        reason=reco.reason,
                    )
                    st.success(f"{reco.name} を {qty}株「買ったつもり」で記録しました。")
                    st.rerun()


with tab_portfolio:
    perf = portfolio.summarize_performance()
    m1, m2, m3 = st.columns(3)
    m1.metric("確定取引回数", perf["total_trades"])
    m2.metric("勝率", f"{perf['win_rate']:.1f}%" if perf["win_rate"] is not None else "-")
    m3.metric("実現損益合計", f"{perf['total_realized_pnl']:,.0f}")

    st.subheader("保有中(未決済)ポジション")
    open_trades = portfolio.get_open_trades()
    if not open_trades:
        st.caption("保有中のポジションはありません。「おすすめ銘柄」タブから買ったつもりを記録してください。")
    else:
        open_tickers = tuple(sorted({t.ticker for t in open_trades}))
        try:
            current_prices = {tk: data_fetch.fetch_price_info(tk) for tk in open_tickers}
        except Exception:
            current_prices = {}

        for t in open_trades:
            cur = current_prices.get(t.ticker)
            cur_price = cur.current_price if cur and cur.current_price is not None else None
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
                c1.write(f"**{t.name} ({t.ticker})** / {t.quantity}株 @ {t.buy_price:,.1f}")
                c1.caption(f"購入日: {t.buy_date}")
                if cur_price is not None:
                    unrealized = (cur_price - t.buy_price) * t.quantity
                    c2.metric("現在値", f"{cur_price:,.1f}")
                    c3.metric("含み損益", f"{unrealized:,.0f}")
                else:
                    c2.write("現在値取得エラー")
                with c4:
                    if st.button("💰 売ったことにする", key=f"sell_{t.id}", disabled=cur_price is None):
                        portfolio.close_trade(t.id, cur_price)
                        st.success(f"{t.name} を決済しました。")
                        st.rerun()

    st.subheader("取引履歴(決済済み)")
    closed_trades = portfolio.get_closed_trades()
    if not closed_trades:
        st.caption("まだ決済済みの取引はありません。")
    else:
        rows = []
        for t in closed_trades:
            pnl = (t.sell_price - t.buy_price) * t.quantity
            rows.append(
                {
                    "銘柄": f"{t.name} ({t.ticker})",
                    "株数": t.quantity,
                    "購入価格": t.buy_price,
                    "売却価格": t.sell_price,
                    "損益": pnl,
                    "購入日": t.buy_date,
                    "決済日": t.sell_date,
                }
            )
        st.dataframe(rows, use_container_width=True)

    st.divider()
    st.caption(
        "⚠️ クラウド上で動かしている場合、再デプロイやスリープからの復帰時に"
        "portfolio.db の内容が消えることがあります。念のため、定期的に下のボタンで"
        "バックアップを取っておくことをおすすめします。"
    )
    all_trades = portfolio.get_all_trades()
    if all_trades:
        import csv
        import io

        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["id", "ticker", "name", "market", "quantity", "buy_price", "buy_date", "reason", "status", "sell_price", "sell_date"])
        for t in all_trades:
            writer.writerow([t.id, t.ticker, t.name, t.market, t.quantity, t.buy_price, t.buy_date, t.reason, t.status, t.sell_price, t.sell_date])
        st.download_button(
            "⬇️ 取引データをCSVでバックアップ",
            data=buf.getvalue().encode("utf-8-sig"),
            file_name="portfolio_backup.csv",
            mime="text/csv",
        )


with tab_watchlist:
    st.subheader("現在のウォッチリスト")
    st.caption(
        "watchlist.py の DEFAULT_WATCHLIST を編集することで銘柄を追加・削除できます"
        "(将来的には画面上で編集できるようにする想定)。"
    )
    st.dataframe(get_watchlist(), use_container_width=True)
