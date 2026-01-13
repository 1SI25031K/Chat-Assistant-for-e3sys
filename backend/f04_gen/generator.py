# backend/f04_gen/generator.py
import os
from google import genai
from dotenv import load_dotenv
from backend.common.models import SlackMessage, FeedbackResponse

# 1. 環境変数の読み込み
load_dotenv()

# 2. Gemini APIの設定 (新ライブラリ版)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("⚠️ GEMINI_API_KEY が設定されていません")

# 新しいクライアントの初期化
client = genai.Client(api_key=GEMINI_API_KEY)

# backend/f04_gen/generator.py

# ... (既存のインポートやクライアント初期化はそのまま) ...

def generate_feedback(message: SlackMessage, context: str = "") -> FeedbackResponse:
    """
    [F-04] AIフィードバック生成 (RAG対応版)
    context 引数を通じて、DynamoDBから取得した過去ログをプロンプトに注入します。
    """
    print(f"--- [F-04] Gemini Thinking with Context... (Intent: {message.intent_tag}) ---")

    try:
        # 1. プロンプト（命令文）の構築
        system_instruction = """
あなたは高度なエンジニアリング・コミュニケーションの専門家「E3-Assist」です。
Slack上の質問者と回答者のやり取りを解析し、両者の技術的成長を最大化するためのフィードバックを提供してください。

### 役割
- 過去のやり取り（コンテキスト）を踏まえ、一貫性のあるアドバイスをすること。
- 以前教えたことが守られているか、あるいは進歩しているかを評価すること。

### 制約事項
- 挨拶、絵文字は一切禁止。
- 結論から述べ、箇条書きで簡潔に構成すること。
- 「優しさ」よりも「改善点の具体性」を優先すること。

### 出力フォーマット
【スコア】質問: X/10, 回答: X/10
【これまでの流れを踏まえた評価】
- (過去ログとの関連性や、会話の進捗に対する評価)
【今回のメッセージへの改善点】
- (具体的な改善アクション)
        """
        
        # 2. 過去の文脈（RAG）と現在のメッセージを結合
        user_query = f"""
        【これまでの会話の流れ】
        {context if context else "（過去のやり取りはありません）"}
        
        【今回のユーザーの状況】
        ユーザーID: {message.user_id}
        意図タグ: {message.intent_tag}
        
        【今回のメッセージ内容】
        {message.text_content}
        """
        
        # 3. 生成実行
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"{system_instruction}\n\n{user_query}"
        )
        
        ai_text = response.text.strip()

        return FeedbackResponse(
            event_id=message.event_id,
            target_user_id=message.user_id,
            feedback_summary=ai_text,
            status="complete"
        )

    except Exception as e:
        print(f"Gemini API Error: {e}")
        # ... (エラー処理はそのまま) ...

# 🧪 単体テスト用
if __name__ == "__main__":
    print("🚀 F-04 Gemini Connection Test (New Client)")
    
    # テストデータ
    test_msg = SlackMessage(
        event_id="TEST_GEN_002",
        user_id="U_TEST_LEADER",
        text_content="Pythonの新しいライブラリへの移行について、メリットを教えて。",
        intent_tag="question",
        status="pending"
    )
    
    # 実行
    result = generate_feedback(test_msg)
    
    print("\n生成された回答:")
    print("--------------------------------------------------")
    print(result.feedback_summary)
    print("--------------------------------------------------")