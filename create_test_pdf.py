
import fitz  # PyMuPDF
import sys

def create_test_pdf(output_dir: str, text: str, filename: str):
    """Creates a simple one-page PDF with the given text in the specified directory."""
    output_path = f"{output_dir}/{filename}"
    doc = fitz.open()
    page = doc.new_page()
    
    # Path to the installed IPA Gothic font in the Docker container
    font_path = "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"
    page.insert_text((50, 72), text, fontsize=11, fontname="ipagothic", fontfile=font_path)
    
    doc.save(output_path)
    doc.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python create_test_pdf.py <output_directory>", file=sys.stderr)
        sys.exit(1)
    output_dir = sys.argv[1]
    
    # Create a Japanese sample PDF
    create_test_pdf(output_dir, "これは日本語のテストです。", "test_jp.pdf")
    # Create an English sample PDF
    create_test_pdf(output_dir, "This is an English test.", "test_en.pdf")
    print(f"Created test_jp.pdf and test_en.pdf in {output_dir}")
