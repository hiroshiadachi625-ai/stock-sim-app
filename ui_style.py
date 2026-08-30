# -*- coding: utf-8 -*-
"""
UIの見た目調整(カスタムCSS)。

SMFG(三井住友フィナンシャルグループ)系の銀行アプリのような、
「白背景+グリーン基調+カード型リスト」という金融アプリらしい雰囲気を目指した
スタイル調整。ブランドカラーの正確な色コードは公開情報から特定できなかったため、
一般的な銀行アプリのグリーンに寄せた近似色を使っている(完全な再現ではない)。

Streamlitの内部HTML構造(data-testid)に依存している部分があるため、
Streamlitのバージョンが大きく変わるとズレる可能性がある。
"""
import streamlit as st

CUSTOM_CSS = """
<style>
/* ---- 全体のベース ---- */
html, body, [class*="css"] {
    font-family: "Hiragino Sans", "Noto Sans JP", "Yu Gothic", -apple-system,
        BlinkMacSystemFont, sans-serif;
}

/* Streamlitの「Made with Streamlit」フッターを非表示にして、より独立したアプリらしく見せる */
footer {visibility: hidden;}

/* ---- ヘッダー(タイトル)まわり ---- */
h1 {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: #0B3D2E;
}

/* ---- タブをセグメントコントロール風に ---- */
button[data-baseweb="tab"] {
    border-radius: 999px !important;
    padding: 0.4rem 1rem !important;
    font-weight: 600 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background-color: #E6F5EC !important;
    color: #00A960 !important;
}
div[data-baseweb="tab-highlight"] {
    background-color: #00A960 !important;
}

/* ---- カード(枠付きコンテナ)を、銀行アプリのリスト項目のような見た目に ---- */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF;
    border-radius: 16px !important;
    border: 1px solid #E7EBE9 !important;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
    padding: 0.25rem 0.25rem;
    margin-bottom: 0.75rem;
}

/* ---- ボタン ---- */
.stButton > button, .stDownloadButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1rem !important;
}
/* プライマリボタン(買ったつもり等)はブランドグリーンで塗りつぶし */
.stButton > button[kind="primary"] {
    background-color: #00A960 !important;
    border-color: #00A960 !important;
}
.stButton > button[kind="primary"]:hover {
    background-color: #00924F !important;
    border-color: #00924F !important;
}

/* ---- 数値(現在値・損益など)を銀行アプリの残高表示っぽく強調 ---- */
div[data-testid="stMetricValue"] {
    font-size: 1.4rem !important;
    font-weight: 700 !important;
}
div[data-testid="stMetricLabel"] {
    color: #6B7674 !important;
    font-size: 0.8rem !important;
}

/* ---- 見出し(サブヘッダー)を少しコンパクトに ---- */
h3 {
    font-size: 1.05rem !important;
    margin-bottom: 0.1rem !important;
}
</style>
"""


def inject():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
