# QLLM Experiment Control System

量子計算（Quantum Neural Networks）を組み込んだ大規模言語モデル（LLM）のファインチューニング実験を、効率的に管理・可視化するためのフルスタック・ダッシュボード・システムです。

## 📋 プロジェクト概要

本プロジェクトは、研究における試行錯誤のサイクルを高速化するために開発されました。複雑なハイパーパラメータの設定、長時間の学習ジョブの非同期管理、およびリアルタイムの進捗監視を、一貫したWebインターフェースを通じて提供します。

### 採用担当者様・開発者の方へ
本リポジトリは、以下のエンジニアリング・スキルを示すために公開しています：
* **コンテナオーケストレーション**: Docker Composeを用いた複数サービスの分離と連携。
* **API設計**: FastAPIによるRESTfulで型安全なAPI設計と非同期処理（Background Tasks）の実装。
* **モダンなUI/UX**: Streamlitを活用した、データサイエンティストにとって実用的なダッシュボードの構築。
* **クリーンアーキテクチャの意識**: スキーマ、ルーター、ロジック（サービス層）を分離した保守性の高いディレクトリ構成。

> [!IMPORTANT]  
> **コアロジックに関する注記** > バックエンドの量子計算エンジン（QLLM）および学習ロジックは、現在進行中の研究内容を含み機密性が高いため、本公開リポジトリでは**モック（ダミーロジック）に差し替えられています**。システムのアーキテクチャおよびインターフェースの設計思想を中心にご確認ください。

---

## 🏗 システム構成図



* **Frontend**: Streamlit (Python) - 実験パラメータ入力、ジョブ一覧、グラフ表示。
* **Backend**: FastAPI (Python 3.12) - ジョブ管理、非同期実行エグゼキューター。
* **Infrastructure**: Docker / Docker Compose - 環境の完全な再現性を保証。
* **Package Management**: Poetry - 依存関係の厳密な管理。

---

## 🚀 クイックスタート

Dockerがインストールされている環境であれば、以下のコマンドのみでシステムが立ち上がります。

```bash
# リポジトリのクローン
git clone https://github.com/[Your-ID]/qllm-api.git
cd qllm-api

# コンテナのビルドと起動
docker compose up -d --build
```

起動後、ブラウザから以下のURLにアクセスしてください：
* **GUI (Streamlit)**: `http://localhost:8501`
* **API Documentation (Swagger UI)**: `http://localhost:8000/docs`

---

## 🛠 ディレクトリ構造

```text
.
├── docker-compose.yml
├── api/
│   └── Dockerfile         # FastAPI環境
├── gui/
│   ├── Dockerfile         # Streamlit環境
│   ├── main.py            # ダッシュボードUI
│   └── api_client.py      # API通信クラス
├── src/                   # バックエンドソースコード
│   ├── main.py            # APIエントリーポイント
│   ├── routers/           # エンドポイント定義
│   ├── schemas/           # Pydanticモデル（型定義）
│   └── services/          # ビジネスロジック
│       └── llm_engine.py  # 実験エンジン（※現在はMock）
└── models/                # 学習済みモデル・ウェイト保存用
```

---

## 💡 設計のこだわり

### 1. 「軽量な一覧」と「詳細データ」の分離
実験数が増えた際のパフォーマンスを考慮し、API設計においてジョブ一覧取得（Summary）と、グラフデータを含む個別取得（Detail）のエンドポイントを分離しました。これにより、GUI側のレスポンスを軽快に保っています。

### 2. スキーマ駆動開発
Pydanticを用いた型定義をフロントエンドとバックエンドの共通言語とすることで、データの整合性を担保しています。

### 3. 研究効率を最大化するUI
研究者が最も注視する **Perplexity ($PP$)** などの指標を、`st.metric` を用いて直感的に把握できるレイアウトを採用しました。
$$PP = \exp(\text{loss})$$