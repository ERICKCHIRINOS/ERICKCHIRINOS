import json
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "data" / "contributions.json"
OUTPUT = ROOT / "contrib-heatmap.svg"

PALETTE = [
    "#161b22",  # Sin contribuciones
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
]

WIDTH = 860
HEIGHT = 165
LEFT = 22
RIGHT = 22
TOP = 34

CELL = 12
GAP = 3
STEP = CELL + GAP

ROWS = 7
DAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


def main():
    data = json.loads(INPUT.read_text(encoding="utf-8"))
    days = data["days"]

    if not days:
        raise ValueError("No hay días para dibujar.")

    days = sorted(days, key=lambda item: item["date"])

    first_date = date.fromisoformat(days[0]["date"])
    last_date = date.fromisoformat(days[-1]["date"])

    expected_days = (last_date - first_date).days + 1

    if len(days) != expected_days:
        raise ValueError("El calendario contiene fechas ausentes.")

    # La primera columna empieza el domingo de la semana
    # en la que cae la primera fecha.
    first_sunday = first_date.toordinal() - (
        (first_date.weekday() + 1) % 7
    )

    # Calcular cuántas semanas ocupa el intervalo completo.
    last_sunday_offset = (
        last_date.toordinal() - first_sunday
    ) // 7

    columns = last_sunday_offset + 1

    available_width = WIDTH - LEFT - RIGHT
    actual_step = available_width / columns

    # Ajustar el tamaño de las celdas para que las columnas
    # se distribuyan uniformemente dentro del ancho disponible.
    cell_size = min(CELL, actual_step - 2)
    if cell_size <= 0:
        raise ValueError("El ancho disponible es insuficiente.")

    elements = []

    for day in days:
        current = date.fromisoformat(day["date"])

        # Columna según la semana real; domingo en la fila 0.
        offset_from_sunday = current.toordinal() - first_sunday
        column = offset_from_sunday // 7
        row = (current.weekday() + 1) % 7

        level = day["level"]
        if not isinstance(level, int) or not 0 <= level < len(PALETTE):
            raise ValueError(
                f"Nivel de actividad inválido en {day['date']}: {level}"
            )

        count = day["count"]

        x = LEFT + column * actual_step
        y = TOP + row * STEP
        delay = (column + row) * 0.012

        if count is None:
            tooltip = f"{day['date']}: conteo no disponible"
        else:
            noun = "contribución" if count == 1 else "contribuciones"
            tooltip = f"{count} {noun} el {day['date']}"

        elements.append(
            f'<rect x="{x:.2f}" y="{y}" '
            f'width="{cell_size:.2f}" height="{cell_size}" '
            f'rx="2" fill="{PALETTE[level]}" opacity="0">'
            f'<title>{escape(tooltip)}</title>'
            f'<animate attributeName="opacity" from="0" to="1" '
            f'dur="0.25s" begin="{delay:.3f}s" fill="freeze"/>'
            f'</rect>'
        )

    total = data.get("total_contributions")

    if total is None:
        total_text = "Contribution counts partially unavailable"
    else:
        total_text = f"{total:,} contributions in the last year"

    legend_x = WIDTH - 160
    legend = []

    for index, color in enumerate(PALETTE):
        x = legend_x + index * 18
        legend.append(
            f'<rect x="{x}" y="136" width="11" height="11" '
            f'rx="2" fill="{color}"/>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
      width="{WIDTH}" height="{HEIGHT}"
      viewBox="0 0 {WIDTH} {HEIGHT}">
      <title>{escape(data["username"])} contribution heatmap</title>

      <rect width="100%" height="100%" rx="10" fill="#0d1117"/>

      <text x="{LEFT}" y="20" fill="#c9d1d9"
        font-family="monospace" font-size="12">
        {escape(data["username"])} / contributions
      </text>

      {''.join(elements)}

      <text x="{LEFT}" y="146" fill="#8b949e"
        font-family="monospace" font-size="11">
        {escape(total_text)}
      </text>

      <text x="{legend_x - 35}" y="147" fill="#8b949e"
        font-family="monospace" font-size="10">Less</text>

      {''.join(legend)}

      <text x="{legend_x + 95}" y="147" fill="#8b949e"
        font-family="monospace" font-size="10">More</text>
    </svg>
    '''

    OUTPUT.write_text(svg, encoding="utf-8")

    print(f"SVG generado: {OUTPUT}")
    print(f"Intervalo: {first_date} - {last_date}")
    print(f"Semanas: {columns}")
    print(f"Días dibujados: {len(elements)}")


if __name__ == "__main__":
    main()