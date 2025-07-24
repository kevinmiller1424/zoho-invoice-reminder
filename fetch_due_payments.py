import requests
from datetime import datetime, date
import calendar
import os
import sys

# Fetch environment variables
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ORGANIZATION_ID = os.environ.get("ORGANIZATION_ID")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Check if all required env variables are present
missing_vars = []
for var_name, var_value in [
    ("ACCESS_TOKEN", ACCESS_TOKEN),
    ("ORGANIZATION_ID", ORGANIZATION_ID),
    ("TELEGRAM_TOKEN", TELEGRAM_TOKEN),
    ("TELEGRAM_CHAT_ID", TELEGRAM_CHAT_ID)
]:
    if not var_value:
        missing_vars.append(var_name)

if missing_vars:
    print(f"Error: Missing environment variables: {', '.join(missing_vars)}")
    sys.exit(1)

def fetch_due_payments():
    headers = {
        "Authorization": f"Zoho-oauthtoken {ACCESS_TOKEN}"
    }

    url = (
        "https://www.zohoapis.com/books/v3/invoices"
        "?page=1"
        "&per_page=200"
        "&filter_by=Status.OverDue"
        "&sort_column=due_date"
        "&sort_order=D"
        "&usestate=true"
        f"&organization_id={ORGANIZATION_ID}"
    )

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return f"Error: {response.status_code} - {response.text}"

    data = response.json()
    invoices = data.get("invoices", [])
    due_invoices = []

    today = date.today()
    start_date = date(today.year, 1, 1)

    prev_month = today.month - 1 if today.month > 1 else 12
    prev_year = today.year if today.month > 1 else today.year - 1
    end_date = date(prev_year, prev_month, calendar.monthrange(prev_year, prev_month)[1])

    for invoice in invoices:
        balance = float(invoice.get("balance", 0))
        due_date_str = invoice.get("due_date")
        customer = invoice.get("customer_name", "Unknown Customer")
        invoice_number = invoice.get("invoice_number", "N/A")

        if not due_date_str or balance <= 0:
            continue

        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except ValueError:
            continue

        if start_date <= due_date <= end_date:
            due_invoices.append({
                "customer": customer,
                "balance": balance,
                "invoice_number": invoice_number,
                "due_date": due_date_str
            })

    if not due_invoices:
        return "No overdue payments found in the specified date range."

    table_header = f"{'Company Name':<30} | {'Amount Due':<12} | {'Invoice No':<15} | {'Due Date':<10}\n"
    table_header += "-" * 80 + "\n"
    table_rows = ""

    for inv in due_invoices:
        due_date_str = inv.get("due_date", "N/A")
        table_rows += f"{inv['customer']:<30} | {inv['balance']:<12.2f} | {inv['invoice_number']:<15} | {due_date_str:<10}\n"

    return table_header + table_rows


def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"<pre>{message}</pre>",
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=payload)
    if response.status_code != 200:
        print(f"Telegram Error: {response.status_code} - {response.text}")
    else:
        print("✅ Message sent to Telegram.")


if __name__ == "__main__":
    print("Starting fetch_due_payments script...")

    message = fetch_due_payments()
    print("Fetched message:")
    print(message)

    if "Company Name" in message:
        print("Sending message to Telegram...")
        send_to_telegram(message)
    else:
        print("No valid overdue payment data to send.")
