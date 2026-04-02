import streamlit as st
import os
import io
import pandas as pd
import matplotlib.pyplot as plt

from api_client import QLLMApiClient



# --- 初期設定 ---
API_URL = os.getenv("API_URL", "http://api:8000")
client = QLLMApiClient(API_URL)

st.set_page_config(page_title="QLLM Control Panel", layout="wide")
st.title("🧪 Quantum-LLM Experiment Control")

# タブの定義
tab_run, tab_history = st.tabs(["🚀 Run Experiment", "📜 Experiment History"])

# --- Tab 1: ジョブのポスト操作 ---
with tab_run:
    st.header("New Experiment Configuration")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Training Params")
        model_name = st.text_input("Model", "facebook/opt-125m")
        epochs = st.number_input("Epochs", 1, 100, 10)
        lr = st.number_input("LR", value=2e-4, format="%.1e")
        
    with col2:
        st.subheader("Model/Quantum Params")
        use_qnn = st.toggle("Use QNN", True)
        n_qubits = st.slider("Qubits", 1, 10, 4)
        n_layers = st.number_input("Layers", 1, 10, 1)

    if st.button("Submit Job", type="primary"):
        payload = {
            "train_params": {"model_name": model_name, "epochs": epochs, "lr": lr},
            "model_params": {"use_qnn": use_qnn, "n_qubits": n_qubits, "n_layers": n_layers}
        }
        job_id = client.submit_job(payload)
        if job_id:
            st.success(f"Accepted: {job_id}")
            # 自動的に詳細タブへ誘導するための情報を保持
            st.session_state["last_job_id"] = job_id

# --- Tab 2: 一覧取得と詳細表示 ---
with tab_history:
    st.header("Job Management")
    
    # 2. ジョブ一覧の表示
    if st.button("🔄 Refresh History"):
        st.rerun()

    jobs = client.get_jobs()
    if jobs:
        df = pd.DataFrame(jobs)
        # 必要な列だけ表示してスッキリさせる
        st.dataframe(df[["job_id", "status", "progress", "model_name"]], use_container_width=True)
        
        st.divider()
        
        # 3. 一覧から選択したジョブの詳細表示
        selected_job_id = st.selectbox(
            "Select Job ID to view details", 
            options=[j["job_id"] for j in jobs],
            index=0
        )
        
        if selected_job_id:
            detail = client.get_job_detail(selected_job_id)
            if detail:
                # ステータス情報の表示
                c1, c2, c3 = st.columns(3)
                c1.metric("Status", detail["status"])
                c2.progress(detail["progress"], text=f"Progress: {detail['progress']*100:.1f}%")
                
                # 完了していたら結果を表示
                if detail["status"] == "completed" and detail["result"]:
                    st.subheader("📊 Experiment Results")
                    res = detail["result"]
                    eval_data = res["evaluation"]

                    # 1. 指標を際立たせるメトリクス表示
                    # 4つのカラムを作成して横並びにする
                    m1, m2, m3, m4 = st.columns(4)
                    
                    with m1:
                        st.metric(label="📉 Eval Loss", value=f"{eval_data['eval_loss']:.4f}")
                    with m2:
                        st.metric(label="🧩 Perplexity", value=f"{eval_data['perplexity']:.2f}")
                    with m3:
                        st.metric(label="⚡ Speed", value=f"{eval_data['train_steps_per_second']:.2f} step/s")
                    with m4:
                        st.metric(label="⏱️ Total Time", value=f"{eval_data['total_training_time']:.1f} min")

                    st.divider() # 区切り線

                    if "history" in res:
                        history_df = pd.DataFrame(res["history"])
                        
                        # 1. フィギュアの作成（この fig, ax を一貫して使う）
                        fig, ax = plt.subplots(figsize=(8, 5))
                        
                        # 2. プロットと装飾（すべて ax に対しておこなう）
                        ax.plot(history_df["epoch"], history_df["loss"], 
                                label="Training Loss", color="#1f77b4", linewidth=2, marker='o', markersize=4)
                        
                        ax.set_xlabel("Epoch", fontsize=10)
                        ax.set_ylabel("Loss", fontsize=10)
                        ax.set_title("Learning Curve", fontsize=12, fontweight='bold')
                        ax.grid(True, linestyle='--', alpha=0.6) # グリッドを明示的にON
                        ax.legend()
                        
                        # レイアウトの微調整
                        fig.tight_layout()

                        # 3. プレビューの表示
                        # clear_figure=False にすることで、この後の保存処理でもデータが保持されます
                        st.pyplot(fig, clear_figure=False)

                        # 4. PNGとしてバッファに保存（ダウンロード用）
                        buf = io.BytesIO()
                        fig.savefig(buf, format="png", dpi=300, bbox_inches='tight') # 高解像度PNG
                        
                        # 5. ダウンロードボタン（PNG設定）
                        st.download_button(
                            label="📥 Download Graph (PNG)",
                            data=buf.getvalue(),
                            file_name=f"plot_{selected_job_id}.png",
                            mime="image/png",
                            use_container_width=True
                        )
                elif detail["status"] == "failed":
                    st.error(f"Error: {detail.get('error')}")
                else:
                    st.info("Job is still processing. Please refresh to see updates.")
    else:
        st.info("No jobs found.")