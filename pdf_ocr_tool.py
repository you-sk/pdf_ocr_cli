import argparse
import json
import sys
from pathlib import Path

import fitz  # PyMuPDF
import pandas as pd
import pytesseract
from PIL import Image


def ocr_pdf(pdf_path: Path, lang: str, dpi: int):
    results = []
    try:
        doc = fitz.open(pdf_path)
    except fitz.FileNotFoundError:
        print(f"Error: PDF file not found at {pdf_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Could not open PDF file. Reason: {e}", file=sys.stderr)
        sys.exit(1)

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)

        # Render page to an image
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Get overall text for the page
        try:
            page_text = pytesseract.image_to_string(img, lang=lang)
        except pytesseract.TesseractNotFoundError:
            print("Error: Tesseract is not installed or not in your PATH.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred during OCR: {e}", file=sys.stderr)
            sys.exit(1)

        # Get detailed word data
        try:
            df = pytesseract.image_to_data(img, lang=lang, output_type=pytesseract.Output.DATAFRAME)
        except pytesseract.TesseractNotFoundError:
            print("Error: Tesseract is not installed or not in your PATH.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred during OCR data extraction: {e}", file=sys.stderr)
            sys.exit(1)

        # Filter and format word data
        words = []
        df_filtered = df[(df.conf != -1) & (df.level == 5) & (df.text.notna())]

        for i, row in df_filtered.iterrows():
            words.append({
                "text": row["text"],
                "bbox": {
                    "left": int(row["left"]),
                    "top": int(row["top"]),
                    "width": int(row["width"]),
                    "height": int(row["height"])
                },
                "confidence": round(float(row["conf"]), 2)
            })

        results.append({
            "page_number": page_num + 1,
            "page_overall_text": page_text,
            "words": words
        })

    return results

def main():
    parser = argparse.ArgumentParser(description="Perform OCR on a PDF file and output results as JSON.")
    parser.add_argument("pdf_file", type=str, help="Path to the PDF file to process.")
    parser.add_argument("-o", "--output", type=str, default=None, help="Path to the output JSON file. Defaults to stdout.")
    parser.add_argument("-l", "--lang", type=str, default="jpn", help="Language for Tesseract OCR (e.g., jpn, eng).")
    parser.add_argument("-d", "--dpi", type=int, default=300, help="Resolution (DPI) for image rendering.")

    args = parser.parse_args()

    pdf_path = Path(args.pdf_file)
    if not pdf_path.is_file():
        print(f"Error: Input file not found or is not a file: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    ocr_results = ocr_pdf(pdf_path, args.lang, args.dpi)

    output_json = json.dumps(ocr_results, ensure_ascii=False, indent=2)

    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_json)
        except IOError as e:
            print(f"Error: Could not write to output file {args.output}. Reason: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output_json)

if __name__ == "__main__":
    main()
