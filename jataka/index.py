import pandas as pd

def parse_jataka_markdown_to_csv(markdown_file_path: str, output_csv_path: str):
    import re
    import csv
    from pathlib import Path

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

        story_match = re.search(r'## Full Story\n(.*?)(?:\n##|\Z)', body, re.DOTALL)
        full_story = story_match.group(1).strip() if story_match else ""

        parsed_entries.append({
            "jataka-number": number,
            "title": title,
            "analysis": analysis,
        })

    with open(output_csv_path, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["jataka-number", "title", "analysis"])
        writer.writeheader()
        for row in parsed_entries:
            writer.writerow(row)

    return output_csv_path

# Run the function on the existing file
parse_jataka_markdown_to_csv("./jataka_stories.md", "./jataka_stories_index.csv")

df = pd.read_csv("./jataka_stories_index.csv")
df.to_excel("./jataka_stories_index.xlsx", index=False)
