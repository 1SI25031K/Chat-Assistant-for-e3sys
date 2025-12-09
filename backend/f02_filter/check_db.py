import sqlite3
import os

# さっきと同じ魔法で、隣のフォルダにあるDBを探します
current_dir = os.path.dirname(os.path.abspath(__file__))
# 一つ上の階層(backend) -> f03_persistence -> emysys.db
DB_PATH = os.path.join(os.path.dirname(current_dir), "f03_persistence", "emysys.db")

print(f"📂 データベースファイル: {DB_PATH}")
print("-" * 40)

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 保存されているデータをすべて取ってくるSQL
    cursor.execute("SELECT * FROM events")
    rows = cursor.fetchall()

    if not rows:
        print("📭 データはまだありません。")
    else:
        print(f"📊 現在 {len(rows)} 件のデータが保存されています:\n")
        for row in rows:
            # rowの中身: (id, user_id, text, tag, time)
            print(f"📝 ID: {row[0]} | 意図: {row[3]} | 内容: {row[2]}")

    conn.close()

except Exception as e:
    print(f"エラー: {e}")