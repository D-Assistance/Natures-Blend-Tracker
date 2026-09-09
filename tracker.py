import requests
from bs4 import BeautifulSoup
import re

# ============================================================
# NATURE'S BLEND PRICE TRACKER
# 3-BAG PRICE TEST
# ============================================================

URL = "https://www.naturesblendbydrmarty.com/"

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


def main():
    print("==========================================")
    print("Nature's Blend 3-Bag Price Test")
    print("==========================================")

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

        # Look through the page for text containing the 3-bag offer.
        found = False

        for element in soup.find_all(["div", "span", "p", "label", "li"]):
            text = element.get_text(" ", strip=True)

            if not text:
                continue

            # Look for wording that identifies a 3-bag offer.
            if re.search(
                r"\b3\s*(?:bags?|x\s*bags?)\b",
                text,
                re.IGNORECASE
            ):
                prices = re.findall(
                    r"\$\s*(\d+(?:\.\d{2})?)",
                    text
                )

                if prices:
                    print()
                    print("Possible 3-bag offer found:")
                    print(text[:500])

                    for price in prices:
                        value = float(price)
                        per_bag = value / 3

                        print(
                            f"Price: ${value:.2f} "
                            f"= ${per_bag:.2f} per bag"
                        )

                    found = True

        if not found:
            print()
            print("No clearly labeled 3-bag offer was found.")
            print()
            print("The page is accessible, but we need")
            print("to inspect how the offer is labeled.")

    except Exception as e:
        print(f"Error connecting to page: {e}")

    print()
    print("==========================================")
    print("3-bag price test complete.")
    print("==========================================")


if __name__ == "__main__":
    main()
