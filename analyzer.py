"""
analyzer.py
-----------
Core logic for the Water Usage Analyzer. Pure Python, no Flask —
same pattern as your other two projects.

Python concepts used in this file:
  - dataclasses            -> clean data model for a UsageRecord
  - datetime                -> sorting readings by date
  - statistics (mean)        -> averages for trend + benchmarking
  - list slicing              -> splitting data into "first half / second half"
                                 for trend comparison
  - rule-based recommendation  -> conservation_tips() is a simple decision
                                 engine: a series of if-checks that each
                                 append a tip when a condition is true
"""

from dataclasses import dataclass
from datetime import datetime
from statistics import mean


# ---------------------------------------------------------------------------
# National/regional benchmark: litres per capita per day (LPCD).
# 135 is the standard urban household benchmark used in Indian water
# planning guidelines. Adjustable per report via the benchmark_lpcd param.
# ---------------------------------------------------------------------------
DEFAULT_BENCHMARK_LPCD = 135


@dataclass
class UsageRecord:
    reading_date: datetime
    liters: float

    def to_dict(self):
        return {"date": self.reading_date.date().isoformat(), "liters": self.liters}


class WaterUsageAnalyzer:
    """
    Takes a raw pasted daily water-usage log + household details, and
    produces:
      - leak estimation (persistent baseline usage that shouldn't exist)
      - daily trend analysis (is usage rising, falling, or stable?)
      - usage benchmarking (vs a standard litres/person/day figure)
      - threshold alerts (days that broke a user-set daily limit)
      - conservation tips (rule-based recommendations from the above)
    """

    def __init__(self, raw_text: str, household_size: int,
                 daily_threshold: float, benchmark_lpcd: float = DEFAULT_BENCHMARK_LPCD):
        self.household_size = max(household_size, 1)  # avoid divide-by-zero
        self.daily_threshold = daily_threshold
        self.benchmark_lpcd = benchmark_lpcd
        self.records = self._parse(raw_text)

    # ---- PARSING -----------------------------------------------------
    def _parse(self, raw_text: str):
        """
        Expected line format:
            YYYY-MM-DD, liters_used
        e.g.
            2026-08-01, 450
        """
        records = []
        for line in raw_text.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) != 2:
                continue
            date_str, liters_str = parts
            try:
                reading_date = datetime.strptime(date_str, "%Y-%m-%d")
                liters = float(liters_str)
            except ValueError:
                continue
            records.append(UsageRecord(reading_date, liters))
        records.sort(key=lambda r: r.reading_date)
        return records

    # ---- FEATURE 1: LEAK ESTIMATION --------------------------------------
    def leak_estimation(self):
        """
        The core idea: even on your LOWEST-usage day (away from home, etc.)
        usage should drop close to a small per-person floor. If the minimum
        recorded day is still well above that floor, water is very likely
        leaking continuously (a running toilet, dripping tap, or pipe leak).
        """
        if not self.records:
            return {"possible_leak": False, "baseline_liters": 0,
                     "leak_floor": 0, "estimated_daily_leak": 0,
                     "estimated_monthly_waste": 0}

        # Reasonable "no one's really using water" floor: ~10L/person/day
        leak_floor = 10 * self.household_size
        baseline = min(r.liters for r in self.records)

        possible_leak = baseline > leak_floor
        estimated_daily_leak = round(max(baseline - leak_floor, 0), 1)
        estimated_monthly_waste = round(estimated_daily_leak * 30, 1)

        return {
            "possible_leak": possible_leak,
            "baseline_liters": baseline,
            "leak_floor": leak_floor,
            "estimated_daily_leak": estimated_daily_leak,
            "estimated_monthly_waste": estimated_monthly_waste,
        }

    # ---- FEATURE 2: DAILY TREND ANALYSIS ------------------------------------
    def daily_trend_analysis(self):
        """
        Splits the log into an earlier half and a later half, and compares
        their averages to see whether usage is trending up, down, or flat.
        Also returns a simple 3-day moving average series for charting.
        """
        if len(self.records) < 2:
            return {"trend": "Not enough data", "pct_change": 0, "moving_average": []}

        mid = len(self.records) // 2
        first_half = [r.liters for r in self.records[:mid]]
        second_half = [r.liters for r in self.records[mid:]]

        avg_first = mean(first_half)
        avg_second = mean(second_half)
        pct_change = round(((avg_second - avg_first) / avg_first) * 100, 1) if avg_first else 0

        if pct_change > 8:
            trend = "Increasing"
        elif pct_change < -8:
            trend = "Decreasing"
        else:
            trend = "Stable"

        # 3-day moving average, for a smoother trend line
        moving_average = []
        window = 3
        for i in range(len(self.records)):
            start = max(0, i - window + 1)
            chunk = [r.liters for r in self.records[start:i + 1]]
            moving_average.append({
                "date": self.records[i].reading_date.date().isoformat(),
                "avg": round(mean(chunk), 1),
            })

        return {"trend": trend, "pct_change": pct_change, "moving_average": moving_average}

    # ---- FEATURE 3: USAGE BENCHMARKING ---------------------------------------
    def usage_benchmarking(self):
        """Compares actual litres/person/day against the standard benchmark."""
        if not self.records:
            return {"avg_lpcd": 0, "benchmark_lpcd": self.benchmark_lpcd,
                     "pct_diff": 0, "status": "No data"}

        total_liters = sum(r.liters for r in self.records)
        avg_daily_total = total_liters / len(self.records)
        avg_lpcd = round(avg_daily_total / self.household_size, 1)

        pct_diff = round(((avg_lpcd - self.benchmark_lpcd) / self.benchmark_lpcd) * 100, 1)

        if pct_diff <= -10:
            status = "Efficient"
        elif pct_diff <= 15:
            status = "Normal"
        else:
            status = "High Usage"

        return {
            "avg_lpcd": avg_lpcd,
            "benchmark_lpcd": self.benchmark_lpcd,
            "pct_diff": pct_diff,
            "status": status,
        }

    # ---- FEATURE 4: THRESHOLD ALERTS -------------------------------------------
    def threshold_alerts(self):
        """Flags every day that exceeded the user-set daily litre limit."""
        alerts = []
        for r in self.records:
            if r.liters > self.daily_threshold:
                alerts.append({
                    "date": r.reading_date.date().isoformat(),
                    "liters": r.liters,
                    "excess": round(r.liters - self.daily_threshold, 1),
                })
        alerts.sort(key=lambda a: a["excess"], reverse=True)
        return alerts

    # ---- FEATURE 5: CONSERVATION TIPS -----------------------------------------
    def conservation_tips(self):
        """
        A simple RULE-BASED recommendation engine: each check below looks
        at one piece of the analysis and appends a tip if the condition is
        true. This is exactly how many real "decision support" systems
        work before anyone reaches for machine learning.
        """
        tips = []
        leak = self.leak_estimation()
        trend = self.daily_trend_analysis()
        bench = self.usage_benchmarking()
        alerts = self.threshold_alerts()

        if leak["possible_leak"]:
            tips.append(
                f"Your lowest-usage day still shows {leak['baseline_liters']}L used — "
                f"this pattern usually means a running toilet or dripping tap. "
                f"Check all taps and toilet flush valves; a leak like this can waste "
                f"~{leak['estimated_monthly_waste']}L a month."
            )

        if trend["trend"] == "Increasing":
            tips.append(
                f"Usage has risen about {trend['pct_change']}% recently. Check for a new "
                f"appliance, guest stay, or garden watering that might explain it — "
                f"or it could be an emerging leak."
            )

        if bench["status"] == "High Usage":
            tips.append(
                f"Your usage is {bench['pct_diff']}% above the standard benchmark "
                f"({bench['benchmark_lpcd']}L/person/day). Try shorter showers, "
                f"fixing dripping taps, and using a bucket instead of a hose for washing."
            )
        elif bench["status"] == "Efficient":
            tips.append(
                "Your household is using water more efficiently than the standard "
                "benchmark — keep it up."
            )

        if alerts:
            tips.append(
                f"{len(alerts)} day(s) exceeded your daily threshold of "
                f"{self.daily_threshold}L. Review what happened on the worst day "
                f"({alerts[0]['date']}, {alerts[0]['excess']}L over limit)."
            )

        if not tips:
            tips.append("No red flags found — your water usage looks healthy and consistent.")

        return tips

    # ---- PUTTING IT ALL TOGETHER -----------------------------------------------
    def full_report(self):
        return {
            "records": [r.to_dict() for r in self.records],
            "leak_estimation": self.leak_estimation(),
            "daily_trend": self.daily_trend_analysis(),
            "benchmarking": self.usage_benchmarking(),
            "threshold_alerts": self.threshold_alerts(),
            "conservation_tips": self.conservation_tips(),
        }
