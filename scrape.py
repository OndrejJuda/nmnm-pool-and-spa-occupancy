"""Snapshot current visitor counts at Městské lázně Nové Město na Moravě.

Appends one row per run to data/YYYY-MM.csv (local Prague time).
Standard library only, so the GitHub Actions runner needs no installs.
"""

import csv
import re
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

URL = "https://lazne.nmnm.cz/data/lazne/navstevnost-homepage.php"
TZ = ZoneInfo("Europe/Prague")
DATA_DIR = Path(__file__).parent / "data"

# Site label -> CSV column. The site prefixes some labels with a letter (GWellness, LMasáže).
AREAS = {
    "Areál": "areal",
    "Bazén": "bazen",
    "Fitness": "fitness",
    "GWellness": "wellness",
    "Koupele": "koupele",
    "LMasáže": "masaze",
    "Solárium": "solarium",
}
COLUMNS = ["timestamp", "weekday", "hour", *AREAS.values()]
REQUIRED = ["bazen", "wellness"]

ROW_RE = re.compile(r"<tr><td>([^<]+)</td><td[^>]*>\s*(\d+)\s*</td></tr>")


def fetch(retries: int = 3) -> str:
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(URL, headers={"User-Agent": "nmnm-occupancy-tracker"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8")
        except Exception as e:
            if attempt == retries:
                raise
            print(f"fetch failed ({e}), retrying", file=sys.stderr)
            time.sleep(10 * attempt)


def parse(html: str) -> dict[str, int]:
    counts = {}
    for label, value in ROW_RE.findall(html):
        column = AREAS.get(label.strip())
        if column:
            counts[column] = int(value)
    missing = [c for c in REQUIRED if c not in counts]
    if missing:
        raise ValueError(f"missing areas {missing} in response: {html[:500]}")
    return counts


def main() -> None:
    counts = parse(fetch())
    now = datetime.now(TZ).replace(microsecond=0)

    DATA_DIR.mkdir(exist_ok=True)
    path = DATA_DIR / f"{now:%Y-%m}.csv"
    is_new = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        if is_new:
            writer.writeheader()
        writer.writerow({
            "timestamp": now.isoformat(),
            "weekday": now.isoweekday(),
            "hour": now.hour,
            **counts,
        })
    print(f"{now.isoformat()} {counts} -> {path.name}")


if __name__ == "__main__":
    main()
