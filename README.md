# LLM Benchmarking Tool

This project provides a simple framework for benchmarking the performance of various Large Language Models (LLMs) using Ollama. It measures key metrics such as response time, tokens per second (TPS), latency, and resource utilization (CPU, RAM).

## Project Structure

The project is organized into the following files:

- **`benchmark.py`**: The main script that orchestrates the benchmarking process. It handles model pulling, execution, and data logging.
- **`config.py`**: Contains all the configuration variables, such as the list of models to benchmark, the judge model for quality scoring, and prompt definitions.
- **`utils.py`**: A collection of helper functions for system information gathering, model management, and quality assessment.
- **`reporting.py`**: Handles the analysis and summarization of benchmark results, generating a ranked report of the models.

## How to Run

1.  **Install Dependencies**:
    Make sure you have the required Python libraries installed. You can install them using pip:
    ```bash
    pip install ollama pandas psutil streamlit plotly
    ```

2.  **Ensure Ollama is Running**:
    This script requires an active Ollama instance to run the benchmarks. Make sure the Ollama service is running in the background.

3.  **Run the Application**:
    You can now run the Streamlit dashboard directly. If the benchmark has not been run before, the dashboard will provide an option to start it.
    ```bash
    streamlit run dashboard.py
    ```
    This single command is all you need to either view existing results or run a new benchmark.

## Output

The script will produce two output files:

-   **`benchmark_results.csv`**: A raw CSV file containing detailed performance metrics for each model and prompt.
-   **`ranked_benchmark_results.csv`**: A summarized CSV file with the models ranked based on a composite score of quality, TPS, and latency.

The ranked results will also be printed to the console at the end of the benchmark.
