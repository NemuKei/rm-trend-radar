from __future__ import annotations

from .db import init_db


if __name__ == "__main__":
    init_db(seed=True)
    print("Initialized rm_trend_radar.db")