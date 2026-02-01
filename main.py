import cv2
import pytesseract
from pdf2image import convert_from_path
from deep_translator import GoogleTranslator
import numpy as np

# Path to tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Paths
pdf_path = "test.pdf"
poppler_path = r"C:\Program Files\poppler-25.12.0\poppler-25.12.0\Library\bin"

# Convert PDF to images
pages = convert_from_path(
    pdf_path,
    dpi=300,
    poppler_path=poppler_path
)

arabic_text = arabic_text = ""


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
import re



def extract_invoice_data(text):
    data = {}

    # Invoice Number (long number)
    inv = re.search(r'\d{10,}', text)
    data["invoice_number"] = inv.group() if inv else "Not found"

    # Issue Date (Arabic context)
    date = re.search(
        r'(تاريخ\s*الإصدار|تاريخ)\D*(\d{2}[-/]\d{2}[-/]\d{4})',
        text
    )
    data["issue_date"] = date.group(2) if date else "Not found"

    # Total Amount (Arabic context)
    total = re.search(
        r'(الإجمالي|إجمالي|المجموع)[^\d]*(\d+\.\d{2})',
        text
    )
    data["total_amount"] = total.group(2) if total else "Not found"

    return data
invoice_data = extract_invoice_data(arabic_text)


print("\n📄 INVOICE REPORT")
print("------------------------")
print("Invoice Number :", invoice_data["invoice_number"])
print("Issue Date     :", invoice_data["issue_date"])
print("Total Amount   :", invoice_data["total_amount"], "SAR")
print("Source File    :", pdf_path)
print("Language       : Arabic")

# print("ARABIC TEXT:\n", arabic_text)

# # Translate Arabic → English
# english_text = GoogleTranslator(source="ar", target="en").translate(arabic_text)
# print("\nENGLISH TEXT:\n", english_text)
import json

with open("invoice_report.json", "w", encoding="utf-8") as f:
    json.dump(invoice_data, f, indent=4, ensure_ascii=False)
