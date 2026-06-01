"""
メインルータ
"""

import uuid
from typing import List
from fastapi import APIRouter, BackgroundTasks, HTTPException, Response, status, Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.schemas.request import PredictionRequest, JobUpdateRequest
from src.schemas.response import AcceptedResponse, StatusResponse, DetailResponse
from src.schemas.job import JobModel, JobStatus
from src.services.handler import run_training_process
from ..database import get_session



router = APIRouter(
    prefix="/experiments",
    tags=["Experiments"],
)

@router.post("", response_model=AcceptedResponse, status_code=status.HTTP_202_ACCEPTED
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
        train_params=request.train_params.model_dump(),
        model_params=request.model_params.model_dump()
    )

    session.add(new_job)
    await session.commit()
    await session.refresh(new_job)

    background_tasks.add_task(
        run_training_process,
        new_job_id,
        request
    )

    return AcceptedResponse(
        job_id=new_job_id,
        exp_title=new_job.exp_title
    )


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


@router.patch("/{job_id}", response_model=JobModel)
async def update_job_status(
    job_id: str,
    update_data: JobUpdateRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    engineからJobの結果を更新する
    """
    job = await session.get(JobModel, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="ジョブが見つかりません")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, val in update_dict.items():
        setattr(job, key, val)
    
    session.add(job)
    await session.commit()
    await session.refresh(job)

    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_experiment(job_id: str, session: AsyncSession = Depends(get_session)):
    """
    ジョブの削除
    """
    job = await session.get(JobModel, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="ジョブが見つかりません")
    
    await session.delete(job)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
