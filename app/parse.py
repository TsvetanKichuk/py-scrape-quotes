import csv

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"
AUTHOR_CACHE = {}


def get_quotes_from_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    quotes_data = []
    for quote in soup.select(".quote"):
        text = quote.select_one(".text").get_text(strip=True)
        author = quote.select_one(".author").get_text(strip=True)
        author_url = BASE_URL + quote.select_one("a")["href"]  # Ссылка на страницу автора
        tags = [tag.get_text(strip=True) for tag in quote.select(".tag")]
        quotes_data.append({
            "text": text,
            "author": author,
            "author_url": author_url,
            "tags": tags,
        })
    next_btn = soup.select_one(".pager .next a")
    next_page = BASE_URL + next_btn["href"] if next_btn else None
    return quotes_data, next_page


def get_author_bio(url):
    if url in AUTHOR_CACHE:
        return AUTHOR_CACHE[url]

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    bio = soup.select_one(".author-description").get_text(strip=True)  # Биография
    AUTHOR_CACHE[url] = bio
    return bio


def save_to_csv(file_path, fieldnames, data):
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def main(output_quotes_csv, output_authors_csv=None):
    all_quotes = []
    all_authors = []

    next_page_url = BASE_URL
    while next_page_url:
        quotes, next_page_url = get_quotes_from_page(next_page_url)
        for quote in quotes:
            all_quotes.append({
                "text": quote['text'],
                "author": quote['author'],
                "tags": ", ".join(quote['tags'])
            })
            if output_authors_csv:
                bio = get_author_bio(quote['author_url'])
                all_authors.append({
                    "author": quote['author'],
                    "bio": bio
                })

    save_to_csv(output_quotes_csv, ["text", "author", "tags"], all_quotes)

    if output_authors_csv:
        save_to_csv(output_authors_csv, ["author", "bio"], all_authors)




if __name__ == "__main__":
    main("output_quotes_csv")
