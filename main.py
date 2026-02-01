import cv2
import pytesseract
from pdf2image import convert_from_path
from deep_translator import GoogleTranslator
import numpy as np

# Path to tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Paths
pdf_path = "arabicInvoice.pdf"
poppler_path = r"C:\Program Files\poppler-25.12.0\poppler-25.12.0\Library\bin"

# Convert PDF to images
pages = convert_from_path(
    pdf_path,
    dpi=300,
    poppler_path=poppler_path
)

arabic_text = ""

for page in pages:
    img = np.array(page)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Thresholding
    gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

    # OCR Arabic
    text = pytesseract.image_to_string(
        gray,
        lang="ara",
        config="--oem 3 --psm 6"
    )

    arabic_text += text + "\n"

print("ARABIC TEXT:\n", arabic_text)

# Translate Arabic → English
english_text = GoogleTranslator(source="ar", target="en").translate(arabic_text)
print("\nENGLISH TEXT:\n", english_text)
