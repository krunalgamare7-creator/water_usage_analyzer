"""
app.py
------
Flask routes for the Water Usage Analyzer.
Same GET/POST pattern as your other two projects.
"""

from flask import Flask, render_template, request, flash
from analyzer import WaterUsageAnalyzer, DEFAULT_BENCHMARK_LPCD

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-if-needed"


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", default_benchmark=DEFAULT_BENCHMARK_LPCD)


@app.route("/analyze", methods=["POST"])
def analyze():
    raw_text = request.form.get("usage_log", "").strip()
    household_str = request.form.get("household_size", "").strip()
    threshold_str = request.form.get("daily_threshold", "").strip()
    benchmark_str = request.form.get("benchmark_lpcd", "").strip()

    if not raw_text:
        flash("Please paste a water usage log before analyzing.")
        return render_template("index.html", default_benchmark=DEFAULT_BENCHMARK_LPCD)

    try:
        household_size = int(household_str)
    except ValueError:
        flash("Household size must be a number.")
        return render_template("index.html", default_benchmark=DEFAULT_BENCHMARK_LPCD)

    try:
        daily_threshold = float(threshold_str)
    except ValueError:
        flash("Daily threshold must be a number.")
        return render_template("index.html", default_benchmark=DEFAULT_BENCHMARK_LPCD)

    try:
        benchmark_lpcd = float(benchmark_str) if benchmark_str else DEFAULT_BENCHMARK_LPCD
    except ValueError:
        benchmark_lpcd = DEFAULT_BENCHMARK_LPCD

    analyzer = WaterUsageAnalyzer(raw_text, household_size, daily_threshold, benchmark_lpcd)

    if not analyzer.records:
        flash(
            "No valid usage records detected. Make sure each line follows: "
            "'YYYY-MM-DD, liters_used' — e.g. '2026-08-01, 450'."
        )
        return render_template("index.html", default_benchmark=DEFAULT_BENCHMARK_LPCD, previous_text=raw_text)

    report = analyzer.full_report()
    return render_template("results.html", report=report, household_size=household_size,
                            daily_threshold=daily_threshold)


if __name__ == "__main__":
    app.run(debug=True)
