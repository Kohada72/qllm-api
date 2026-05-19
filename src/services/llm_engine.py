import asyncio
import random
import httpx
import os

from src.schemas.request import PredictionRequest
from src.schemas.job import JobStatus, TrainingStep, EvaluationResults

# 自分自身のAPIサーバーのアドレス（環境変数から取得、デフォルトはローカル）
API_URL = os.getenv("API_URL")

async def run_training_process(job_id: str, request: PredictionRequest):
    """
    重い学習処理をシミュレートし、API経由で進捗を報告するバックグラウンドタスク
    """
    # HTTPクライアントの準備
    async with httpx.AsyncClient(base_url=API_URL) as client:
        try:
            # 1. 状態を 'RUNNING' に更新
            await client.patch(f"/jobs/{job_id}", json={"status": JobStatus.RUNNING.value})
            
            epochs = request.train_params.epochs
            history = []

            # 2. 学習ループ
            for epoch in range(1, epochs + 1):
                await asyncio.sleep(2) 
                
                progress = epoch / epochs

                step = TrainingStep(
                    epoch=float(epoch),
                    loss=max(0.1, 4.0 - (epoch * 0.35) + random.uniform(-0.1, 0.1)),
                    learning_rate=request.train_params.lr * (0.9 ** epoch),
                    grad_norm=random.uniform(0.1, 0.5)
                )
                history.append(step.model_dump()) # PydanticモデルをDict化
                
                # 進捗と最新ログをAPI経由で更新
                await client.patch(f"/jobs/{job_id}", json={
                    "progress": progress,
                    "history": history
                })
                
                print(f"Job {job_id}: Epoch {epoch}/{epochs} completed.")

            # 3. 最終結果の組み立て
            evaluation = EvaluationResults(
                eval_loss=history[-1]["loss"] * 0.95,
                train_steps_per_second=10.5,
                perplexity=40.0 + random.uniform(-2.0, 2.0),
                total_training_time=(epochs * 2.0) / 60
            )

            # 4. 完了状態の送信
            await client.patch(f"/jobs/{job_id}", json={
                "status": JobStatus.COMPLETED.value,
                "progress": 1.0,
                "evaluation": evaluation.model_dump(),
                "ppl": evaluation.perplexity # 外出しした検索用カラム
            })

        except Exception as e:
            # 5. エラー時の処理
            print(f"Job {job_id} failed: {e}")
            await client.patch(f"/jobs/{job_id}", json={
                "status": JobStatus.FAILED.value,
                # エラーメッセージをログに残す設計があればここに追加
            })
