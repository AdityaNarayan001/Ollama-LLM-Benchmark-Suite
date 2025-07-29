import ollama
import platform
import os
import psutil
import subprocess
from config import JUDGE_MODEL

def get_system_info():
    return {
        "CPU": platform.processor() or os.uname().machine,
        "RAM (GB)": round(psutil.virtual_memory().total / (1024 ** 3), 1),
        "Platform": platform.platform(),
        "Cores": psutil.cpu_count(logical=False)
    }

def check_quantized(model_name):
    return "q" in model_name.lower() or "int" in model_name.lower()

def system_compatibility_score(info):
    score = 0
    if info["RAM (GB)"] >= 16: score += 1
    if info["Cores"] >= 8: score += 1
    if "arm" in info["CPU"].lower(): score += 1 
    return score / 3.0  

def pull_model(model_name):
    try:
        ollama.show(model_name)
        print(f"Model '{model_name}' is already available locally.")
    except ollama.ResponseError:
        print(f"Model '{model_name}' not found locally. Pulling from Ollama...")
        ollama.pull(model_name)
        print(f"Model '{model_name}' pulled successfully.")

def judge_output_quality(output):
    prompt = f"Rate the following answer for accuracy and clarity on a scale of 1 to 10:\n\n{output}\n\nScore:"
    try:
        result = ollama.chat(
            model=JUDGE_MODEL,
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )
        score_text = result['message']['content']
        score = float(score_text.strip().split()[0])
        return min(max(score, 1.0), 10.0)
    except:
        return "N/A"

def get_thermal_power_info():
    try:
        result = subprocess.check_output(
            ["powermetrics", "--samplers", "smc", "--duration", "1"], stderr=subprocess.DEVNULL
        ).decode()
        temp = None
        power = None
        for line in result.splitlines():
            if "CPU die temperature" in line:
                temp = float(line.split(':')[1].strip().split(' ')[0])
            if "Average power usage" in line and "CPU" in line:
                power = float(line.split(':')[1].strip().split(' ')[0])
        return temp, power
    except:
        return None, None
