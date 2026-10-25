import json
import re
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup


USERNAME = "GucciGang15"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUTPUT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"


def fetch_html():
    response = requests.get(
        URL,
        headers={"User-Agent": "GitHub-Profile-Art/1.0"},
        timeout=30,
    )
    response.raise_for_status()
    return response.text


def parse_contributions(html):
    soup = BeautifulSoup(html, "html.parser")

    # Relacionar cada tooltip con el ID de su celda.
    tooltip_counts = {}

    for tooltip in soup.find_all("tool-tip"):
        cell_id = tooltip.get("for")
        text = tooltip.get_text(" ", strip=True)

        if not cell_id:
            continue

        match = re.search(r"([\d,]+)\s+contributions?", text, re.I)

        if match:
            tooltip_counts[cell_id] = int(match.group(1).replace(",", ""))
        elif re.search(r"\bno contributions\b", text, re.I):
            tooltip_counts[cell_id] = 0

    days = []

    for cell in soup.select("td[data-date][data-level]"):
        cell_id = cell.get("id")
        day_date = cell.get("data-date")
        level_text = cell.get("data-level")

        try:
            parsed_date = date.fromisoformat(day_date)
            level = int(level_text)
        except (TypeError, ValueError):
            continue

        if not 0 <= level <= 4:
            continue

        count = tooltip_counts.get(cell_id)

        # No inventar conteos si GitHub cambia el HTML.
        if count is None and level == 0:
            count = 0

        days.append({
            "date": parsed_date.isoformat(),
            "level": level,
            "count": count,
        })

    days.sort(key=lambda day: day["date"])

    if not days:
        raise ValueError("No se encontraron días de contribuciones.")

    if len({day["date"] for day in days}) != len(days):
        raise ValueError("Se encontraron fechas duplicadas.")

    # No presentar un total como exacto si falta un conteo activo.
    total = None
    if all(day["count"] is not None for day in days):
        total = sum(day["count"] for day in days)

    return days, total


def calculate_stats(days):
    monthly_totals = defaultdict(int)

    for day in days:
        month = day["date"][:7]
        if day["count"] is not None:
            monthly_totals[month] += day["count"]

    active_days = [
        day for day in days
        if day["count"] is not None and day["count"] > 0
    ]

    best_day = max(
        active_days,
        key=lambda day: day["count"],
        default=None,
    )

    # Rachas calculadas con las fechas disponibles.
    longest_streak = 0
    current_streak = 0
    previous_date = None

    for day in days:
        current_date = date.fromisoformat(day["date"])

        if day["count"] is None:
            current_streak = 0
            previous_date = current_date
            continue

        if day["count"] > 0:
            if previous_date == current_date - timedelta(days=1):
                current_streak += 1
            else:
                current_streak = 1

            longest_streak = max(longest_streak, current_streak)
        else:
            current_streak = 0

        previous_date = current_date

    # Racha actual: solo si el último día disponible tiene actividad.
    current_streak = 0

    for day in reversed(days):
        if day["count"] is None or day["count"] == 0:
            break
        current_streak += 1

    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly_totals": dict(sorted(monthly_totals.items())),
    }


def main():
    html = fetch_html()
    days, total = parse_contributions(html)

    result = {
        "username": USERNAME,
        "total_contributions": total,
        "days": days,
        "stats": calculate_stats(days),
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Usuario: {USERNAME}")
    print(f"Días encontrados: {len(days)}")
    print(f"Total de contribuciones: {total}")
    print(f"Archivo generado: {OUTPUT}")


if __name__ == "__main__":
    main()
