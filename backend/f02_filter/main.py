import sys
import os
import json

# --- 魔法のコード: 隣のフォルダ(F-03)を見つけられるようにする ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# F-03 の保存機能と初期化機能をインポート
# try の中はインデント（字下げ）が必要です！
try:
    from f03_persistence.main import save_event, init_db
except ImportError:
    print("⚠️ エラー: F-03が見つかりません。backendフォルダの構成を確認してください。")
    # ダミー関数（エラー回避用）
    def save_event(data): return data
    def init_db(): pass


# ==========================================
# 1. データ受信シミュレーション
# ==========================================
mock_input_data = {
    "source": "slack",
    "event_id": "evt_combine_retry_02", # IDを変えておきました
    "user_id": "U12345",
    "text_content": "交通費精算のやり方を教えてください",
    "timestamp": "2023-12-05T10:00:00Z"
}

# ==========================================
# 2. 意図判定ロジック (F-02 Logic)
# ==========================================
def determine_intent(text):
    if "?" in text or "質問" in text or "教えて" in text:
        return "question"
    else:
        return "chat"

# ==========================================
# 3. メイン処理
# ==========================================
def main():
    # ★ エラー回避のため、最初にDBがあるか確認・作成する
    print("--- 🛠 DBチェック ---")
    init_db()
    
    print("\n--- 📥 [F-01] からデータを受信しました ---")
    processed_data = mock_input_data.copy()

    # STEP 1: 意図判定
    tag = determine_intent(processed_data["text_content"])
    processed_data["intent_tag"] = tag
    processed_data["status"] = "processed"
    print(f"⚙️ [F-02] 判定完了: {tag}")

    # STEP 2: DB保存 (F-03 Call)
    print("--- 💾 [F-03] へ保存を依頼します ---")
    # ここで F-03 の関数を呼び出します
    processed_data = save_event(processed_data)

    # STEP 3: 次へ
    print("\n--- 📤 [F-04] へ渡すデータ (完成形) ---")
    return processed_data

if __name__ == "__main__":
    result = main()
    print(json.dumps(result, indent=2, ensure_ascii=False))