import pandas as pd
import re
import csv
from pathlib import Path
import json

def parse_jataka_markdown(markdown_file_path: str)->list[dict[str, str]]:
    with open(markdown_file_path, "r", encoding="utf-8") as file:
            content = file.read()

    # Split content into individual entries
    entries = re.split(r'^# Ja\s*(\d+)\s+(.*?)\n', content, flags=re.MULTILINE)
    parsed_entries = []

    for i in range(1, len(entries), 3):
        number = entries[i].strip()
        title = entries[i + 1].strip()
        body = entries[i + 2]

        analysis_match = re.search(r'## Analysis\n(.*?)(?:\n##|\Z)', body, re.DOTALL)
        analysis = analysis_match.group(1).strip() if analysis_match else ""

        character_match = re.search(r'## Chracters\n(.*?)(?:\n##|\Z)', body, re.DOTALL)
        characters = character_match.group(1).strip() if  character_match else ""

        keywords_match = re.search(r'## Keywords\n(.*?)(?:\n##|\Z)', body, re.DOTALL)
        keywords = keywords_match.group(1).strip() if keywords_match else ""

        story_match = re.search(r'## Full Story\n(.*?)(?:\n##|\Z)', body, re.DOTALL)
        full_story = story_match.group(1).strip() if story_match else ""

        parsed_entries.append({
            "jataka-number": number,
            "title": title,
            "analysis": analysis,
            "characters": characters,
            "keywords": keywords,
            "full_story": full_story,
        })
    return parsed_entries



def entries_to_csv(entries:list[dict[str,str]], output_csv_path: str):
    with open(output_csv_path, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["jataka-number", "title"])
        writer.writeheader()
        for row in entries:
            writer.writerow({
                "jataka-number": row["jataka-number"],
                "title": row["title"]
            })

    return output_csv_path

def entries_to_json(entries:list[dict[str, str]], output_json_path:str):
    json_data = []

    for entry in entries:
        json_data.append({
            "id": f"Ja{entry['jataka-number']}",
            "title": entry["title"],
            "analysis": entry["analysis"],
            "characters": [c.strip() for c in entry["characters"].split(",") if c.strip()],
            "keywords": [k.strip() for k in entry["keywords"].split(",") if k.strip()],
            "full_story": entry["full_story"]
        })

    with open(output_json_path, "w", encoding="utf-8") as jsonfile:
        json.dump(json_data, jsonfile, ensure_ascii=False, indent=2)

    return output_json_path

entries = parse_jataka_markdown("./jataka_stories.md")
entries_to_csv(entries, "./jataka_stories_index.csv")
entries_to_json(entries, "./jataka_stories_full.json")

#df = pd.read_csv("./jataka_stories_index.csv")
#df.to_excel("./jataka_stories_index.xlsx", index=False)
