import requests
from bs4 import BeautifulSoup
import re

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
    print("Nature's Blend Offer Diagnostic")
    print("==========================================")

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

    print()
    print("Searching page for text containing '3 Bags'...")
    print()

    found = 0

    for element in soup.find_all(["div", "span", "p", "label", "li"]):
        text = element.get_text(" ", strip=True)

        if re.search(r"3\s+Bags", text, re.IGNORECASE):

            # Only show reasonably small pieces of text.
            if len(text) <= 300:

                print("------------------------------------------")
                print(text)

                # Also show any dollar amounts in this exact piece.
                prices = re.findall(
                    r"\$\s*[\d,]+\.\d{2}",
                    text
                )

                if prices:
                    print("Prices in this piece:")
                    print(", ".join(prices))

                found += 1

                # Stop after the first 15 useful matches.
                if found >= 15:
                    break

    print()
    print("==========================================")
    print(f"Diagnostic matches shown: {found}")
    print("==========================================")


if __name__ == "__main__":
    main()
