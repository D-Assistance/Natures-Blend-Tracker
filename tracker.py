import requests
from bs4 import BeautifulSoup
import re

# ============================================================
# NATURE'S BLEND PRICE TRACKER
# 3-BAG OFFER TEST
# ============================================================

URL = "https://www.naturesblendbydrmarty.com/"

MAX_BAGS = 3
TARGET_PRICE = 25.00

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def money_to_float(value):
    """Convert a price such as '$85.35' into 85.35."""
    return float(value.replace("$", "").replace(",", "").strip())


def find_three_bag_offers(text):
    """
    Find 3-bag offers by looking for the specific pattern:

    3 Bags Save $94 $85.35

    The first dollar amount is the savings amount.
    The second dollar amount is the actual package price.
    """

    pattern = re.compile(
        r"3\s+Bags\s+Save\s+\$[\d,]+\.\d{2}\s+"
        r"\$([\d,]+\.\d{2})",
        re.IGNORECASE
    )

    matches = pattern.findall(text)

    offers = []

    for match in matches:
        package_price = money_to_float(match)
        price_per_bag = package_price / MAX_BAGS

        if package_price not in [offer["package_price"] for offer in offers]:
            offers.append({
                "package_price": package_price,
                "bags": MAX_BAGS,
                "price_per_bag": price_per_bag
            })

    return offers


def main():
    print("==========================================")
    print("Nature's Blend 3-Bag Price Test")
    print("==========================================")
    print(f"Maximum qualifying purchase: {MAX_BAGS} bags")
    print(f"Target price: ${TARGET_PRICE:.2f} per bag")
    print()

    try:
        response = requests.get(
            URL,
            headers=HEADERS,
            timeout=20
        )

        print(f"Website response status: {response.status_code}")

        if response.status_code != 200:
            print("The website blocked the tracker.")
            return

        soup = BeautifulSoup(response.text, "html.parser")

        # Convert the webpage to clean text.
        text = soup.get_text(" ", strip=True)

        # ----------------------------------------------------
        # Check whether the product is currently available.
        # ----------------------------------------------------

        out_of_stock = bool(
            re.search(
                r"sorry,\s*we'?re\s+currently\s+out\s+of\s+stock",
                text,
                re.IGNORECASE
            )
        )

        if out_of_stock:
            print("Product availability: OUT OF STOCK")
        else:
            print("Product availability: AVAILABLE or status unclear")

        print()

        # ----------------------------------------------------
        # Find only the 3-bag package offers.
        # ----------------------------------------------------

        offers = find_three_bag_offers(text)

        if not offers:
            print("No 3-bag package offer was found.")
            print()
            print("The page structure may have changed.")
            return

        print("3-bag package offers found:")
        print()

        for offer in offers:
            print(
                f"3 bags: ${offer['package_price']:.2f} total"
            )
            print(
                f"Price per bag: ${offer['price_per_bag']:.2f}"
            )

            if offer["price_per_bag"] <= TARGET_PRICE:
                print("TARGET REACHED: $25.00 or less per bag")
            else:
                print("Above $25.00 target")

            print()

        # ----------------------------------------------------
        # Select the lowest qualifying 3-bag price.
        # ----------------------------------------------------

        lowest = min(
            offers,
            key=lambda offer: offer["price_per_bag"]
        )

        print("------------------------------------------")
        print("LOWEST QUALIFYING 3-BAG PRICE")
        print("------------------------------------------")
        print(
            f"Total for 3 bags: ${lowest['package_price']:.2f}"
        )
        print(
            f"Price per bag: ${lowest['price_per_bag']:.2f}"
        )

        if lowest["price_per_bag"] <= TARGET_PRICE:
            print("ALERT CONDITION: YES")
        else:
            print("ALERT CONDITION: NO")

    except Exception as e:
        print(f"Error connecting to page: {e}")

    print()
    print("==========================================")
    print("3-bag price test complete.")
    print("==========================================")


if __name__ == "__main__":
    main()
