import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

# 自分のプロジェクトからインポート
from src.main import app         # FastAPIのインスタンス
from src.routers.database import get_session  # 本番用の依存関数

# ==========================================
# 1. テスト用データベースの準備
# ==========================================
# :memory: を指定して、メモリ上に一時的なDBを作成
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)

# テスト用の窓口（セッション）
async def get_test_session():
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

# ★ ここが魔法！本番の get_session を get_test_session にすり替える
app.dependency_overrides[get_session] = get_test_session


# ==========================================
# 2. テスト環境のセットアップ (Fixture)
# ==========================================
@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    """各テストの前にテーブルを作成し、終わったら削除する"""
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    yield  # ここでテストが実行される
    
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


# ==========================================
# 3. 実際のテストケース
# ==========================================
@pytest.mark.asyncio
async def test_create_and_list_jobs():
    """ジョブを作成し、一覧に反映されるかテストする"""
    
    # 非同期用のクライアントを作成
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        
        # ① ジョブ作成のPOSTリクエストを送信
        mock_payload = {
            "exp_title": "Test Experiment",
            "train_params": {
                "model_name": "test-model",
                "dataset": "test-data",
                "epochs": 5
            },
            "model_params": {
                "use_qnn": True
            }
        }
        
        post_response = await client.post("/experiments", json=mock_payload)
        assert post_response.status_code == 202
        
        # レスポンスからIDを取得
        created_job = post_response.json()
        assert "job_id" in created_job
        assert created_job["exp_title"] == "Test Experiment"
        
        # ② 一覧取得のGETリクエストを送信
        get_response = await client.get("/experiments")
        assert get_response.status_code == 200
        
        jobs_list = get_response.json()
        assert len(jobs_list) == 1  # 1件登録されているはず
        assert jobs_list[0]["job_id"] == created_job["job_id"]