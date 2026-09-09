import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

# ============================================================
# NATURE'S BLEND PRICE TRACKER
# ============================================================

# We are only interested in offers of 1, 2, or 3 bags.
MAX_BAGS = 3

# Your personal sale benchmark.
TARGET_PRICE = 25.00

# Official Nature's Blend offer page.
OFFER_URL = "https://www.naturesblendbydrmarty.com/"

# Discord webhook is stored securely in GitHub.
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# File where we will eventually keep the price history.
HISTORY_FILE = "price_history.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def get_page():
    """Download the Nature's Blend offer page."""
    try:
        response = requests.get(
            OFFER_URL,
            headers=HEADERS,
            timeout=20
        )

        print(f"Website response status: {response.status_code}")

        if response.status_code != 200:
            print("The website did not allow the tracker to read the page.")
            return None

        return response.text

    except Exception as e:
        print(f"Error connecting to website: {e}")
        return None


def find_prices(page):
    """
    Look through the page for dollar amounts.

    This first test deliberately reports what prices are present
    rather than making assumptions about which one is the sale price.
    """
    soup = BeautifulSoup(page, "html.parser")

    text = soup.get_text(" ", strip=True)

    import re

    prices = re.findall(r"\$\s*(\d+(?:\.\d{2})?)", text)

    unique_prices = []

    for price in prices:
        value = float(price)

        if value not in unique_prices:
            unique_prices.append(value)

    return unique_prices


def main():
    print("==========================================")
    print("Nature's Blend Price Tracker")
    print("==========================================")
    print(f"Maximum qualifying purchase: {MAX_BAGS} bags")
    print(f"Sale benchmark: ${TARGET_PRICE:.2f} per bag")
    print()

    page = get_page()

    if page is None:
        print("Price check could not be completed.")
        return

    prices = find_prices(page)

    if not prices:
        print("No dollar prices were found on the page.")
        return

    print("Dollar amounts found on the page:")

    for price in prices:
        print(f"  ${price:.2f}")

    print()
    print("The tracker successfully reached the offer page.")
    print("Next we will identify which prices belong to 1-, 2-,")
    print("and 3-bag offers so we do not mistake unrelated prices")
    print("for the actual Nature's Blend price.")


if __name__ == "__main__":
    main()
