import os
import sys
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

# プロジェクトのルートディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../")

from backend.common.models import FeedbackResponse

# 環境変数の読み込み
load_dotenv()

# Slackクライアントの初期化
slack_token = os.getenv("SLACK_BOT_TOKEN")
client = WebClient(token=slack_token)

def send_reply(response: FeedbackResponse, channel_id: str) -> bool:

    print(f"--- 📤 [F-06] Sending Reply to Channel: {channel_id} ---")

    try:
        # メッセージ送信の実行
        result = client.chat_postMessage(
            channel=channel_id,
            text=response.feedback_summary,
            thread_ts=response.ts # スレッド返信
        )
        
        if result["ok"]:
            print(f"✅ Message sent successfully to {channel_id}")
            return True
        else:
            print(f"❌ Message sent but marked as failed: {result}")
            return False

    except SlackApiError as e:
        print(f"❌ Slack API Error: {e.response['error']}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected Error in F-06: {e}")
        return False

# 単体テスト用ブロック
if __name__ == "__main__":
    print("🚀 F-06 Standalone Test")
    
    # テストする時はここに「C」から始まるチャンネルIDを入れてください
    TEST_CHANNEL_ID = "C0A1XF35V4N" # あなたのログにあったチャンネルID
    
    if slack_token:
        test_data = FeedbackResponse(
            event_id="TEST_NOTIFY_001",
            target_user_id="dummy_user",
            feedback_summary="【F-06テスト】チャンネルへの返信テストです。",
            status="complete"
        )
        
        # 引数にチャンネルIDを渡して実行
        send_reply(test_data, TEST_CHANNEL_ID)
    else:
        print("⚠️ SLACK_BOT_TOKEN が設定されていません")