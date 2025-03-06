import csv
import logging
from dataclasses import dataclass, field, fields, astuple

import requests
from bs4 import Tag, BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"

@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]

QUOTE_FIELDS = [field.name for field in fields(Quote)]

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]: %(message)s",
    handlers=[
        logging.FileHandler("parse.log"),
        logging.StreamHandler()
    ]
)

def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
    text=quote.select_one(".text").text,
    author=quote.select_one(".author").text,
    tags=[tag.text for tag in quote.select(".tag")]
    )

def get_home_quotes() -> [Quote]:
    text = requests.get(BASE_URL).content
    soup = BeautifulSoup(text, "html.parser")
    quotes = soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]

def get_num_pages(page_soup: Tag) -> int:
    pagination = page_soup.select_one(".pager")
    if not pagination:
        # If no pagination is found, assume there's only one page
        return 1
    # Find the last page number from the pager links
    page_links = pagination.select("a[href]")
    if not page_links:
        return 1
    # Extract numbers from hrefs and find the maximum
    try:
        page_numbers = [int(a["href"].split("/")[-2]) for a in page_links if a["href"].split("/")[-2].isdigit()]
        return max(page_numbers) if page_numbers else 1
    except (KeyError, ValueError):
        # Return 1 if there's any unexpected issue parsing numbers
        return 1


def single_page_quotes(soup: Tag) -> [Quote]:
    quotes = soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]

def get_all_quotes() -> [Quote]:
    logging.info("Getting all quotes")
    text = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(text, "html.parser")
    all_quotes = single_page_quotes(first_page_soup)
    num_pages = get_num_pages(first_page_soup)
    for page_num in range(1, num_pages + 1):
        logging.info(f"Getting quotes from page {page_num}")
        text = requests.get(BASE_URL, {"page": page_num}).content
        next_page_soup = BeautifulSoup(text, "html.parser")
        all_quotes.extend(single_page_quotes(next_page_soup))
    return all_quotes

def output_csv_path(quotes: [Quote]) -> None:
    with open("results.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quotes) for quotes in quotes])

def main() -> None:
    output_csv_path(get_all_quotes())



if __name__ == "__main__":
    main()
