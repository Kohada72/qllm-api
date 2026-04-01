import streamlit as st
import os
from api_client import QLLMApiClient



# APIクライアントの初期化（環境変数からURL取得）
API_URL = os.getenv("API_URL", "http://api:8000")
client = QLLMApiClient(API_URL)

st.set_page_config(page_title="QLLM Experiment Control", layout="wide")
st.title("🧪 Quantum-LLM Experiment Dashboard")


# --- サイドバー：基本設定 ---
with st.sidebar:
    st.header("Base Settings")
    model_name = st.text_input("LLM Model", value="facebook/opt-125m")
    data_set = st.selectbox("Dataset", ["wikitext", "ptb", "custom"])
    st.divider()
    if st.button("Check API Status"):
        st.write("Healthy" if client.is_healthy() else "Unreachable")


# --- メインエリア：パラメータ入力 ---
# スキーマの構造（Train/Model）に合わせて2列に分割
col1, col2 = st.columns(2)

with col1:
    st.subheader("🚀 Training Parameters")
    with st.container(border=True):
        train_seed = st.number_input("Train Seed", value=42)
        data_seed = st.number_input("Data Seed", value=42)
        n_train = st.number_input("Train Samples", value=4000, step=100)
        epochs = st.slider("Epochs", 1, 100, 10)
        lr = st.number_input("Learning Rate", value=2e-4, format="%.1e")

with col2:
    st.subheader("⚛️ Model & Quantum Settings")
    with st.container(border=True):
        use_qnn = st.toggle("Enable QNN", value=True)
        n_qubits = st.number_input("Qubits", value=4, min_value=1, max_value=10)
        n_layers = st.number_input("Circuit Layers", value=1, min_value=1)
        bond_dim = st.number_input("MPO Bond Dimension", value=4, min_value=1)
        token_length = st.number_input("Max Token Length", value=512)


# --- アクション：ジョブ投入 ---
st.divider()
if st.button("Run Experiment", type="primary", use_container_width=True):
    # リクエストボディの組み立て
    payload = {
        "train_params": {
            "model_name": model_name,
            "train_seed": train_seed,
            "data_seed": data_seed,
            "data_set": data_set,
            "n_train": n_train,
            "epochs": epochs,
            "lr": lr
        },
        "model_params": {
            "use_qnn": use_qnn,
            "bond_dim": bond_dim,
            "n_qubits": n_qubits,
            "n_layers": n_layers,
            "token_length": token_length
        }
    }
    
    with st.spinner("Submitting job..."):
        job_id = client.submit_job(payload)
        if job_id:
            st.success(f"Job submitted! ID: {job_id}")
            # セッション状態に保存（ポーリング開始用）
            st.session_state["current_job_id"] = job_id