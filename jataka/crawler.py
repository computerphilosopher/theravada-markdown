import requests
from bs4 import BeautifulSoup, Tag
import pandas as pd
from typing import List, Dict, Optional

def fetch_page(url: str) -> str:
    """
    Fetch the webpage content from the given URL.
    """
    response = requests.get(url)
    response.encoding = response.apparent_encoding
    response.raise_for_status()
    return response.text

def parse_html(html: str) -> BeautifulSoup:
    """
    Parse the HTML content and return a BeautifulSoup object.
    """
    return BeautifulSoup(html, "html.parser")

def process_row(row: Tag) -> Optional[Dict[str, Optional[str]]]:
    """
    Process a single table row and return a dictionary of the entry if valid.
    """
    cols = row.find("td")
    if not cols:
        return None  # Skip empty rows
    paragraphs = cols.find_all("p")

    # Extract the first line from the first column
    title_raw: str = paragraphs[0].text.strip().split("\n")[0]
    title_tokens: List[str] = title_raw.split()
    if len(title_tokens) < 2 or not title_tokens[1].isdigit():
        return None

    number: str = title_tokens[0] + " " + title_tokens[1]
    title: str = title_tokens[2] if len(title_tokens) > 2 else ""

    # Extract the link if available
    title_tag = paragraphs[0].find("a")
    link: Optional[str] = title_tag["href"].strip() if title_tag and title_tag.has_attr("href") else None

    synopsis = paragraphs[1].text.strip()
    characaters = paragraphs[2].text.strip()

    return {
        "number": number, 
        "title": title, 
        "synopsis": synopsis,
        "characters": characaters,
        "link": link
    }

def extract_jataka_entries(soup: BeautifulSoup) -> List[Dict[str, Optional[str]]]:
    """
    Extract Jataka story entries from the table in the HTML.
    Each entry is a dictionary with keys: 'Number', 'Title', 'Link'.
    """
    entries: List[Dict[str, Optional[str]]] = []
    table = soup.find(
        lambda tag: tag.name == "table" and tag.has_attr('id') and tag['id'] == "Jataka"
    )
    if not table:
        return entries

    # Skip search and header row and process each row individually
    rows = table.find_all("tr")[2:]
    for row in rows:
        entry = process_row(row)
        if entry:
            entries.append(entry)
    return entries

def build_dataframe(entries: List[Dict[str, Optional[str]]]) -> pd.DataFrame:
    """
    Build a pandas DataFrame from the list of entries.
    """
    return pd.DataFrame(entries)

def convert_to_absolute_links(df: pd.DataFrame, base_url: str) -> pd.DataFrame:
    """
    Convert the relative links in the DataFrame to absolute URLs using the base URL.
    """
    if "Link" in df.columns:
        df["Link"] = df["Link"].apply(lambda x: f"{base_url}/{x}" if x else None)
    return df

def fetch_jataka_stories(url: str) -> pd.DataFrame:
    """
    Fetch, parse, extract Jataka stories from the given URL and return a DataFrame.
    """
    html: str = fetch_page(url)
    soup: BeautifulSoup = parse_html(html)
    entries: List[Dict[str, Optional[str]]] = extract_jataka_entries(soup)
    df: pd.DataFrame = build_dataframe(entries)
    base_url: str = "https://ancient-buddhist-texts.net/English-Texts/Jataka"
    df = convert_to_absolute_links(df, base_url)
    return df

if __name__ == "__main__":
    url: str = "https://ancient-buddhist-texts.net/English-Texts/Jataka/000-Jataka-Table.htm"
    df: pd.DataFrame = fetch_jataka_stories(url)
    print(df.head())

    df.to_csv("jataka_stories_index.csv", index=True, encoding="utf-8")
