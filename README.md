# Pexeso generator

[![Tests](https://github.com/nightoul/pexeso-generator/actions/workflows/tests.yml/badge.svg)](https://github.com/nightoul/pexeso-generator/actions/workflows/tests.yml)

Make printable, square memory-game cards from a folder of pictures. Designed for teachers: save one picture per vocabulary word, then generate matching pairs in one command.

## Setup

Python 3.10 or newer:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, activate with `.venv\Scripts\activate` instead.

## Generate cards

Put your PNG, JPG, or JPEG files in a folder, then run:

```sh
python pexeso.py ./pictures -o ./output/animals.pdf
```

By default, each picture appears twice, in adjacent positions. Cards are **50 × 50 mm**, with light cut lines and 3 mm internal padding. Neighbouring cards touch, so each line between them is a single scissor cut. The grid is centered on portrait A4 with at least 10 mm margins: 3 columns × 5 rows per sheet. Extra cards automatically continue onto another page. Print at **100% / actual size**, then cut along the square outlines.

By default, pictures are fitted smartly. Clip-art on a white or transparent background has its empty borders trimmed and is shown whole, since leftover space blends into the white card. Photos with a colored background are zoomed in and cropped evenly from the center to fill the square. Transparent areas become white, phone-photo orientation is respected, and embedded pictures are resized to a maximum of 300 DPI at print size and stored as high-quality JPEG, so the PDF stays small enough to email to a print shop. Only files directly inside the input folder are included, in filename order; other file types are ignored. A corrupt picture stops generation with its filename, leaving any existing output intact.

## Options

```sh
# Larger cards that show each complete picture, without cropping
python pexeso.py ./pictures -o large.pdf --card-size 60 --fit contain

# One copy of each image for flashcards
python pexeso.py ./pictures --copies 1

# Separate cards with 2 mm gaps, less padding, and wider margins
python pexeso.py ./pictures --gap 2 --padding 2 --margin 12

python pexeso.py --help
```

All dimensions are in millimeters. `--fit smart` (the default) chooses per picture as described above; `--fit cover` always crops each image to a square; `--fit contain` always shows the complete image and keeps its proportions. The output file is replaced when generation succeeds. Card backs and duplex printing are not included.

## Development

```sh
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

GitHub Actions runs the tests and checks the CLI on Python 3.10 through 3.14 for every push and pull request. You can also run it manually from the repository's Actions tab.
