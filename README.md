# 💧 Water Usage Analyzer

A simple and lightweight Python project to analyze daily water usage, detect trends, and provide smart conservation recommendations.

This project follows the same clean structure as my other Python analyzers - core logic is pure Python, no Flask mixed in logic.

### ✨ Features
- Add daily water usage logs (from `sample_usage_log.txt`)
- Analyze average, high & low usage
- Trend comparison (first half vs second half)
- Smart conservation tips based on usage pattern
- Clean web UI with Flask

### 🧠 Python Concepts Used (in `analyzer.py`)
- `dataclasses` -> clean data model for a `UsageRecord`
- `datetime` -> sorting readings by date
- `statistics (mean)` -> averages for trend + benchmarking
- `list slicing` -> splitting data into "first half / second half" for trend comparison
- `rule-based recommendation` -> `conservation_tips()` is a simple decision engine with if-checks

### 📁 Project Structure**# 💧 Water Usage Analyzer

A simple and lightweight Python project to analyze daily water usage, detect trends, and provide smart conservation recommendations.

This project follows the same clean structure as my other Python analyzers - core logic is pure Python, no Flask mixed in logic.

### ✨ Features
- Add daily water usage logs (from `sample_usage_log.txt`)
- Analyze average, high & low usage
- Trend comparison (first half vs second half)
- Smart conservation tips based on usage pattern
- Clean web UI with Flask

### 🧠 Python Concepts Used (in `analyzer.py`)
- `dataclasses` -> clean data model for a `UsageRecord`
- `datetime` -> sorting readings by date
- `statistics (mean)` -> averages for trend + benchmarking
- `list slicing` -> splitting data into "first half / second half" for trend comparison
- `rule-based recommendation` -> `conservation_tips()` is a simple decision engine with if-checks

### 📁 Project Structure**
