# ACCESS_TOKEN = "1000.358593bdf1e1d10af487518ec385e0ed.13fcdd834428eddc1af11097f199d539"
import requests
from datetime import datetime, date
import calendar

ACCESS_TOKEN = "1000.7ab62a7056e3739946d9060fd5c5b781.a6717c79fcb64b7de4a5afc27da7bbe6"
ORGANIZATION_ID = "730309921"

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

    # Start of current year
    start_date = date(today.year, 1, 1)

    # Calculate previous month and year
    if today.month == 1:
        prev_month = 12
        prev_year = today.year - 1
    else:
        prev_month = today.month - 1
        prev_year = today.year

    # Last day of previous month
    last_day_prev_month = calendar.monthrange(prev_year, prev_month)[1]

    # End date = last day of previous month
    end_date = date(prev_year, prev_month, last_day_prev_month)

    # Uncomment to debug date range:
    # print(f"Filtering invoices from {start_date.isoformat()} to {end_date.isoformat()}")

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

        # Uncomment to debug invoices:
        # print(f"Invoice {invoice_number} due date: {due_date.isoformat()}")
        print(f"Due date: {due_date} | Start date: {start_date} | End date: {end_date} | Included: {start_date <= due_date <= end_date}")
        if start_date <= due_date <= end_date:
            due_invoices.append({
                "customer": customer,
                "balance": balance,
                "invoice_number": invoice_number,
                "due_date": due_date_str
            })

    if not due_invoices:
        return "No overdue payments found in the specified date range."

    # Build the table string
    # Build the table string with Due Date included
    table_header = f"{'Company Name':<30} | {'Amount Due':<12} | {'Invoice No':<15} | {'Due Date':<10}\n"
    table_header += "-" * 80 + "\n"

    table_rows = ""
    for inv in due_invoices:
        # Format the due date as YYYY-MM-DD
        due_date_str = inv.get("due_date", "N/A")
        table_rows += f"{inv['customer']:<30} | {inv['balance']:<12.2f} | {inv['invoice_number']:<15} | {due_date_str:<10}\n"

    return table_header + table_rows



if __name__ == "__main__":
    message = fetch_due_payments()
    print(message)
    # --- TELEGRAM CONFIGURATION ---
# TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
# TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"  # Example: 123456789

# def send_to_telegram(message):
#     url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
#     payload = {
#         "chat_id": TELEGRAM_CHAT_ID,
#         "text": f"<pre>{message}</pre>",
#         "parse_mode": "HTML"
#     }
#     response = requests.post(url, data=payload)
#     if response.status_code != 200:
#         print(f"Telegram Error: {response.status_code} - {response.text}")
#     else:
#         print("✅ Message sent to Telegram.")

# if __name__ == "__main__":
#     message = fetch_due_payments()
#     print(message)  # For debugging in terminal
#     send_to_telegram(message)
