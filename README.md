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

By default, each picture appears twice, in adjacent positions. Cards are **50 × 50 mm**, with light cut lines, 3 mm internal padding, and 2 mm gaps. The grid is centered on portrait A4 with at least 10 mm margins: 3 columns × 5 rows per sheet. Extra cards automatically continue onto another page. Print at **100% / actual size**, then cut along the square outlines.

Pictures retain their proportions and are never cropped by default. Transparent areas become white, phone-photo orientation is respected, and embedded pictures are resized to a maximum of 300 DPI at print size. Only files directly inside the input folder are included, in filename order; other file types are ignored. A corrupt picture stops generation with its filename, leaving any existing output intact.

## Options

```sh
# Larger cards, cropped to fill the image area
python pexeso.py ./pictures -o large.pdf --card-size 60 --fit cover

# One copy of each image for flashcards
python pexeso.py ./pictures --copies 1

# Tightly packed cards, without gaps
python pexeso.py ./pictures --gap 0 --padding 2 --margin 12

python pexeso.py --help
```

All dimensions are in millimeters. `--fit contain` shows the complete image; `--fit cover` crops it to a square. The output file is replaced when generation succeeds. Card backs and duplex printing are not included.

## Development

```sh
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

GitHub Actions runs the tests and checks the CLI on Python 3.10 through 3.14 for every push and pull request. You can also run it manually from the repository's Actions tab.
