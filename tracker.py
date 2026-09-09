import os
import re
import json
from datetime import datetime, timezone
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
import requests
from bs4 import BeautifulSoup


URL = "https://www.naturesblendbydrmarty.com/"
PURCHASE_URL = "https://www.naturesblendbydrmarty.com/"
HISTORY_FILE = "price_history.json"

MAX_BAGS = 3
TARGET_PRICE = 25.00


def fetch_page():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/150.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(URL, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text

def find_three_bag_offers(soup):
    """
    Find the 3-bag prices from the official Nature's Blend page.

    The page currently contains several references to "3 Bags."
    We use the first two unique, complete 3-bag price entries:
      1. One-time purchase
      2. Subscription

    Other matches are ignored because the page's HTML can associate
    a savings amount with the wrong package.
    """

    pattern = re.compile(
        r"3\s+Bags\s+Save\s+\$[\d,]+(?:\.\d{2})?\s+\$([\d,]+(?:\.\d{2})?)",
        re.IGNORECASE,
    )

    matches = []

    for element in soup.find_all(["div", "span", "p", "label", "li"]):
        text = " ".join(element.get_text(" ", strip=True).split())

        match = pattern.search(text)

        if match:
            price = float(match.group(1).replace(",", ""))

            if price not in [item["price"] for item in matches]:
                matches.append({
                    "text": text,
                    "price": price,
                })

    # We need at least one genuine 3-bag price.
    if not matches:
        return []

    # The first unique match is the one-time price.
    # The second unique match is the subscription price.
    return matches[:2]


def check_availability(soup):
    page_text = soup.get_text(" ", strip=True).lower()

    out_of_stock_phrases = [
        "sorry, we're currently out of stock",
        "currently out of stock",
        "out of stock",
    ]

    for phrase in out_of_stock_phrases:
        if phrase in page_text:
            return False

    return True


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return []


def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=2)


def send_discord(message):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")

    if not webhook_url:
        print("Discord webhook secret not found.")
        return

    response = requests.post(
        webhook_url,
        json={"content": message},
        timeout=30,
    )

    response.raise_for_status()
    print("Discord notification sent.")


def send_email(subject, message):
    gmail_username = os.environ.get("GMAIL_USERNAME")
    gmail_app_password = os.environ.get("GMAIL_APP_PASSWORD")

    if not gmail_username or not gmail_app_password:
        print("Email settings are missing.")
        return

    email = EmailMessage()
    email["From"] = gmail_username
    email["To"] = gmail_username
    email["Subject"] = subject
    email.set_content(message)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(gmail_username, gmail_app_password)
        smtp.send_message(email)

    print("Email alert sent.")


def main():
    print("==========================================")
    print("Dr. Marty Nature's Blend Price Tracker")
    print("==========================================")

    html = fetch_page()
    soup = BeautifulSoup(html, "html.parser")

    offers = find_three_bag_offers(soup)

    if not offers:
        print("ERROR: Could not find the 3-bag price.")
        print("No price will be recorded.")
        return

    # The first unique 3-bag price is the one-time purchase.
    one_time_price = offers[0]["price"]
    price_per_bag = one_time_price / MAX_BAGS

    # The second unique 3-bag price is the subscription price.
    subscription_price = None
    if len(offers) >= 2:
        subscription_price = offers[1]["price"]

    available = check_availability(soup)

    print(f"3-bag one-time price: ${one_time_price:.2f}")
    print(f"Price per bag: ${price_per_bag:.2f}")

    if subscription_price is not None:
        print(f"3-bag subscription price: ${subscription_price:.2f}")
        print(
            f"Subscription price per bag: "
            f"${subscription_price / MAX_BAGS:.2f}"
        )

    print(f"Currently available: {available}")

    history = load_history()

    # Only available, one-time offers count as qualifying prices.
    qualifying_records = [
        record
        for record in history
        if record.get("available") is True
        and record.get("offer_type") == "one-time"
    ]

    previous_low = None

    if qualifying_records:
        previous_low = min(
            record["price_per_bag"]
            for record in qualifying_records
        )

    timestamp = datetime.now(timezone.utc).isoformat()

    record = {
        "timestamp": timestamp,
        "date": timestamp[:10],
        "source": URL,
        "offer_type": "one-time",
        "bags": MAX_BAGS,
        "package_price": one_time_price,
        "price_per_bag": round(price_per_bag, 2),
        "available": available,
    }

    history.append(record)
    save_history(history)

    print("------------------------------------------")
    print("This run has been recorded in price_history.json")

    # Do not send a deal alert when the product is unavailable.
    if not available:
        print("No alert: product is currently out of stock.")
        return

    messages = []

    if price_per_bag <= TARGET_PRICE:
        messages.append(
            f"🎉 Dr. Marty Nature's Blend is ${price_per_bag:.2f}/bag "
            f"for 3 bags — at or below your ${TARGET_PRICE:.2f} target!\n"
            f"🛒 Buy/check the offer: {PURCHASE_URL}"
        )

    if previous_low is None or price_per_bag < previous_low:
        messages.append(
            f"🏆 NEW ALL-TIME LOW: Dr. Marty Nature's Blend is now "
            f"${price_per_bag:.2f}/bag for 3 bags "
            f"(${one_time_price:.2f} total).\n"
            f"🛒 Buy/check the offer: {PURCHASE_URL}"
        )

    if messages:
        message = "\n".join(messages)
        send_discord(message)
        send_email("Dr. Marty Nature's Blend Price Alert", message)
    else:
        print("No alert needed.")

    print("Tracker completed successfully.")


if __name__ == "__main__":
    main()
