# OCR Image Renamer

A Python desktop utility that reads identifiers printed in images with Tesseract OCR and creates renamed copies in a separate folder. This public edition generalizes a utility developed for an organization. Setup and processing are local.

## Run

1. Install Python 3.10 or newer with Tkinter and install [Tesseract OCR](https://github.com/tesseract-ocr/tesseract).
2. Run `python -m pip install -r requirements.txt`.
3. Make Tesseract available on PATH or set the TESSERACT_CMD environment variable to its executable.
4. Run `python app.py`. Select input and output folders, then enter the ID pattern.

The default pattern recognizes an example such as ID-1234. The first capture group becomes the filename, or the entire match if the pattern has no capture group. If OCR cannot find a usable ID, the app asks you to enter one or skip the image. JPEG and PNG files retain their extensions. Duplicate names get a numbered suffix. Original images stay in the input folder.

The repository contains source code and documentation. You supply your own images locally.
