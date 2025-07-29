import pandas as pd

def summarize_results(csv_file):
    try:
        df = pd.read_csv(csv_file)
        df = df.dropna(subset=["LLM Quality Score (1-10)", "Tokens/sec", "Latency (ms/token)"])

        df["LLM Quality Score (1-10)"] = df["LLM Quality Score (1-10)"].astype(float)
        df["Tokens/sec"] = df["Tokens/sec"].astype(float)
        df["Latency (ms/token)"] = df["Latency (ms/token)"].astype(float)

        grouped = df.groupby("Model").agg({
            "LLM Quality Score (1-10)": "mean",
            "Tokens/sec": "mean",
            "Latency (ms/token)": "mean",
            "Quantized": "first"
        }).reset_index()

        grouped["score"] = (
            grouped["LLM Quality Score (1-10)"] * 0.5 +
            (grouped["Tokens/sec"] / grouped["Tokens/sec"].max()) * 0.3 +
            ((1 / grouped["Latency (ms/token)"]) / (1 / grouped["Latency (ms/token)"]).max()) * 0.2
        )

        grouped = grouped.sort_values(by="score", ascending=False).reset_index(drop=True)
        grouped["Rank"] = grouped.index + 1

        print("\n🏆 Model Ranking (Best to Worst):")
        print(grouped[["Rank", "Model", "LLM Quality Score (1-10)", "Tokens/sec", "Latency (ms/token)", "Quantized", "score"]].to_string(index=False))

        best = grouped.iloc[0]
        print(f"\n✅ Best Model: {best['Model']} (Rank 1)")
        print(f"   → Score: {best['score']:.2f}, Quality: {best['LLM Quality Score (1-10)']:.2f}, TPS: {best['Tokens/sec']:.2f}, Latency: {best['Latency (ms/token)']:.2f}ms, Quantized: {best['Quantized']}")

        grouped.to_csv("ranked_benchmark_results.csv", index=False)

    except Exception as e:
        print(f"[!] Could not summarize results: {e}")
