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

# Site label -> CSV column. Since 23.11.2026 the site shows only Bazén, Fitness and Wellness
# as tiles; areal/koupele/masaze/solarium stay in the CSV (empty) to keep the schema stable.
AREAS = {
    "Bazén": "bazen",
    "Fitness": "fitness",
    "Wellness": "wellness",
}
COLUMNS = [
    "timestamp", "weekday", "hour",
    "areal", "bazen", "fitness", "wellness", "koupele", "masaze", "solarium",
    "stav", "stale",
]
REQUIRED = ["bazen", "wellness"]

TILE_RE = re.compile(
    r'class="nmnm-obsazenost__nazev">\s*([^<]+?)\s*</span>\s*'
    r'<span class="nmnm-obsazenost__pocet">\s*(\d+)\s*</span>'
)
# "Návštěvnost stav k 8:38" = when the site's counter was last updated.
STAV_RE = re.compile(r"stav k\s*(\d{1,2}:\d{2})", re.IGNORECASE)
# The site marks outdated numbers with this class (the name also appears in its <style>, so match attributes only).
STALE_RE = re.compile(r'class="[^"]*\bnmnm-obsazenost(?:__stav)?--star[ay]\b')


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


def parse(html: str) -> dict[str, object]:
    counts: dict[str, object] = {}
    for label, value in TILE_RE.findall(html):
        column = AREAS.get(label)
        if column:
            counts[column] = int(value)
    missing = [c for c in REQUIRED if c not in counts]
    if missing:
        raise ValueError(f"missing areas {missing} in response: {html[:500]}")
    stav = STAV_RE.search(html)
    counts["stav"] = stav.group(1) if stav else ""
    counts["stale"] = int(bool(STALE_RE.search(html)))
    return counts


def ensure_header(path: Path) -> None:
    """Upgrade an older file's header in place when COLUMNS gained new trailing fields."""
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    header = ",".join(COLUMNS)
    if lines and lines[0].strip() != header:
        old = lines[0].strip().split(",")
        if old != COLUMNS[: len(old)]:
            raise ValueError(f"unexpected header in {path.name}: {lines[0].strip()}")
        ending = lines[0][len(lines[0].rstrip("\r\n")):] or "\r\n"
        lines[0] = header + ending
        path.write_text("".join(lines), encoding="utf-8", newline="")


def main() -> None:
    counts = parse(fetch())
    now = datetime.now(TZ).replace(microsecond=0)

    DATA_DIR.mkdir(exist_ok=True)
    path = DATA_DIR / f"{now:%Y-%m}.csv"
    is_new = not path.exists()
    if not is_new:
        ensure_header(path)
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
