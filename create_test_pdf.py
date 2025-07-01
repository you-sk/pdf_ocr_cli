
import fitz  # PyMuPDF

def create_test_pdf(output_path: str, text: str):
    """Creates a simple one-page PDF with the given text."""
    doc = fitz.open()
    page = doc.new_page()
    
    # Path to the installed IPA Gothic font in the Docker container
    font_path = "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"
    page.insert_text((50, 72), text, fontsize=11, fontfile=font_path)
    
    doc.save(output_path)
    doc.close()

if __name__ == '__main__':
    # Create a Japanese sample PDF
    create_test_pdf("test_jp.pdf", "これは日本語のテストです。")
    # Create an English sample PDF
    create_test_pdf("test_en.pdf", "This is an English test.")
    print("Created test_jp.pdf and test_en.pdf")
