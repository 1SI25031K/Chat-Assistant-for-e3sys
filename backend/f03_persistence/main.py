# backend/f03_persistence/main.py
# ↑このファイルの中身を、以下にすべて書き換えてください

import sqlite3
import json
import os

# --- 【重要】DBの場所を絶対パスで固定する ---
# どこから実行しても、必ずこの main.py と同じフォルダに db を作らせる魔法の記述
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "emysys.db")

def init_db():
    """
    データベースとテーブルを初期化する関数
    """
    # 固定したパス(DB_PATH)を使用
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            text_content TEXT,
            intent_tag TEXT,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()
    # どこに作ったかを表示するように変更
    print(f"✅ [Init] DB準備完了: {DB_PATH}")

def save_event(data):
    """
    JSONデータを受け取り、DBに保存し、そのままデータを返す関数
    """
    # 念のため、保存する直前にテーブルがあるか確認（安全策）
    # ※本来は起動時に一度だけやるのが良いですが、安全重視でここに簡易チェックを入れます
    if not os.path.exists(DB_PATH):
        init_db()
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        sql = """
            INSERT INTO events (id, user_id, text_content, intent_tag, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """

        record = (
            data.get("event_id"),
            data.get("user_id"),
            data.get("text_content"),
            data.get("intent_tag"),
            data.get("timestamp")
        )

        cursor.execute(sql, record)
        conn.commit()
        print(f"💾 [Save] DB保存成功: {data.get('event_id')}")

    except sqlite3.IntegrityError:
        print(f"⚠️ [Skip] データ重複: {data.get('event_id')}")
    except sqlite3.OperationalError as e:
        # テーブルがないエラーをキャッチした場合、初期化を試みる
        print(f"⚠️ [Retry] テーブルが見つかりません。初期化を試みます... ({e})")
        init_db()
        # 再帰呼び出しは無限ループの危険があるため、今回はエラーとして通過させる
    except Exception as e:
        print(f"❌ [Error] 保存失敗: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

    return data

# --- 動作確認用 ---
if __name__ == "__main__":
    print("--- F-03 Test ---")
    init_db()
    # テストデータ省略