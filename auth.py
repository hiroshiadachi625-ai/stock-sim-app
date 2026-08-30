# -*- coding: utf-8 -*-
"""
簡易パスワード認証。

個人専用アプリをクラウド(Streamlit Community Cloud等)にデプロイすると、
URLを知っている人なら誰でもアクセスできてしまう。プラットフォーム側の
アクセス制限機能と合わせて、アプリ自体にも簡易的なパスワードロックを
かけられるようにしている。

- st.secrets に APP_PASSWORD が設定されている場合のみ、パスワード入力を求める。
- ローカルでの個人利用時など、APP_PASSWORD が未設定の場合は認証をスキップする
  (自分のPCで動かすだけなら不要なため)。
"""
import streamlit as st


def _get_configured_password():
    try:
        return st.secrets.get("APP_PASSWORD")
    except Exception:
        return None


def require_password():
    """必要ならパスワード入力画面を表示し、未認証ならここで処理を止める。"""
    configured_password = _get_configured_password()
    if not configured_password:
        # パスワード未設定(ローカル個人利用など)の場合は素通り
        return

    if st.session_state.get("authenticated"):
        return

    st.title("🔒 ログイン")
    st.caption("このアプリは個人専用です。パスワードを入力してください。")
    pw = st.text_input("パスワード", type="password")
    if st.button("ログイン"):
        if pw == configured_password:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("パスワードが違います。")
    st.stop()
