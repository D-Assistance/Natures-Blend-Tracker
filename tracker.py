import requests
from bs4 import BeautifulSoup
import json
import os

# --- CONFIGURATION ---

# Dr. Marty's Nature's Blend product page
URL = "https://drmartypets.com/product/natures-blend"

# Discord webhook is stored securely as a GitHub Secret
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# Alert when the price is at or below this amount
TARGET_PRICE = 34.95

# Make the request look like it is coming from a normal web browser
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def check_price():
    try:
        response = requests.get(URL, headers=HEADERS, timeout=15)

        if response.status_code != 200:
            print(f"Error fetching page: Status code {response.status_code}")
            return

        soup = BeautifulSoup(response.content, "html.parser")

        # Look for common website price formats
        price_element = (
            soup.find("span", {"class": "amount"})
            or soup.find("meta", {"property": "og:price:amount"})
        )

        if price_element:
            if price_element.name == "meta":
                price_text = price_element.get("content")
            else:
                price_text = price_element.text

            cleaned_price = "".join(
                c for c in price_text if c.isdigit() or c == "."
            )

            current_price = float(cleaned_price)

            print(
                f"Current price for Nature's Blend found: "
                f"${current_price:.2f}"
            )

            if current_price <= TARGET_PRICE:
                send_alert(current_price)

        else:
            print(
                "Could not isolate the price element on the page. "
                "Website layout may have changed."
            )

    except Exception as e:
        print(f"An error occurred: {e}")


def send_alert(price):
    if not DISCORD_WEBHOOK_URL:
        print("Discord webhook URL is missing.")
        return

    payload = {
        "username": "Nature's Blend Price Tracker",
        "content": (
            f"🚨 **SALE ALERT!** 🚨\n"
            f"Dr. Marty's Nature's Blend is showing a price of "
            f"**${price:.2f}**!\n"
            f"Check it here: {URL}"
        ),
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(
        DISCORD_WEBHOOK_URL,
        data=json.dumps(payload),
        headers=headers,
        timeout=15,
    )

    if response.status_code == 204:
        print("Alert successfully sent to Discord!")
    else:
        print(
            f"Failed to send Discord alert: "
            f"{response.status_code}"
        )


if __name__ == "__main__":
    check_price()
