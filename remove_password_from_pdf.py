import pikepdf
from dotenv import load_dotenv
import os
# Load the environment variables from the .env file
load_dotenv()
password = os.getenv("PDF_PASSWORD")
if not password:
    print("Password not found in environment variables.")

def remove_password_from_pdf(filename, password=None):
    pdf = pikepdf.open(filename, password=password)
    pdf.save("pdf_file_with_no_password.pdf")

if __name__ == "__main__":
    remove_password_from_pdf("statement.pdf", password)