
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "assets" / "source-photo.png"
OUTPUT = ROOT / "ascii-portrait-preview.png"

# Calidad de la conversión
COLUMNS = 160
FONT_SIZE = 9

BACKGROUND = (5, 5, 5)

# Caracteres disponibles para construir los tonos.
CHARACTERS = " .,:;!|iIl-+~_=*ox%#@"


def load_font():
    candidates = [
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/cour.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ]

    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, FONT_SIZE)

    return ImageFont.load_default()


def measure_character_density(character, font):
    """Mide la cantidad de tinta que ocupa un carácter."""
    width = max(1, round(font.getlength(character)) + 2)
    bbox = font.getbbox(character)
    height = max(1, bbox[3] - bbox[1] + 2)

    sample = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(sample)

    draw.text(
        (1, 1 - bbox[1]),
        character,
        font=font,
        fill=255,
    )

    pixels = list(sample.getdata())
    return sum(pixels) / (255 * len(pixels))


def prepare_image():
    if not INPUT.exists():
        raise FileNotFoundError(
            f"No se encontró la imagen de entrada: {INPUT}"
        )

    image = Image.open(INPUT).convert("RGB")
    image = ImageOps.grayscale(image)

    # Ajuste moderado para conservar los tonos originales.
    image = ImageOps.autocontrast(image, cutoff=0.5)
    image = ImageEnhance.Contrast(image).enhance(1.15)

    return image


def create_character_ramp(font):
    """Ordena los caracteres desde el más ligero al más denso."""
    densities = [
        (measure_character_density(char, font), char)
        for char in CHARACTERS
    ]

    densities.sort(key=lambda item: item[0])

    # Evita que diferencias minúsculas entre caracteres
    # creen demasiados niveles prácticamente iguales.
    ramp = []
    previous_density = None

    for density, char in densities:
        if (
            previous_density is None
            or density - previous_density >= 0.001
        ):
            ramp.append((density, char))
            previous_density = density

    if len(ramp) < 3:
        raise ValueError("No se pudieron medir suficientes caracteres.")

    return ramp


def convert_to_ascii(image, font, ramp):
    original_width, original_height = image.size

    cell_width = max(1, round(font.getlength("M")))
    bbox = font.getbbox("Mg")
    cell_height = max(1, bbox[3] - bbox[1] + 1)

    rows = max(
        1,
        round(
            original_height
            / original_width
            * COLUMNS
            * cell_width
            / cell_height
        ),
    )

    image = image.resize(
        (COLUMNS, rows),
        Image.Resampling.LANCZOS,
    )

    pixels = list(image.getdata())

    densities = [item[0] for item in ramp]
    characters = [item[1] for item in ramp]

    result = []

    for y in range(rows):
        line = []

        for x in range(COLUMNS):
            brightness = pixels[y * COLUMNS + x] / 255.0

            # Curva suave: evita perder demasiados tonos medios.
            brightness = brightness ** 0.9

            # El tono decide la densidad del carácter.
            target_density = (
                densities[0]
                + brightness * (densities[-1] - densities[0])
            )

            index = min(
                range(len(densities)),
                key=lambda i: abs(densities[i] - target_density),
            )

            # Conservamos el brillo en lugar de pintar todo de blanco.
            intensity = int(95 + brightness * 160)

            line.append((characters[index], intensity))

        result.append(line)

    return result, cell_width, cell_height


def render_preview(ascii_data, font, cell_width, cell_height):
    width = COLUMNS * cell_width
    height = len(ascii_data) * cell_height

    image = Image.new(
        "RGB",
        (width, height),
        BACKGROUND,
    )

    draw = ImageDraw.Draw(image)

    for y, line in enumerate(ascii_data):
        for x, (character, intensity) in enumerate(line):
            if character == " ":
                continue

            draw.text(
                (x * cell_width, y * cell_height),
                character,
                font=font,
                fill=(intensity, intensity, intensity),
            )

    return image


def main():
    font = load_font()
    source = prepare_image()
    ramp = create_character_ramp(font)

    ascii_data, cell_width, cell_height = convert_to_ascii(
        source,
        font,
        ramp,
    )

    preview = render_preview(
        ascii_data,
        font,
        cell_width,
        cell_height,
    )

    preview.save(OUTPUT)

    print("Conversión ASCII completada.")
    print(f"Entrada: {INPUT}")
    print(f"Salida: {OUTPUT}")
    print(f"Columnas: {COLUMNS}")
    print(f"Filas: {len(ascii_data)}")
    print(f"Resolución: {preview.width} x {preview.height}")


if __name__ == "__main__":
    main()
