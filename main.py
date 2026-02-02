import re
import json
import pdfplumber
import cv2
import pytesseract
from pdf2image import convert_from_path
import numpy as np

# -------------------------------
# CONFIGURATION
# -------------------------------
pdf_path = "test2.pdf"

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
poppler_path = r"C:\Program Files\poppler-25.12.0\poppler-25.12.0\Library\bin"


# -------------------------------
# STEP 1: TRY TEXT EXTRACTION (BEST)
# -------------------------------
arabic_text = ""

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            arabic_text += text + "\n"


# -------------------------------
# STEP 2: IF NO TEXT FOUND → OCR
# -------------------------------
if arabic_text.strip() == "":
    pages = convert_from_path(
        pdf_path,
        dpi=300,
        poppler_path=poppler_path
    )

    for page in pages:
        img = np.array(page)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

        text = pytesseract.image_to_string(
            gray,
            lang="ara",
            config="--oem 3 --psm 6"
        )

        arabic_text += text + "\n"


# -------------------------------
# STEP 3: NORMALIZE NUMBERS
# -------------------------------
def normalize_numbers(text):
    arabic_to_english = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
    return text.translate(arabic_to_english)


arabic_text = normalize_numbers(arabic_text)


# -------------------------------
# STEP 4: EXTRACT INVOICE DATA
# -------------------------------
def extract_invoice_data(text):
    data = {}

    # Invoice number (long number)
    numbers = re.findall(r'\d+', text)
    long_numbers = [n for n in numbers if len(n) >= 8]
    data["invoice_number"] = long_numbers[0] if long_numbers else "Not found"

    # Issue date (yyyy/mm/dd or dd/mm/yyyy)
    date = re.search(
        r'\d{4}[-/]\d{2}[-/]\d{2}|\d{2}[-/]\d{2}[-/]\d{4}',
        text
    )
    data["issue_date"] = date.group() if date else "Not found"

    # Total amount = largest decimal number
    amounts = re.findall(r'\d+\.\d{2}', text)
    data["total_amount"] = max(amounts, key=float) if amounts else "Not found"

    return data


invoice_data = extract_invoice_data(arabic_text)


# -------------------------------
# STEP 5: PRINT REPORT
# -------------------------------
print("\n📄 INVOICE REPORT")
print("------------------------")
print("Invoice Number :", invoice_data["invoice_number"])
print("Issue Date     :", invoice_data["issue_date"])
print("Total Amount   :", invoice_data["total_amount"], "SAR")
print("Source File    :", pdf_path)
print("Language       : Arabic")


# -------------------------------
# STEP 6: SAVE REPORT
# -------------------------------
with open("invoice_report.json", "w", encoding="utf-8") as f:
    json.dump(invoice_data, f, indent=4, ensure_ascii=False)
