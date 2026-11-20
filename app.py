"""Locally rename copies of images using identifiers found by OCR."""
import os
from pathlib import Path
import re
import shutil
from tkinter import Tk, filedialog, messagebox, simpledialog

EXTENSIONS = {".jpg", ".jpeg", ".png"}
DEFAULT_PATTERN = r"\bID[-:\s]*(\d{4})\b"


def find_identifier(text, pattern):
    match = pattern.search(text)
    if match:
        value = match.group(1) if pattern.groups else match.group()
        if value and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", value):
            return value
    return None


def read_identifier(path, pattern):
    from PIL import Image, ImageOps
    import pytesseract

    tesseract = os.getenv("TESSERACT_CMD")
    if tesseract:
        pytesseract.pytesseract.tesseract_cmd = tesseract

    with Image.open(path) as image:
        gray = ImageOps.autocontrast(ImageOps.grayscale(ImageOps.exif_transpose(image)))
        gray.thumbnail((1800, 1800))
        for mode in (11, 6):
            text = pytesseract.image_to_string(gray, config=f"--psm {mode}", timeout=20)
            identifier = find_identifier(text, pattern)
            if identifier:
                return identifier
    return None


def copy_with_name(source, destination, identifier):
    for index in range(1, 10001):
        suffix = "" if index == 1 else f"_{index}"
        target = destination / f"{identifier}{suffix}{source.suffix.lower()}"
        try:
            handle = target.open("xb")
        except FileExistsError:
            continue
        try:
            with handle, source.open("rb") as original:
                shutil.copyfileobj(original, handle)
        except OSError:
            target.unlink(missing_ok=True)
            raise
        return target
    raise OSError("Too many files with the same identifier")


def main():
    root = Tk()
    root.withdraw()
    try:
        source_dir = filedialog.askdirectory(title="Select the original image folder", parent=root)
        if not source_dir:
            return
        output_dir = filedialog.askdirectory(title="Select a separate output folder", parent=root)
        if not output_dir:
            return
        source, destination = Path(source_dir).resolve(), Path(output_dir).resolve()
        if source == destination:
            messagebox.showerror("Choose another folder", "The output folder must differ from the input folder.", parent=root)
            return

        expression = simpledialog.askstring(
            "Identifier pattern", "Enter a pattern with the ID as its first capture group.",
            initialvalue=DEFAULT_PATTERN, parent=root,
        )
        if expression is None:
            return
        try:
            pattern = re.compile(expression, re.IGNORECASE)
        except re.error as error:
            messagebox.showerror("Invalid pattern", str(error), parent=root)
            return

        images = sorted(path for path in source.iterdir() if path.is_file() and path.suffix.lower() in EXTENSIONS)
        copied = skipped = failed = 0
        for path in images:
            try:
                identifier = read_identifier(path, pattern)
            except (ImportError, OSError, RuntimeError):
                identifier = None
            if not identifier:
                identifier = simpledialog.askstring(
                    "Enter identifier",
                    f"No identifier found for {path.name}. Enter it manually or cancel to skip.",
                    parent=root,
                )
                if not identifier:
                    skipped += 1
                    continue
                identifier = identifier.strip()
                if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", identifier):
                    messagebox.showwarning("Invalid identifier", f"Skipped {path.name}.", parent=root)
                    skipped += 1
                    continue
            try:
                copy_with_name(path, destination, identifier)
            except OSError:
                failed += 1
            else:
                copied += 1
        messagebox.showinfo("Finished", f"Copied: {copied}\nSkipped: {skipped}\nFile errors: {failed}", parent=root)
    except OSError as error:
        messagebox.showerror("File error", str(error), parent=root)
    finally:
        root.destroy()


if __name__ == "__main__":
    main()
