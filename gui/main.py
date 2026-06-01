import os
import io
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from dotenv import load_dotenv
from api_client import QLLMApiClient



# --- 初期設定 ---
load_dotenv()

api_url = os.getenv("API_URL")
client = QLLMApiClient(api_url)

st.set_page_config(page_title="QLLM Control Panel", layout="wide")
st.title("🧪 Quantum-LLM Experiment Control")

# タブの定義
tab_run, tab_history = st.tabs(["Run Experiment", "Experiment History"])

# --- Tab 1: ジョブのポスト操作 ---
with tab_run:
    st.header("Experiment Configuration")
    
    # ユーザーがわかりやすいように実験タイトル入力を追加
    exp_title = st.text_input("Experiment Title", "Test Experiment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Training Params")
        model_name = st.text_input("Model", "facebook/opt-125m")
        dataset = st.text_input("Dataset", "wikitext")  # データセット入力を追加
        epochs = st.number_input("Epochs", 1, 100, 10)
        lr = st.number_input("LR", value=2e-4, format="%.1e")
        
    with col2:
        st.subheader("Model/Quantum Params")
        use_qnn = st.toggle("Use QNN", True)
        bond_dim = st.slider("MPO Bond Dim", 1, 10, 4)  # スキーマ定義に合わせて修正
        hid_dim = st.slider("Hidden Dim / Qubits", 1, 10, 4)  # スキーマ定義に合わせて修正
        n_layers = st.number_input("Layers", 1, 10, 1)

    if st.button("Submit Job", type="primary"):
        # ⭕ 最新のPredictionRequestスキーマに合わせてPayloadのネスト構造を正確にマッピング
        payload = {
            "exp_title": exp_title,
            "train_config": {
                "model_name": model_name,
                "dataset": dataset,
                "n_epoch": epochs,
                "lr": lr
            },
            "model_config": {
                "use_qnn": use_qnn,
                "bond_dim": bond_dim,
                "hid_dim": hid_dim,
                "n_layers": n_layers
            }
        }
        job_id = client.submit_job(payload)
        if job_id:
            st.success(f"Accepted: {job_id}")
            st.session_state["last_job_id"] = job_id

# --- Tab 2: 一覧取得と詳細表示 ---
with tab_history:
    st.header("Job Management")
    
    if st.button("🔄 Refresh History"):
        st.rerun()

    jobs = client.get_jobs()
    if jobs:
        df = pd.DataFrame(jobs)
        
        available_cols = ["job_id", "exp_title", "status", "progress", "ppl"]
        display_cols = [col for col in available_cols if col in df.columns]
        st.dataframe(df[display_cols], use_container_width=True)
        
        st.divider()
        
        selected_job_id = st.selectbox(
            "Select Job ID to view details", 
            options=[j["job_id"] for j in jobs],
            index=0
        )
        
        if selected_job_id:
            detail = client.get_job_detail(selected_job_id)
            if detail:
                # ⭕ 削除ボタンを配置するために、カラム数を3から4に増やします
                c1, c2, c3, c4 = st.columns([1, 2, 1, 1]) # 横幅の比率を調整
                
                c1.metric("Status", detail["status"])
                
                current_progress = detail.get("progress") if detail.get("progress") is not None else 0.0
                c2.progress(current_progress, text=f"Progress: {current_progress*100:.1f}%")
                
                # ⭕ c4 の位置に赤色の削除ボタンを配置
                with c4:
                    st.write("") # 上部の余白調整（メトリクスのラベルと高さを合わせるため）
                    st.write("") 
                    if st.button("🗑️ Delete Job", type="secondary", help="このジョブを完全に削除します"):
                        # clientにdelete_jobメソッドがあると仮定して呼び出す
                        # (もしapi_clientに未実装なら、requests.delete(f"{api_url}/experiments/{selected_job_id}") でも可)
                        try:
                            import requests
                            res = requests.delete(f"{api_url}/experiments/{selected_job_id}")
                            if res.status_code == 204:
                                st.success("削除しました！")
                                st.rerun() # 画面を再描画して一覧から消す
                            else:
                                st.error(f"削除に失敗しました: {res.status_code}")
                        except Exception as e:
                            st.error(f"通信エラー: {e}")
                
                # 完了時のレスポンスデータ構造のパース処理
                if detail["status"] == "completed":
                    st.subheader("📊 Experiment Results")
                    
                    m1, m2, m3 = st.columns(3)
                    eval_data = detail.get("evaluation", {})
                    eval_loss = eval_data.get("eval_loss", 0.0)
                    total_time = eval_data.get("total_time", 0.0)
                    ppl_value = detail.get("ppl")
                    
                    with m1:
                        st.metric(label="📉 Eval Loss", value=f"{eval_loss:.4f}")
                    with m2:
                        if ppl_value is not None:
                            st.metric(label="🧩 Perplexity", value=f"{ppl_value:.2f}")
                        else:
                            st.metric(label="🧩 Perplexity", value="N/A")
                    with m3:
                        st.metric(label="⏱️ Total Time", value=f"{total_time:.1f} min")

                    st.divider()

                    if "history" in detail and detail["history"]:
                        history_df = pd.DataFrame(detail["history"])
                        
                        fig, ax = plt.subplots(figsize=(8, 5))
                        ax.plot(history_df["epoch"], history_df["loss"], 
                                label="Training Loss", color="#1f77b4", linewidth=2, marker='o', markersize=4)
                        
                        ax.set_xlabel("Epoch", fontsize=10)
                        ax.set_ylabel("Loss", fontsize=10)
                        ax.set_title("Learning Curve", fontsize=12, fontweight='bold')
                        ax.grid(True, linestyle='--', alpha=0.6)
                        ax.legend()
                        
                        fig.tight_layout()
                        st.pyplot(fig, clear_figure=False)

                        buf = io.BytesIO()
                        fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
                        
                        st.download_button(
                            label="📥 Download Graph (PNG)",
                            data=buf.getvalue(),
                            file_name=f"plot_{selected_job_id}.png",
                            mime="image/png",
                            use_container_width=True
                        )
                elif detail["status"] == "failed":
                    st.error("Job execution failed. Please check the backend log files for more information.")
                else:
                    st.info("Job is still processing. Please refresh to see updates.")
    else:
        st.info("No jobs found.")
