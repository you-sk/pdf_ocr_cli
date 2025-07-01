import argparse
import json
import sys
from pathlib import Path

import cv2
import fitz  # PyMuPDF
import numpy as np
import pandas as pd
import pytesseract
from PIL import Image


def ocr_pdf(pdf_path: Path, lang: str, dpi: int, psm: int):
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

        # --- Image Preprocessing ---
        # 1. Convert PIL Image to NumPy array (BGR)
        open_cv_image = np.array(img)
        open_cv_image = open_cv_image[:, :, ::-1].copy()

        # 2. Grayscale
        gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)

        # 3. Binarization (Otsu's) - Invert the image for line detection
        binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

        # 4. Line removal - further adjusted for test PDFs
        # Horizontal lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1))
        detected_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)
        cnts = cv2.findContours(detected_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        for c in cnts:
            cv2.drawContours(binary, [c], -1, 0, 1)

        # Vertical lines
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 50))
        detected_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel, iterations=1)
        cnts = cv2.findContours(detected_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        for c in cnts:
            cv2.drawContours(binary, [c], -1, 0, 1)
        
        # Invert the image back so text is black and background is white
        binary = cv2.bitwise_not(binary)

        # 5. Convert back to PIL Image
        img_processed = Image.fromarray(binary)
        # --- End of Preprocessing ---

        tess_config = f'--psm {psm}'

        # Get overall text for the page
        try:
            page_text = pytesseract.image_to_string(img_processed, lang=lang, config=tess_config)
        except pytesseract.TesseractNotFoundError:
            print("Error: Tesseract is not installed or not in your PATH.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred during OCR: {e}", file=sys.stderr)
            sys.exit(1)

        # Get detailed word data
        try:
            df = pytesseract.image_to_data(img_processed, lang=lang, output_type=pytesseract.Output.DATAFRAME, config=tess_config)
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
    parser.add_argument("--psm", type=int, default=6, help="Tesseract Page Segmentation Mode (PSM) selection.")

    args = parser.parse_args()

    pdf_path = Path(args.pdf_file)
    if not pdf_path.is_file():
        print(f"Error: Input file not found or is not a file: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    ocr_results = ocr_pdf(pdf_path, args.lang, args.dpi, args.psm)

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
