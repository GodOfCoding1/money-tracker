from playwright.sync_api import sync_playwright
from pathlib import Path
import re
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import matplotlib.pyplot as plt
def plot_recipient_sums(recipient_sums):
    recipients = list(recipient_sums.keys())
    amounts = list(recipient_sums.values())

    plt.figure(figsize=(12, 8))
    plt.barh(recipients, amounts, color='skyblue')
    plt.xlabel('Total Paid Amount (₹)')
    plt.ylabel('Recipients')
    plt.title('Total Amount Paid to Recipients')
    plt.tight_layout()
    plt.show()
# Function to extract the desired data
def extract_data_from_html(file_path, start_date, end_date):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Load the local HTML file
        page.goto(f'file://{file_path}')

        # Use a CSS selector to locate the specific div
        
        # Selector for the main container div
        transaction_selector = "div.outer-cell.mdl-cell.mdl-cell--12-col.mdl-shadow--2dp"
        transactions = page.query_selector_all(transaction_selector)
        recipient_sums = defaultdict(float)

        if transactions:
            for transaction in transactions:
                # Extract transaction details
                amount_time_selector = "div[class='content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1']"
                details_selector = "div.content-cell.mdl-cell.mdl-cell--12-col.mdl-typography--caption"

                amount_time_element = transaction.query_selector(amount_time_selector)
                details_element = transaction.query_selector(details_selector)

                if amount_time_element:
                    amount_time_text = amount_time_element.inner_text()
                    # print(amount_time_text)
                    time_text= amount_time_text.split('\n')[1]

                    # Extract action (Paid, Received, Sent), amount, and time of transaction
                    action_match = re.search(r"\b(Paid|Received|Sent)\b", amount_time_text)
                    amount_match = re.search(r"\u20b9([\d,.]+)", amount_time_text)
                    time_match = re.search(r"\d{1,2} \w{3,4} \d{4}, \d{2}:\d{2}:\d{2} GMT[+-]\d{2}:\d{2}", amount_time_text)
                    recipient_match = re.search(r"to (.*?) using Bank Account", amount_time_text)

                    action = action_match.group(1) if action_match else "Not found"
                    paid_amount = float(amount_match.group(1).replace(",", "")) if amount_match else 0.0
                    # transaction_time = time_match.group(0) if time_match else "Not found"
                    transaction_time_str = time_text.replace("Sept", "Sep")
                    recipient = recipient_match.group(1) if recipient_match else "Not found"

                if details_element:
                    details_text = details_element.inner_text()

                    # Extract status
                    status_match = re.search(r"\b(Completed|Failed|Pending)\b", details_text)
                    status = status_match.group(1) if status_match else "Not found"
                # Parse transaction time and compare with after_date
                if transaction_time_str != "Not found":
                    transaction_time = datetime.strptime(transaction_time_str, "%d %b %Y, %H:%M:%S GMT%z")
                    # Ensure start_date and end_date are in IST timezone
                    if start_date.tzinfo is None:
                        start_date = start_date.replace(tzinfo=timezone(timedelta(hours=5, minutes=30)))
                    if end_date.tzinfo is None:
                        end_date = end_date.replace(tzinfo=timezone(timedelta(hours=5, minutes=30)))

                    if start_date <= transaction_time <= end_date and action in ["Paid","Sent"]:
                        if details_element:
                            details_text = details_element.inner_text()

                            # Extract status
                            status_match = re.search(r"\b(Completed|Failed|Pending)\b", details_text)
                            status = status_match.group(1) if status_match else "Not found"

                            if status == "Completed":
                                recipient_sums[recipient] += float(paid_amount)

                # Print the extracted details
                # print("Action:", action)
                # print("Amount:", paid_amount)
                # print("Transaction Time:", transaction_time)
                # print("Recipient:", recipient)
                # print("Status:", status)
                # print("---")
            print("Dict",recipient_sums)
            sorted_arr=[]
            for key,value in recipient_sums.items():
                sorted_arr.append([value,key])
            sorted_arr.sort(reverse=True)
            for transaction in sorted_arr[:10]:
                print(transaction)
            print("Total Money Used:", sum(list(recipient_sums.values())))
            plot_recipient_sums(recipient_sums)
        else:
            print("No transactions found")

        # Close the browser
        browser.close()

# Replace 'path_to_file.html' with the actual path to your HTML file
# extract_data_from_html(Path(Path.cwd(),"data","gpay","Google Pay","My Activity","My Activity.html"), datetime(2024, 11, 1))

# Replace 'path_to_file.html' with the actual path to your HTML file
# Replace '2024-01-01' and '2024-12-31' with your desired start and end dates, ensure they are in IST timezone
extract_data_from_html(Path(Path.cwd(), "data", "gpay", "Google Pay", "My Activity", "My Activity.html"), 
                       datetime(2024, 6, 1, tzinfo=timezone(timedelta(hours=5, minutes=30))), 
                       datetime(2024, 12, 1, tzinfo=timezone(timedelta(hours=5, minutes=30))))