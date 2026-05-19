"""
全てのリクエストを定義
"""

from typing import Optional, List
from pydantic import BaseModel, Field

from .job import TrainParams, ModelParams, JobStatus, TrainingStep, EvaluationResults



class PredictionRequest(BaseModel):
    """メインリクエスト"""
    exp_title: str
    model_name: str = Field("facebook/opt-125m", description="使用するモデル名")
    use_qnn: bool = Field(True, description="QNN有効化設定")
    dataset: str = Field("wikitext", description="データセットを指定")
    train_params: TrainParams = Field(default_factory=TrainParams)
    model_params: ModelParams = Field(default_factory=ModelParams)


class JobUpdateRequest(BaseModel):
    """core engine側から進捗データを受け取るスキーマ"""
    status: Optional[JobStatus] = None
    progress: Optional[float] = None
    history: Optional[List[TrainingStep]] = None
    evaluation: Optional[EvaluationResults] = None
    ppl: Optional[float] = None