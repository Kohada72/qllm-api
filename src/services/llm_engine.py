import asyncio
import random
from datetime import datetime

from src.schemas.request import PredictionRequest
from src.schemas.response import ExperimentResponse, TrainingStep, EvaluationResults
from src.schemas.job import JobStatus



async def run_training_process(job_id: str, request: PredictionRequest, jobs_store: dict):
    """
    重い学習処理をシミュレートするバックグラウンドタスク。
    jobs_store を直接更新することで、Router側から進捗が見えるようにする。
    """
    try:
        # 1. 状態を 'running' に更新
        jobs_store[job_id]["status"] = JobStatus.RUNNING
        
        epochs = request.train_params.epochs
        history = []

        # 2. 学習ループのシミュレーション
        for epoch in range(1, epochs + 1):
            # 実際の学習の代わりにスリープ（開発中は短めに設定）
            # 本番ではここが 1エポック数分〜数十分になる
            await asyncio.sleep(2) 
            
            # 進捗率の計算
            progress = epoch / epochs
            jobs_store[job_id]["progress"] = progress

            # ダミーのメトリクスを作成
            step = TrainingStep(
                epoch=float(epoch),
                loss=max(0.1, 4.0 - (epoch * 0.35) + random.uniform(-0.1, 0.1)),
                learning_rate=request.train_params.lr * (0.9 ** epoch),
                grad_norm=random.uniform(0.1, 0.5)
            )
            history.append(step)
            
            # ログ出力（コンテナのログで確認用）
            print(f"Job {job_id}: Epoch {epoch}/{epochs} completed. Progress: {progress:.2%}")

        # 3. 最終結果の組み立て
        evaluation = EvaluationResults(
            eval_loss=history[-1].loss * 0.95,
            train_steps_per_second=10.5,
            perplexity=40.0 + random.uniform(-2.0, 2.0),
            total_training_time=(epochs * 2.0) / 60
        )

        result = ExperimentResponse(
            status="success",
            history=history,
            evaluation=evaluation,
        )

        # 4. 完了状態をストアに保存
        jobs_store[job_id]["status"] = JobStatus.COMPLETED
        jobs_store[job_id]["result"] = result.model_dump() # Pydanticモデルを辞書に変換

    except Exception as e:
        # エラーハンドリング
        jobs_store[job_id]["status"] = JobStatus.FAILED
        jobs_store[job_id]["error"] = str(e)
        print(f"Job {job_id} failed: {e}")