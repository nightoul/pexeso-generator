import tempfile
import unittest
from pathlib import Path

from PIL import Image
from pypdf import PdfReader
from reportlab.lib.pagesizes import A4

from pexeso import generate


class GeneratorTests(unittest.TestCase):
    def test_pairs_paginate_on_a4(self):
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root)
            for i in range(8):
                Image.new("RGB", (120, 60), (i * 30, 100, 200)).save(folder / f"{i}.jpg")
            output = folder / "cards.pdf"
            self.assertEqual(generate(folder, output), (16, 2))
            pages = PdfReader(output).pages
            self.assertEqual(len(pages), 2)
            self.assertAlmostEqual(float(pages[0].mediabox.width), A4[0], places=3)
            self.assertAlmostEqual(float(pages[0].mediabox.height), A4[1], places=3)
            # Every card has one square cut outline, including the last page.
            self.assertEqual(pages[0].get_contents().get_data().count(b" re S"), 15)
            self.assertEqual(pages[1].get_contents().get_data().count(b" re S"), 1)
            # By default, neighbouring cards share cut lines.
            rects = [tuple(map(float, line.split()[-6:-2]))
                     for line in pages[0].get_contents().get_data().splitlines()
                     if line.endswith(b" re S")]
            (x1, y1, w, h), (x2, y2, _, _), (_, _, _, _), (x4, y4, _, _) = rects[:4]
            self.assertAlmostEqual(x2, x1 + w, places=3)
            self.assertAlmostEqual(y4, y1 - h, places=3)

    def test_corrupt_image_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root)
            (folder / "bad.png").write_bytes(b"not an image")
            output = folder / "cards.pdf"
            output.write_bytes(b"existing")
            with self.assertRaisesRegex(ValueError, "bad.png"):
                generate(folder, output)
            self.assertEqual(output.read_bytes(), b"existing")
            self.assertEqual(len(list(folder.glob("*.pdf"))), 1)

    def test_invalid_layout_and_empty_folder(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaisesRegex(ValueError, "fit"):
                generate(root, Path(root) / "cards.pdf", card_size=300)
            with self.assertRaisesRegex(ValueError, "No PNG"):
                generate(root, Path(root) / "cards.pdf")


if __name__ == "__main__":
    unittest.main()
