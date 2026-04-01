from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional

from src.schemas.response import ExperimentResponse



class JobStatus(str, Enum):
    """ジョブの状態を定義する列挙型"""
    PENDING = "pending"     # 実行待ち
    RUNNING = "running"     # 実行中
    COMPLETED = "completed" # 完了
    FAILED = "failed"       # 失敗


class JobAcceptedResponse(BaseModel):
    job_id: str = Field(..., description="ジョブを一意に識別するID（UUIDなど）")
    status: str = Field("pending", description="現在のステータス (pending/running)")
    message: str = Field("学習ジョブを受け付けました", description="ユーザー向けメッセージ")


class JobStatusResponse(BaseModel):
    job_id: str
    status: str = Field(..., description="ステータス (pending/running/completed/failed)")
    progress: Optional[float] = Field(None, description="進捗率 (0.0~1.0)")


class JobDetailResponse(JobStatusResponse):
    result: Optional[ExperimentResponse] = None
    error: Optional[str] = None