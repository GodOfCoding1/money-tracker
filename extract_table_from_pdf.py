import pdfplumber
import pandas as pd
import re

def extract_table_from_pdf(pdf_path, page_number=None):
    """
    Extracts tables from a PDF and converts them to a DataFrame.

    :param pdf_path: Path to the PDF file.
    :param page_number: Specific page number to extract the table from (1-indexed). If None, extracts from all pages.
    :return: A list of DataFrames, one for each page or table found.
    """
    tables = []
    
    with pdfplumber.open(pdf_path) as pdf:
        if page_number:
            pages = [pdf.pages[page_number - 1]]  # 1-indexed
        else:
            pages = pdf.pages

        for page in pages:
            page_tables = page.extract_tables()
            for table in page_tables:
                # Convert the extracted table into a DataFrame
                df = pd.DataFrame(table)  # Use the first row as column headers
                tables.append(df)
    
    return tables

# Path to the PDF file
pdf_path = "pdf_file_with_no_password.pdf"

# Extract tables from the PDF
extracted_tables = extract_table_from_pdf(pdf_path, page_number=1)


# Function to extract recipient
def extract_recipient(remarks):
    match = re.search(r"DR/(.*?)(/|$)", remarks, re.DOTALL)
    return match.group(1).strip() if match else None

# Function to extract debited amount
def extract_debit_amount(amount):
    match = re.search(r"([\d,\.]+) \(Dr\)", amount)
    return float(match.group(1).replace(",", "")) if match else None

extracted_tables = extracted_tables[1:]

# Process and display the extracted tables
for i, table in enumerate(extracted_tables, start=1):
    print(f"Table {i}:\n")
    print(table)

    df = pd.DataFrame(table)
    # Extract necessary columns
    df['Recipient'] = df[3].apply(extract_recipient)
    df['Debited Amount'] = df[4].apply(extract_debit_amount)
    df['Date'] = df[1]

    # Filter rows with valid debited amounts
    df_filtered = df[['Date', 'Recipient', 'Debited Amount']].dropna()

    print(df_filtered)
    print(len(df_filtered))
    print("\n")
