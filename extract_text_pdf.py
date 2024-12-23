from PyPDF2 import PdfReader
from dotenv import load_dotenv
import os
import re

# Load the environment variables from the .env file
load_dotenv()

def extract_text_from_pdf(file_path):
    try:
        # Get the password from the environment
        password = os.getenv("PDF_PASSWORD")
        if not password:
            print("Password not found in environment variables.")
            return None

        # Open the PDF file
        reader = PdfReader(file_path)
        
        # Check if the PDF is encrypted
        if reader.is_encrypted:
            # Try to decrypt the PDF with the password
            if not reader.decrypt(password):
                print("Failed to decrypt the PDF. Please check the password.")
                return None
        
        # Extract text from each page
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        
        return text

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Replace 'path_to_file.pdf' with your PDF file path
file_path = "statement.pdf"
pdf_text = extract_text_from_pdf(file_path)
patterns = [
    r"Details of statementScan the QR code\sto download Vyom on\s+your smartphone",
    r"NEFT : National Electronic Fund Transfer\s+\| UPI : Unified Payment Interface\s+RTGS : Real Time Gross Settlement\s+\| INT : Intra Fund Transfer\s+Bharat Bill Payment ServiceBBPS :\s+This is system generated statement and does not require signature\nhttps://www\.unionbankofindia\.co\.in\nRequest to our customers for immediately notifying their base branch, in case of any discrepancy\s+in the bank statement\.\s+Registered office: Union Bank Bhavan,239,Vidhan Bhavan Marg,Nariman Point,Mumbai-\s+400021,India\.",
    r"S\.No Date Transaction Id Remarks Amount\(Rs\.\) Balance\(Rs\.\)"
]
for pattern in patterns:
    pdf_text = re.sub(pattern, "", pdf_text, flags=re.MULTILINE)

if pdf_text:
    print("Extracted text:")
    print(pdf_text)
else:
    print("No text extracted.")

pattern = r"(\d+)(\d{2}/\d{2}/\d{4}) .*?DR/(.*?)/.*?([\d,]+\.\d+) \(Dr\)"

# Use re.DOTALL to handle newline characters
matches = re.findall(pattern, pdf_text, re.DOTALL)

# Format the extracted data
extracted_data = []
for match in matches:
    serial_number = match[0]
    date = match[1]
    recipient = match[2].replace("\n", "").strip()  # Remove newlines and extra spaces
    debited_amount = float(match[3].replace(",", ""))  # Convert to float
    extracted_data.append({
        "serial_number": serial_number,
        "date": date,
        "recipient": recipient,
        "debited_amount": debited_amount
    })

# Display the extracted data
for data in extracted_data:
    print(data)