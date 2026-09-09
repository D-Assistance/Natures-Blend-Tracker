import requests
from bs4 import BeautifulSoup
import re

# ============================================================
# NATURE'S BLEND PRICE TRACKER
# ============================================================

MAX_BAGS = 3
TARGET_PRICE = 25.00

# Official Nature's Blend pages we will try.
OFFER_URLS = [
    "https://www.naturesblendbydrmarty.com/",
    "https://offer.drmartypets.com/tv/os.php",
    "https://offer.drmartypets.com/sms/os.php",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
              "image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def check_page(url):
    print()
    print("------------------------------------------")
    print(f"Checking: {url}")

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        print(f"Website response status: {response.status_code}")

        if response.status_code != 200:
            print("This page blocked the tracker.")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(" ", strip=True)

        prices = re.findall(r"\$\s*(\d+(?:\.\d{2})?)", text)

        unique_prices = []

        for price in prices:
            value = float(price)

            if value not in unique_prices:
                unique_prices.append(value)

        if unique_prices:
            print("Dollar amounts found:")
            for price in unique_prices:
                print(f"  ${price:.2f}")
        else:
            print("No dollar prices were found.")

    except Exception as e:
        print(f"Error connecting to page: {e}")


def main():
    print("==========================================")
    print("Nature's Blend Price Tracker")
    print("==========================================")
    print(f"Maximum qualifying purchase: {MAX_BAGS} bags")
    print(f"Sale benchmark: ${TARGET_PRICE:.2f} per bag")

    for url in OFFER_URLS:
        check_page(url)

    print()
    print("==========================================")
    print("Price-page test complete.")
    print("==========================================")


if __name__ == "__main__":
    main()
