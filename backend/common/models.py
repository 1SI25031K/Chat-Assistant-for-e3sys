from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class SlackMessage:
    event_id: str
    user_id: str
    text_content: str
    channel_id: str
    ts: str # Slackのメッセージタイムスタンプ
    source: str = "slack"
    intent_tag: Optional[str] = None
    status: str = "pending"

    @classmethod
    def from_dict(cls, data: dict):
        """辞書形式(JSON)からクラスを生成する"""
        return cls(**data)

    def to_dict(self):
        """クラスを辞書形式(JSON用)に変換する"""
        return asdict(self)


@dataclass
class FeedbackResponse:
    event_id: str
    target_user_id: str
    ts: str  # 返信先のスレッドIDとして使用
    feedback_summary: str
    status: str = "complete"

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

    def to_dict(self):
        return asdict(self)