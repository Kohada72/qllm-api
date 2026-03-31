from pydantic import BaseModel, Field
from typing import List, Optional



class TrainingStep(BaseModel):
    epoch: float = Field(..., description="エポック数")
    loss: float = Field(..., description="学習損失")
    learning_rate: float = Field(..., description="学習率")
    grad_norm: Optional[float] = Field(None, description="勾配ノルム")


class EvaluationResults(BaseModel):
    eval_loss: float = Field(..., description="評価損失")
    train_steps_per_second: float = Field(..., description="1秒あたりのステップ処理数")
    perplexity: float = Field(..., description="Perplexity")
    total_training_time: float = Field(..., description="合計学習時間(分)")


class ExperimentResponse(BaseModel):
    status: str = Field("success", description="処理ステータス")
    
    history: List[TrainingStep] = Field(..., description="学習過程")
    evaluation: EvaluationResults = Field(..., description="評価結果")