import os
import traceback
import httpx

from src.schemas.request import PredictionRequest
from src.schemas.job import JobStatus
from src.services.trainer import execute_training



API_URL = os.getenv("API_URL")
ERROR_LOG_FILE_PATH = "error.log"

async def run_training_process(job_id: str, request: PredictionRequest):
    """
    APIとの通信やエラーハンドリングを担うHandler層
    """
    history = []

    # Trainerに渡すための「進捗報告用コールバック関数」を定義
    async def progress_callback(epoch: int, loss: float, lr: float, grad_norm: float):
        # APIの要求仕様に合わせてデータを整形し、historyに蓄積
        progress = epoch / request.train_params.n_epoch
        
        step_data = {
            "epoch": float(epoch),
            "loss": loss,
            "learning_rate": lr,
            "grad_norm": grad_norm
        }
        history.append(step_data)

        # APIへPATCH送信
        async with httpx.AsyncClient(base_url=API_URL) as client:
            await client.patch(f"/experiments/{job_id}", json={
                "progress": progress,
                "history": history
            })


    # メインの実行ブロック
    async with httpx.AsyncClient(base_url=API_URL) as client:
        try:
            # 1. 状態を 'RUNNING' に更新
            await client.patch(f"/experiments/{job_id}", json={"status": JobStatus.RUNNING.value})
            
            # 2. スキーマからプリミティブな値を抽出し、純粋な学習ロジックを実行
            #    先ほど定義した progress_callback を渡す
            result = await execute_training(
                epochs=request.train_params.n_epoch,
                lr=request.train_params.lr,
                model_name=request.model_name,
                on_step=progress_callback
            )

            # 3. 完了状態の送信 (Trainerから返ってきた結果をAPIスキーマにはめ込む)
            await client.patch(f"/experiments/{job_id}", json={
                "status": JobStatus.COMPLETED.value,
                "progress": 1.0,
                "evaluation": {
                    "eval_loss": result["eval_loss"],
                    "total_time": result["total_time"]
                },
                "ppl": result["ppl"]
            })

        except Exception as e:
            # 4. エラー時の処理（ログファイルへの書き出しとFAILED送信）
            print(f"Job {job_id} failed: {e}")
            try:
                with open(ERROR_LOG_FILE_PATH, "w", encoding="utf-8") as f:
                    f.write(f"=== Job ID: {job_id} ===\n")
                    f.write(f"Error Message: {str(e)}\n\n")
                    f.write("=== 詳細なスタックトレース (Traceback) ===\n")
                    traceback.print_exc(file=f)
            except Exception as file_err:
                print(f"Failed to write log file: {file_err}")

            await client.patch(f"/experiments/{job_id}", json={
                "status": JobStatus.FAILED.value,
            })
