"""
Jobの定義
"""

from enum import Enum
from pydantic import BaseModel, Field
from sqlmodel import SQLModel, Field as SQLField
from sqlalchemy import Column, JSON
from typing import List, Optional



class JobStatus(str, Enum):
    """Jobの状態"""
    WAITING = "waiting"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TrainParams(BaseModel):
    """リクエストのハイパーパラメータ"""
    data_seed: int = Field(42, ge=0, description="データサンプリングのシード値")
    n_train: int = Field(4000, ge=1, description="学習データサンプル数")
    n_valid: int = Field(500, ge=1, description="バリデーションデータサンプル数")
    n_test: int = Field(500, ge=1, description="テストデータサンプル数")
    n_epoch: int = Field(10, ge=1, description="エポック数")
    lr: float = Field(2e-4, gt=0, description="学習率")


class ModelParams(BaseModel):
    """リクエストのモデルハイパーパラメータ"""
    params_seed: int = Field(42, ge=0, description="モデルパラメータ初期化時のシード値")
    token_length: int = Field(512, ge=1, description="予測トークン最大長")
    bond_dim: int = Field(4, ge=1, le=10, description="MPOのbond次元")
    hid_dim: int = Field(4, ge=1, le=10, description="中間次元(QNNモードでは量子ビット数)")
    n_layers: int = Field(1, ge=1, le=10, description="レイヤー数")


class TrainingStep(BaseModel):
    """各ステップの記録"""
    epoch: float = Field(..., description="エポック数")
    loss: float = Field(..., description="学習損失")
    grad_norm: Optional[float] = Field(None, description="勾配ノルム")


class EvaluationResults(BaseModel):
    """最終的な実行結果を定義"""
    eval_loss: float = Field(..., description="評価損失")
    total_time: float = Field(..., description="合計学習時間(分)")


class JobModel(SQLModel, table=True):
    """Jobのメインクラス"""
    job_id: str = SQLField(primary_key=True)
    exp_title: str = SQLField("Test experiment", description="実験タイトル")

    model_name: str = SQLField("facebook/opt-125m", description="使用するモデル名")
    use_qnn: bool = SQLField(True, description="QNN有効化設定")
    dataset: str = SQLField("wikitext", description="データセットを指定")

    status: JobStatus = SQLField(default=JobStatus.WAITING)
    progress: Optional[float] = SQLField(default=0.0, description="進捗率 (0.0~1.0)")
    ppl: Optional[float] = SQLField(default=None, description="Perplexity")

    train_params: TrainParams = SQLField(default_factory=TrainParams, sa_column=Column(JSON))
    model_params: ModelParams = SQLField(default_factory=ModelParams, sa_column=Column(JSON))
    history: List[TrainingStep] = SQLField(default_factory=list, sa_column=Column(JSON))
    evaluation: Optional[EvaluationResults] = SQLField(default=None, sa_column=Column(JSON))
