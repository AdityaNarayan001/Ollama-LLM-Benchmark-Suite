import ollama
import time
import csv
import psutil
from config import MODELS, CSV_FILE, REPEAT, PROMPTS
from utils import (
    get_system_info,
    check_quantized,
    system_compatibility_score,
    pull_model,
    judge_output_quality,
    get_thermal_power_info,
)
from reporting import summarize_results

def benchmark_model(model_name):
    print(f"--- Benchmarking {model_name} ---")

    try:
        # Warm-up
        ollama.chat(model=model_name, messages=[{"role": "user", "content": "Warmup"}], stream=False)
        load_start = time.time()
        ollama.chat(model=model_name, messages=[{"role": "user", "content": "Ready?"}], stream=False)
        load_time = time.time() - load_start

        for i in range(REPEAT):
            prompt = PROMPTS[i % len(PROMPTS)]

            cpu_before = psutil.cpu_percent(interval=1)
            ram_before = psutil.virtual_memory().used / (1024 ** 3)
            temp_before, power_before = get_thermal_power_info()

            t0 = time.time()
            response = ollama.chat(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                stream=False
            )
            t1 = time.time()

            cpu_after = psutil.cpu_percent(interval=1)
            ram_after = psutil.virtual_memory().used / (1024 ** 3)
            temp_after, power_after = get_thermal_power_info()

            gen_text = response['message']['content']
            tokens_generated = len(gen_text.split())
            total_time = t1 - t0
            tps = tokens_generated / total_time if total_time > 0 else 0
            latency = (total_time / tokens_generated * 1000) if tokens_generated > 0 else 0
            quality_score = judge_output_quality(gen_text)

            print(f"[{i+1}/{REPEAT}] Prompt: {prompt[:30]:<30} → Output: {gen_text.strip()[:60]}...")
            print(f"{'Time:':<10} {total_time:>6.2f}s  |  TPS: {tps:>6.2f}  |  Latency: {latency:>6.2f} ms")
            print(f"{'RAM Δ:':<10} {ram_after - ram_before:>6.2f} GB |  CPU Δ: {cpu_after - cpu_before:>6.2f}%")
            print(f"{'Temp:':<10} {temp_after or 'N/A':>6}°C  |  Power: {power_after or 'N/A':>6}W  |  Score: {quality_score}")
            print("-" * 70)

            with open(CSV_FILE, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    model_name, prompt, tokens_generated, f"{total_time:.2f}", f"{latency:.2f}",
                    f"{tps:.2f}", f"{load_time:.2f}",
                    f"{ram_after - ram_before:.2f}", f"{cpu_after - cpu_before:.2f}",
                    f"{temp_after or 'N/A'}", f"{power_after or 'N/A'}",
                    check_quantized(model_name), quality_score
                ])

    except Exception as e:
        print(f"Error benchmarking {model_name}: {e}")
        print("-" * 60)

if __name__ == "__main__":
    print("Starting LLM Benchmark with Ollama...")
    print("This script benchmarks several LLMs and logs performance + system resource usage.")
    print(f"Results will be saved to '{CSV_FILE}'.\nEnsure 'ollama' is running.")

    sys_info = get_system_info()
    print("System Info:")
    for k, v in sys_info.items():
        print(f"  {k:<12}: {v}")
    print(f"System Compatibility Score: {system_compatibility_score(sys_info):.2f}")
    print("=" * 60)

    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Model", "Prompt", "Tokens Generated", "Total Time (s)", "Latency (ms/token)", "Tokens/sec",
            "Model Load Time (s)", "RAM Usage (GB)", "CPU Load Change (%)",
            "Temperature (°C)", "Power (W)", "Quantized", "LLM Quality Score (1-10)"
        ])

    for model in MODELS:
        pull_model(model)
        benchmark_model(model)

    summarize_results(CSV_FILE)
    print(f"\nBenchmark complete. Results saved in {CSV_FILE}.")
