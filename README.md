# QLLM Experiment Control System

量子計算（Quantum Neural Networks）を組み込んだ大規模言語モデル（LLM）の学習実験を管理・可視化するためのアプリケーションです。

## 概要

本システムは、LLMのファインチューニングにおける実験パラメータの管理、ジョブの実行、および学習結果の可視化を一元化することを目的としています。研究ワークフローにおける実験履歴の保存と、解析用グラフの出力を容易にします。

> [!NOTE]  
> **コアロジックについて** > バックエンドの量子計算（QLLM）エンジンおよび学習処理の実装は、研究の事情により本リポジトリでは**モック（ダミーロジック）**に差し替えられています。

## 主な機能

- **実験設定と投入**: モデル名、学習率、量子レイヤー数などのパラメータをGUIから設定し、ジョブを投入。
- **非同期ジョブ管理**: 学習処理をバックグラウンドで実行し、他の操作を妨げずに進捗を監視。
- **実験履歴の閲覧**: 過去に実行したジョブのステータス、進捗、パラメータを一覧表示。
- **結果の可視化と出力**: 学習曲線（Loss）をMatplotlibで描画し、解析用のPNG画像としてダウンロード。

## 技術スタック

- **Frontend**: Streamlit
- **Backend**: FastAPI (Python 3.12)
- **Container**: Docker / Docker Compose
- **Package Management**: Poetry

## ディレクトリ構成

```text
.
├── docker-compose.yml
├── Dockerfile             # API用
├── gui/
│   ├── Dockerfile         # GUI用
│   ├── main.py            # Streamlitメインロジック
│   └── api_client.py      # API通信用クライアント
├── src/
│   ├── main.py            # FastAPIエントリーポイント
│   ├── routers/           # APIエンドポイント定義
│   ├── schemas/           # Pydanticモデル（型定義）
│   └── services/          # 実験実行エンジン（Mock実装）
└── models/                # データ保存用ボリューム
```

## セットアップと起動

Dockerがインストールされている環境で、以下のコマンドを実行してください。

```bash
# ビルドと起動
docker compose up -d --build
```

起動後、以下のURLからアクセス可能です。
- **GUI**: `http://localhost:8501`
- **API Docs (Swagger UI)**: `http://localhost:8000/docs`