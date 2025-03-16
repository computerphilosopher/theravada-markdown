import requests
from bs4 import BeautifulSoup
import concurrent.futures

def fetch_page(url: str) -> BeautifulSoup:
    """Fetches the HTML content of a given URL and returns a BeautifulSoup object."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"❌ Failed to fetch {url}")
            return None
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"⚠️ Error fetching {url}: {e}")
        return None

def extract_jataka_info(index: int, base_url: str) -> dict[str, str]:
    """Fetches and extracts Jataka details from the given index."""
    url = f"{base_url}/{index:03d}.htm"
    soup = fetch_page(url)

    if not soup:
        return {
            "Jataka Number": f"Ja {index:03d}",
            "Title": "Unknown",
            "Alternative Titles": "Unknown",
            "Analysis": "No summary available",
            "Characters": "Unknown",
            "Keywords": "Unknown",
            "Full Story": "No content available"
        }

    title_tag = soup.find("p", class_="Heading3")
    jataka_title = " ".join(title_tag.text.split(" ")[1:]).strip() if title_tag else "Unknown"

    alt_title_tag = soup.find("p", string=lambda text: "Alternative Title" in text if text else False)
    alt_title = alt_title_tag.text.replace("Alternative Title: ", "").strip() if alt_title_tag else "Unknown"

    analysis_tag = soup.find("div", class_="analysis")
    summary = analysis_tag.get_text("\n").strip() if analysis_tag else "No summary available"

    characters_tag = analysis_tag.find_all("p") if analysis_tag else []
    characters = [p.get_text().strip() for p in characters_tag if "=" in p.text]
    characters_text = "; ".join(characters) if characters else "Unknown"

    keywords_tag = soup.find("p", string=lambda text: "Keywords" in text if text else False)
    keywords = keywords_tag.text.replace("Keywords: ", "").strip() if keywords_tag else "Unknown"

    body_sections = soup.find_all("div", class_=["translation", "translationX", "versetrans"])
    full_text = "\n\n".join([section.get_text("\n").strip() for section in body_sections]) if body_sections else "No content available"

    ret = {
        "Jataka Number": f"Ja {index:03d}",
        "Title": jataka_title,
        "Alternative Titles": alt_title,
        "Analysis": summary,
        "Characters": characters_text,
        "Keywords": keywords,
        "Full Story": full_text
    }
    #print(ret)
    return ret

def extract_jataka_entries(base_url: str, max_threads: int = 10) -> list[dict[str, str]]:
    """Crawls all Jataka stories using multithreading for faster execution."""
    entries = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_index = {executor.submit(extract_jataka_info, i, base_url): i for i in range(1, 548)}
        for future in concurrent.futures.as_completed(future_to_index):
            result = future.result()
            entries.append(result)
    return sorted(entries, key=lambda x: int(x["Jataka Number"].split(" ")[1]))  # Maintain order

def save_as_markdown(entries: list[dict[str, str]], filename: str = "jataka_stories.md"):
    """Saves Jataka stories in a single Markdown file."""
    with open(filename, "w", encoding="utf-8") as file:
        for entry in entries:
            file.write(f"# {entry['Jataka Number']} {entry['Title']}\n\n")
            file.write("## Alternative Titles\n")
            if entry["Alternative Titles"] != "Unknown":
                for alt in entry["Alternative Titles"].split(";"):
                    file.write(f"- {alt.strip()}\n")
            else:
                file.write("No alternative titles available.\n")
            file.write("\n")

            file.write("## Analysis\n")
            file.write(f"{entry['Analysis']}\n\n")

            file.write("## Characters\n")
            if entry["Characters"] != "Unknown":
                for char in entry["Characters"].split(";"):
                    file.write(f"- {char.strip()}\n")
            else:
                file.write("No characters available.\n")
            file.write("\n")

            file.write("## Keywords\n")
            file.write(f"{entry['Keywords']}\n\n")

            file.write("## Full Story\n")
            file.write(f"{entry['Full Story']}\n\n")
            file.write("---\n\n")

if __name__ == "__main__":
    base_url="https://ancient-buddhist-texts.net/English-Texts/Jataka"
    entries = extract_jataka_entries(base_url, max_threads=10)
    
    save_as_markdown(entries, "jataka_stories.md")
    print("✅ Jataka stories saved as 'jataka_stories.md'")
