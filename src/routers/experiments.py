from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from typing import List, Dict
import uuid

from src.schemas.request import PredictionRequest
from src.schemas.job import JobAcceptedResponse, JobStatusResponse, JobDetailResponse, JobStatus
from src.services.llm_engine import run_training_process



router = APIRouter(
    prefix="/experiments",
    tags=["Experiments"],
)

# 簡易DB: dev
jobs_store: Dict[str, dict] = {}


@router.post(
    "", 
    response_model=JobAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED
)
async def create_experiment(
    request: PredictionRequest,
    background_tasks: BackgroundTasks
):
    """
    学習・実験ジョブを発行します。
    重い処理はバックグラウンドで実行され、即座にJob IDを返します。
    """
    job_id = str(uuid.uuid4())
    
    # 初期ステータスを保存
    jobs_store[job_id] = {
        "job_id": job_id,
        "status": JobStatus.PENDING,
        "progress": 0.0,
        "result": None
    }

    # バックグラウンドタスクの登録
    # 実際の学習ロジック（run_training_process）を非同期で走らせる
    background_tasks.add_task(
        run_training_process,
        job_id,
        request,
        jobs_store
    )

    return JobAcceptedResponse(job_id=job_id)


@router.get("", response_model=List[JobStatusResponse])
async def list_experiments():
    """
    過去に発行したジョブの一覧を取得します。
    """
    return [JobStatusResponse(**data) for data in jobs_store.values()]


@router.get("/{job_id}", response_model=JobDetailResponse)
async def get_experiment_status(job_id: str):
    """
    指定したJob IDの進捗状況や結果を取得します。
    """
    job_data = jobs_store.get(job_id)
    if not job_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ジョブが見つかりません"
        )
    
    return JobDetailResponse(**job_data)