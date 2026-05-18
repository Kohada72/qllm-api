"""
全てのレスポンスを定義
"""

from pydantic import BaseModel, Field
from typing import List, Optional

from .job import JobStatus, TrainParams, ModelParams, TrainingStep, EvaluationResults  #.jobと指定するとモジュールの移動で壊れない



class AcceptedResponse(BaseModel):
    """受付返答用"""
    job_id: str = Field(..., description="Jobの識別id")
    exp_title: str = Field(..., description="Jobの識別タイトル")
    status: JobStatus = Field(JobStatus.WAITING, description="Jobの状態")


class StatusResponse(BaseModel):
    """一覧表示用"""
    job_id: str
    exp_title: str
    status: JobStatus = Field(JobStatus.WAITING, description="ステータス")
    progress: Optional[float] = Field(None, description="進捗率 (0.0~1.0)")
    ppl: Optional[float] = Field(None, description="Perplexity")


class DetailResponse(StatusResponse):
    """詳細表示用"""
    train_params: TrainParams = Field(..., description="トレーニングパラメータ")
    model_params: ModelParams = Field(..., description="モデルパラメータ")
    history: List[TrainingStep] = Field(list, description="学習過程")
    evaluation: Optional[EvaluationResults] = Field(None, description="最終結果")