## 現状のディレクトリ構想
'''Plaintext
.
├── .env
├── .env.example
├── .gitignore
├── README.md
├── docker-compose.yml    # APIとGUIを繋ぐオーケストレーション
├── pyproject.toml        # Poetryの依存関係管理
│
├── api/                  # FastAPI本体
│   ├── main.py           # アプリの起動エントリーポイント
│   ├── core/
│   │   └── config.py     # 設定管理、共通定数
│   ├── routers/
│   │   └── experiments.py
│   ├── schemas/
│   │   ├── job.py        # 出力：ジョブを投げた直後のフィードバック
│   │   ├── request.py    # 入力：LLM/量子パラメータのグループ化
│   │   └── response.py   # 出力：結果の構造化
│   └── services/
│       ├── llm_engine.py     # LLMの推論処理
│       └── quantum_engine.py # PennyLane/QTHA.pyのロジック
│
├── gui/                  # Streamlit本体
│   ├── main.py           # 画面構成とAPI呼び出し
│   └── components/       # 再利用可能なUIパーツ（グラフ表示等）
│
├── models/               # LLMモデルウェイト保存用（Git LFSまたは手動配置）
│
└── tests/                # 自動テスト（pytest）
    └── test_api.py       # 前の手順で作ったAsyncClientによるテスト


.
|____Dockerfile
|____pyproject.toml
|____models
|____.devcontainer
|____README.md
|____.dockerignore
|____.gitignore
|____.env
|____docker-compose.yml
|____poetry.lock
|____.git
|____src
  |____routers
  | |______init__.py
  | |____experiments.py
  |____core
  | |____config.py
  | |______init__.py
  |______init__.py
  |____schemas
  | |____job.py
  | |____request.py
  | |______init__.py
  | |____response.py
  |____main.py
  |____services
    |____llm_engine.py
    |______init__.py
'''