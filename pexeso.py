#!/usr/bin/env python3
"""Turn a folder of pictures into printable square memory-game cards."""

import argparse
import math
from pathlib import Path
import sys
import tempfile

from PIL import Image, ImageChops, ImageOps
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

EXTENSIONS = {".png", ".jpg", ".jpeg"}
WHITE = 240  # Grey levels at or above this count as background white.


def nonnegative(value):
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise argparse.ArgumentTypeError("must be a finite, nonnegative number")
    return number


def positive(value):
    number = nonnegative(value)
    if number == 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return number


def plain_background(image):
    """Return True when most of the picture's outer edge is white, as in clip-art."""
    width, height = image.size
    gray = image.convert("L")
    edges = [gray.crop(box) for box in ((0, 0, width, 1), (0, height - 1, width, height),
                                        (0, 0, 1, height), (width - 1, 0, width, height))]
    white = sum(sum(edge.histogram()[WHITE:]) for edge in edges)
    return white >= 0.8 * 2 * (width + height)


def trim(image):
    """Crop away plain white borders around the picture's subject."""
    difference = ImageChops.difference(image, Image.new("RGB", image.size, "white"))
    box = difference.convert("L").point(lambda v: 255 if v > 255 - WHITE else 0).getbbox()
    return image.crop(box) if box else image


def generate(folder, output, card_size=50, margin=10, gap=0, padding=3,
             copies=2, fit="smart"):
    """Generate a PDF; dimensions are millimeters. Return (cards, pages)."""
    folder, output = Path(folder), Path(output)
    if not folder.is_dir():
        raise ValueError(f"Image folder does not exist: {folder}")
    if (not all(math.isfinite(v) for v in (card_size, margin, gap, padding))
            or card_size <= 0 or min(margin, gap, padding) < 0
            or padding * 2 >= card_size or copies < 1
            or not isinstance(copies, int) or fit not in {"smart", "contain", "cover"}):
        raise ValueError("Invalid card dimensions, copies, or fit mode")
    width, height = A4
    size, border, gutter = card_size * mm, margin * mm, gap * mm
    cols = math.floor((width - 2 * border + gutter) / (size + gutter))
    rows = math.floor((height - 2 * border + gutter) / (size + gutter))
    if cols < 1 or rows < 1:
        raise ValueError("Cards and margins do not fit on A4 paper")
    paths = sorted((p for p in folder.iterdir() if p.is_file()
                    and p.suffix.lower() in EXTENSIONS), key=lambda p: p.name)
    if not paths:
        raise ValueError(f"No PNG or JPG images found in {folder}")
    if output.resolve() in [p.resolve() for p in paths]:
        raise ValueError("Output must not overwrite an input image")

    output.parent.mkdir(parents=True, exist_ok=True)
    # Write atomically so a corrupt image cannot leave a half-written PDF.
    with tempfile.NamedTemporaryFile(dir=output.parent, suffix=".pdf", delete=False) as f:
        temporary = Path(f.name)
    try:
        pdf = canvas.Canvas(str(temporary), pagesize=A4)
        pdf.setTitle("Pexeso cards")
        capacity = cols * rows
        left = (width - (cols * size + (cols - 1) * gutter)) / 2
        top = (height + (rows * size + (rows - 1) * gutter)) / 2
        index = 0
        pixels = max(1, math.ceil((card_size - 2 * padding) / 25.4 * 300))
        for path in paths:
            try:
                with Image.open(path) as source:
                    image = ImageOps.exif_transpose(source).convert("RGBA")
                    background = Image.new("RGBA", image.size, "white")
                    background.alpha_composite(image)
                    image = background.convert("RGB")
                    mode = fit
                    if fit == "smart":
                        # Clip-art blends into the white card; photos must fill the square.
                        mode = "contain" if plain_background(image) else "cover"
                        image = trim(image)
                    if mode == "cover":
                        image = ImageOps.fit(image, (pixels, pixels), method=Image.Resampling.LANCZOS)
                    else:
                        image.thumbnail((pixels, pixels), Image.Resampling.LANCZOS)
            except (OSError, ValueError, Image.DecompressionBombError) as exc:
                raise ValueError(f"Cannot read image {path.name}: {exc}") from exc
            reader = ImageReader(image)
            inner = size - 2 * padding * mm
            scale = min(inner / image.width, inner / image.height)
            iw, ih = image.width * scale, image.height * scale
            for _ in range(copies):
                if index and index % capacity == 0:
                    pdf.showPage()
                slot = index % capacity
                x = left + (slot % cols) * (size + gutter)
                y = top - (slot // cols + 1) * size - (slot // cols) * gutter
                pdf.setStrokeColorRGB(0.65, 0.65, 0.65)
                pdf.setLineWidth(0.4)
                pdf.rect(x, y, size, size)
                pdf.drawImage(reader, x + (size - iw) / 2, y + (size - ih) / 2, iw, ih)
                index += 1
        pdf.save()
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    return index, math.ceil(index / capacity)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path, help="folder containing PNG/JPG images")
    parser.add_argument("-o", "--output", type=Path, default=Path("pexeso.pdf"))
    parser.add_argument("--card-size", type=positive, default=50, help="square side in mm (default: 50)")
    parser.add_argument("--margin", type=nonnegative, default=10, help="minimum page margin in mm (default: 10)")
    parser.add_argument("--gap", type=nonnegative, default=0, help="gap between cards in mm (default: 0, shared cut lines)")
    parser.add_argument("--padding", type=nonnegative, default=3, help="image inset in mm (default: 3)")
    parser.add_argument("--copies", type=int, default=2, help="copies per image (default: 2 for pairs)")
    parser.add_argument("--fit", choices=("smart", "contain", "cover"), default="smart",
                        help="smart shows clip-art whole and crops photos to a square (default); "
                             "cover always crops to a centered square; contain always shows the whole picture")
    args = parser.parse_args(argv)
    try:
        cards, pages = generate(**vars(args))
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Error: {exc}\n")
    print(f"Created {args.output}: {cards} cards on {pages} A4 page(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
