import requests
from bs4 import BeautifulSoup
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

def extract_jataka_entries(soup: BeautifulSoup) -> List[Dict[str, Optional[str]]]:
    """
    Extract Jataka story entries from the table in the HTML.
    Each entry is a dictionary with keys: 'Number', 'Title', 'Link'.
    """
    entries: List[Dict[str, Optional[str]]] = []
    table = soup.find("table")
    if table:
        rows = table.find_all("tr")[1:]  # Skip header row
        for row in rows:
            cols = row.find_all("td")
            if not cols:
                continue  # Skip empty rows

            # Extract the first line from the first column
            first_col_text: str = cols[0].text.strip().split("\n")[0]
            tokens: List[str] = first_col_text.split()
            if len(tokens) < 2 or not tokens[1].isdigit():
                continue

            number: str = tokens[0] + " " + tokens[1]
            title: str = tokens[2] if len(tokens) > 2 else ""

            # Extract the link if available
            title_tag = cols[0].find("a")
            link: Optional[str] = title_tag["href"].strip() if title_tag and title_tag.has_attr("href") else None

            entry: Dict[str, Optional[str]] = {"Number": number, "Title": title, "Link": link}
            entries.append(entry)
            print(entry)
    return entries

def build_dataframe(entries: List[Dict[str, Optional[str]]]) -> pd.DataFrame:
    """
    Build a pandas DataFrame from the list of entries.
    """
    df: pd.DataFrame = pd.DataFrame(entries)
    return df

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
