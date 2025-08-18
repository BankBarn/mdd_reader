from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import os

with open("carlson.html", 'r') as file_object:
    sample_html = file_object.read()
    

def extract_card_bits(html: str) -> List[Dict[str, Optional[str]]]:
    """
    Parse all cards and return [{'title': ..., 'footer': ...}, ...]
    where title is from `.card-title` and footer from `.mdd-highcharts-footer`.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Prefer explicit card containers; if none, fall back to the host tag.
    cards = soup.select(".card-container")
    if not cards:
        cards = soup.select("mdd-indicator-card")

    results: List[Dict[str, Optional[str]]] = []
    for card in cards:
        # Search within the card only
        title_el = card.select_one(".card-title")
        body_el = card.select_one(".mdd-indicator-container")
        footer_el = card.select_one(".mdd-highcharts-footer")

        # Robust text extraction: collapse internal whitespace
        title = title_el.get_text(" ", strip=True) if title_el else None
        body = body_el.get_text(" ", strip=True) if body_el else None
        footer = footer_el.get_text(" ", strip=True) if footer_el else None

        # Normalize empties to None
        title = title or None
        body = body or None
        footer = footer or None

        # Only append if at least one is present (optional)
        if title is not None or footer is not None:
            results.append({"title": title, "data": body, "footer": footer})

    return results


# --- example ---
if __name__ == "__main__":
    print(extract_card_bits(sample_html))
    # [{'title': 'Total Milk Production', 'footer': '4-day avg on Apr 16'}]
