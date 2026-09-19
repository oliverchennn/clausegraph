"""Prepare synthetic native/scanned evidence locally. Makes no provider calls."""
import argparse
from pathlib import Path
import json
import textwrap

from PIL import Image, ImageDraw, ImageFont

TEXT = """SYNTHETIC EVIDENCE ONLY - not a real bill or customer.
Practice Utility Company / Alex Example
The utility payment of $123.45 is due September 28, 2026.
No discount, payment extension or third-party approval is offered.
"""
EXPECTED = {
    "synthetic": True, "kind": "obligation", "amount_cents": 12345,
    "due_date": "2026-09-28", "direction": "expense", "approval_status": "not_required",
    "review_requirement": "Unreviewed extraction must not become a confirmed executable fact.",
    "limits": "Two synthetic documents of one clause. Not a representative accuracy benchmark.",
}


def prepare(output: Path) -> list[Path]:
    paths = [output / name for name in ["native-payment.txt", "scanned-payment.pdf", "expected.json"]]
    if any(path.exists() for path in paths):
        raise FileExistsError("Use a new output directory; existing evidence files are never overwritten.")
    output.mkdir(parents=True, exist_ok=True)
    paths[0].write_text(TEXT, encoding="utf-8")
    image = Image.new("RGB", (1200, 1600), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=28)
    lines = [line for paragraph in TEXT.splitlines() for line in textwrap.wrap(paragraph, width=65)]
    for index, line in enumerate(lines):
        draw.text((60, 100 + index * 48), line, font=font, fill="black")
    # Image-only PDF deliberately exercises OCR rather than embedded PDF text.
    image.save(paths[1], "PDF", resolution=150.0)
    paths[2].write_text(json.dumps(EXPECTED, indent=2) + "\n", encoding="utf-8")
    return paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(".data/extraction-demo"))
    args = parser.parse_args()
    for path in prepare(args.output):
        print(path)
    print("Prepared only; no external processing, upload or live accuracy measurement occurred.")
