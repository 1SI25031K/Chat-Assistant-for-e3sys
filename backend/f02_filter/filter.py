import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv
from backend.common.models import SlackMessage

# ロガー設定
logger = logging.getLogger(__name__)

# .env 読み込み
load_dotenv()

def analyze_intent(input_message: SlackMessage) -> SlackMessage:
    """
    [F-02] 意図判定 (Intent Classification)
    APIキーがない場合は、開発現場のあらゆる単語を網羅した
    「超・広範囲キーワードリスト」でバックアップ判定を行う。
    """
    logger.info(f"--- [F-02] Analyzing Intent for: {input_message.event_id} ---")

    text = input_message.text_content
    api_key = os.environ.get("GEMINI_API_KEY")

    # ---------------------------------------------------------
    # 1. APIキーがない場合の「キーワード判定 (超・完全版)」
    # ---------------------------------------------------------
    if not api_key:
        logger.warning("⚠️ API Key not found. Fallback to massive keyword matching.")
        
        # 開発現場で飛び交うあらゆる「質問・トラブル・依頼・技術用語」
        keywords = [
            # --------------------------
            # 🆘 SOS・疑問・依頼・感情
            # --------------------------
            "?", "？", "ですか", "ますか", "教えて", "教えろ", "願います", "頼む", "お願いします",
            "どうすれば", "どうやる", "方法", "仕方", "手順", "やり方", 
            "分からない", "わからん", "不明", "なにこれ", "何これ", "why", "what", "how",
            "help", "ヘルプ", "助けて", "詰んだ", "詰まってる", "進まない", "終わらない",
            "緊急", "至急", "早急", "なる早", "asap", "urgent",
            "相談", "確認", "共有", "提案", "検討", "レビュー", "review",
            
            # --------------------------
            # 💥 エラー・不具合・異常
            # --------------------------
            "error", "エラー", "exception", "例外", "fail", "failed", "failure", "失敗",
            "bug", "バグ", "不具合", "defect", "incident", "インシデント", "障害",
            "crash", "クラッシュ", "落ちる", "落ちた", "止まる", "止まった", "フリーズ", "hang",
            "broken", "break", "壊れた", "動かない", "反応しない",
            "おかしい", "変", "strange", "weird", "odd", "unexpected", "予期せぬ",
            "timeout", "timed out", "タイムアウト", "重い", "遅い", "latency",
            
            # --------------------------
            # 🐍 Python / コード関連
            # --------------------------
            "import", "install", "pip", "conda", "venv", "virtualenv",
            "syntax", "indentation", "indent", "インデント", "構文",
            "type", "型", "int", "str", "list", "dict", "none", "null", "undefined",
            "function", "def", "class", "method", "argument", "param", "引数", "戻り値", "return",
            "traceback", "stacktrace", "スタックトレース",
            "keyerror", "valueerror", "typeerror", "indexerror", "nameerror", "attributeerror",
            
            # --------------------------
            # 🐙 Git / バージョン管理
            # --------------------------
            "git", "github", "gitlab", "commit", "push", "pull", "fetch", "clone",
            "merge", "マージ", "rebase", "リベース", "conflict", "コンフリクト", "競合",
            "branch", "ブランチ", "checkout", "stash", "reset", "revert", "cherry-pick",
            "diff", "差分", "pr", "pull request", "プルリク",
            
            # --------------------------
            # ☁️ インフラ / ネットワーク / DB
            # --------------------------
            "aws", "s3", "ec2", "lambda", "cloud", "gcp", "azure",
            "docker", "container", "image", "compose", "build", "ビルド",
            "deploy", "デプロイ", "release", "リリース", "rollback", "ロールバック",
            "env", "環境変数", "config", "設定", "conf", "yaml", "json", "xml",
            "connect", "接続", "connection", "refused", "denied", "network", "wifi",
            "dns", "ip", "port", "ポート", "ssh", "sudo", "permission", "権限", "access",
            "db", "database", "sql", "mysql", "postgres", "sqlite", "query", "select", "insert",
            "table", "column", "record", "data", "migration", "マイグレーション",
            
            # --------------------------
            # 🌐 Web / API / HTTP
            # --------------------------
            "http", "https", "url", "uri", "link", "リンク",
            "404", "500", "403", "401", "200", "status", "code",
            "api", "endpoint", "エンドポイント", "rest", "graphql",
            "get", "post", "put", "delete", "patch",
            "header", "body", "payload", "cookie", "session", "cache", "キャッシュ",
            "cors", "authentication", "auth", "login", "ログイン", "token", "key"
        ]
        
        # 究極の any() 判定
        # lower() で小文字化してからチェックするので "Python" も "PYTHON" も "python" も拾います
        text_lower = text.lower()
        is_question = any(k in text_lower for k in keywords)

        if is_question:
            input_message.intent_tag = "question"
        else:
            input_message.intent_tag = "chat"
            
        logger.info(f"🔑 Massive Keyword Match Result: {input_message.intent_tag}")
        return input_message

    # ---------------------------------------------------------
    # 2. Geminiを使った高度な判定
    # ---------------------------------------------------------
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
        あなたはSlackボットの「意図判定」システムです。
        以下のメッセージを読み、それが「回答が必要な質問・相談・エラー報告」か「ただの雑談・挨拶」か分類してください。
        
        メッセージ: "{text}"
        
        出力ルール:
        - 質問、作業依頼、エラー報告なら "question" とだけ出力してください。
        - 挨拶、相槌、独り言なら "chat" とだけ出力してください。
        - 余計な説明は一切不要です。単語一つだけを返してください。
        """

        response = model.generate_content(prompt)
        intent = response.text.strip().lower()
        
        if "question" in intent:
            final_tag = "question"
        else:
            final_tag = "chat"

        logger.info(f"🤖 AI Judgment: '{text}' => {final_tag}")

        input_message.intent_tag = final_tag
        return input_message

    except Exception as e:
        logger.error(f"❌ Intent Analysis Error: {e}")
        # エラー時は念のため質問として扱う
        input_message.intent_tag = "question"
        return input_message