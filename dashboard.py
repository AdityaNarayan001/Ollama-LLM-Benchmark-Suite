import streamlit as st
import pandas as pd
import plotly.express as px
import subprocess
import os
import time

st.set_page_config(layout="wide")

st.title("LLM Benchmark Dashboard")

def load_data():
    if os.path.exists("ranked_benchmark_results.csv") and os.path.exists("benchmark_results.csv"):
        ranked_df = pd.read_csv("ranked_benchmark_results.csv")
        raw_df = pd.read_csv("benchmark_results.csv")
        return ranked_df, raw_df
    return None, None

ranked_df, raw_df = load_data()

if ranked_df is not None and raw_df is not None:
    st.header("🏆 Model Ranking")
    st.dataframe(ranked_df)

    st.header("📊 Detailed Performance Metrics")

    # Model selection
    selected_models = st.multiselect(
        "Select models to compare:",
        options=raw_df["Model"].unique(),
        default=raw_df["Model"].unique()
    )

    if selected_models:
        filtered_df = raw_df[raw_df["Model"].isin(selected_models)]

        col1, col2 = st.columns(2)

        with col1:
            # Tokens per second
            fig_tps = px.box(
                filtered_df,
                x="Model",
                y="Tokens/sec",
                color="Model",
                title="Tokens per Second (TPS)",
                labels={"Tokens/sec": "Tokens/sec", "Model": "Model"}
            )
            st.plotly_chart(fig_tps, use_container_width=True)

            # Latency
            fig_latency = px.box(
                filtered_df,
                x="Model",
                y="Latency (ms/token)",
                color="Model",
                title="Latency (ms/token)",
                labels={"Latency (ms/token)": "Latency (ms/token)", "Model": "Model"}
            )
            st.plotly_chart(fig_latency, use_container_width=True)

        with col2:
            # Quality Score
            fig_quality = px.box(
                filtered_df,
                x="Model",
                y="LLM Quality Score (1-10)",
                color="Model",
                title="LLM Quality Score (1-10)",
                labels={"LLM Quality Score (1-10)": "Quality Score", "Model": "Model"}
            )
            st.plotly_chart(fig_quality, use_container_width=True)

            # RAM Usage
            fig_ram = px.box(
                filtered_df,
                x="Model",
                y="RAM Usage (GB)",
                color="Model",
                title="RAM Usage (GB)",
                labels={"RAM Usage (GB)": "RAM Usage (GB)", "Model": "Model"}
            )
            st.plotly_chart(fig_ram, use_container_width=True)

    st.header("Raw Benchmark Data")
    st.dataframe(raw_df)
else:
    st.warning("Benchmark results not found. Please run the benchmark to generate results.")
if st.button("Run Benchmark"):
    st.info("Starting benchmark... This may take a while. Logs will appear below.")
    log_area = st.empty()
    log_content = ""

    process = subprocess.Popen(
        ["python", "-u", "benchmark.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )

    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            log_content += output
            log_area.code(log_content)
            time.sleep(0.1) 

    if process.returncode == 0:
        st.success("Benchmark complete!")
        st.rerun()
    else:
        st.error("Benchmark failed. Check the logs above for details.")
