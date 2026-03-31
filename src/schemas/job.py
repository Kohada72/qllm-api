from pydantic import BaseModel, Field
from typing import Optional



class JobAcceptedResponse(BaseModel):
    job_id: str = Field(..., description="ジョブを一意に識別するID（UUIDなど）")
    status: str = Field("pending", description="現在のステータス (pending/running)")
    message: str = Field("学習ジョブを受け付けました", description="ユーザー向けメッセージ")


class JobStatusResponse(BaseModel):
    job_id: str
    status: str = Field(..., description="ステータス (pending/running/completed/failed)")
    progress: Optional[float] = Field(None, description="進捗率 (0.0~1.0)")
    result: Optional[dict] = None 
    error: Optional[str] = None