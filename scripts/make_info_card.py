
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "info-card.svg"

BACKGROUND = "#0d1117"
FOREGROUND = "#c9d1d9"
MUTED = "#8b949e"
ACCENT = "#58a6ff"
LINE = "#30363d"

WIDTH = 760
HEIGHT = 300


def make_row(label, value, y):
    return f"""
    <text x="34" y="{y}" fill="{MUTED}"
          font-family="monospace" font-size="12"
          letter-spacing="1">{escape(label)}</text>
    <text x="190" y="{y}" fill="{FOREGROUND}"
          font-family="monospace" font-size="13">{escape(value)}</text>
    """


def main():
    rows = [
        ("FOCUS", "Software Development"),
        ("LANGUAGES", "Python · PHP · C#"),
        ("WEB", "JavaScript · HTML · CSS"),
        ("DATABASES", "MySQL · PostgreSQL"),
        ("TOOLS", "Git · GitHub"),
    ]

    row_elements = []
    for index, (label, value) in enumerate(rows):
        y = 112 + index * 32
        row_elements.append(make_row(label, value, y))

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
        width="{WIDTH}" height="{HEIGHT}"
        viewBox="0 0 {WIDTH} {HEIGHT}">
      <title>GucciGang15 profile information</title>
      <rect width="100%" height="100%" rx="12"
            fill="{BACKGROUND}"/>

      <rect x="1" y="1" width="{WIDTH - 2}" height="{HEIGHT - 2}"
            rx="11" fill="none" stroke="{LINE}"/>

      <text x="34" y="42" fill="{ACCENT}"
            font-family="monospace" font-size="12">
        PROFILE / 01
      </text>

      <text x="34" y="73" fill="{FOREGROUND}"
            font-family="monospace" font-size="23"
            font-weight="bold">GucciGang15</text>

      <text x="34" y="93" fill="{MUTED}"
            font-family="monospace" font-size="12">
        Computer Science Student
      </text>

      <line x1="34" y1="99" x2="726" y2="99"
            stroke="{LINE}"/>

      {''.join(row_elements)}

      <line x1="34" y1="263" x2="726" y2="263"
            stroke="{LINE}"/>

      <text x="34" y="284" fill="{MUTED}"
            font-family="monospace" font-size="11">
        Building projects. Learning every day.
      </text>

      <circle cx="711" cy="281" r="4" fill="{ACCENT}">
        <animate attributeName="opacity"
                 values="1;0.25;1"
                 dur="2s" repeatCount="indefinite"/>
      </circle>
    </svg>
    """

    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"Info card generated: {OUTPUT}")


if __name__ == "__main__":
    main()
