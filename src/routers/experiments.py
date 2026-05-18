"""
メインルータ
"""

import uuid
from typing import List
from fastapi import APIRouter, BackgroundTasks, HTTPException, status, Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.schemas.request import PredictionRequest
from src.schemas.response import AcceptedResponse, StatusResponse, DetailResponse
from src.schemas.job import JobModel, JobStatus
from src.services.llm_engine import run_training_process
from .database import get_session



router = APIRouter(
    prefix="/experiments",
    tags=["Experiments"],
)

@router.post(
    "", 
    response_model=AcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED
)
async def create_experiment(
    request: PredictionRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session)
):
    """
    ジョブの発行
    バックグラウンドで実行しアクセプトメッセージが返る
    """
    new_job_id = str(uuid.uuid4())

    new_job = JobModel(
        job_id=new_job_id,
        status=JobStatus.WAITING,
        **request.model_dump(exclude={"train_params", "model_params"}),
        train_params=request.train_params,
        model_params=request.model_params
    )

    session.add(new_job)
    await session.commit()
    await session.refresh(new_job)

    background_tasks.add_task(
        run_training_process,
        new_job
    )

    return AcceptedResponse(job_id=new_job_id)


@router.get("", response_model=List[StatusResponse])
async def list_experiments(session: AsyncSession = Depends(get_session)):
    """
    ジョブの一覧を取得
    """
    statement = select(JobModel)
    result = await session.exec(statement)
    jobs = result.all()
    return jobs


@router.get("/{job_id}", response_model=DetailResponse)
async def get_experiment_status(job_id: str, session: AsyncSession = Depends(get_session)):
    """
    指定したJob IDの進捗状況や結果を取得
    """
    job = await session.get(JobModel, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ジョブが見つかりません"
        )
    
    return job