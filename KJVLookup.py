import requests
import os
import re
from typing import List, Dict

# ANSI colors
YELLOW = "\033[1;33m"
RESET = "\033[0m"
DIM = "\033[2m"
BOLD = "\033[1m"

LOCAL_FILE = "kjv.txt"
SOURCE_URL = "https://openbible.com/textfiles/kjv.txt"

def download_bible_if_needed():
    if os.path.exists(LOCAL_FILE):
        print(f"Using existing local KJV: {LOCAL_FILE}")
        return

    print("Downloading KJV text file (one-time, ~4 MB)...")
    try:
        r = requests.get(SOURCE_URL, timeout=15)
        r.raise_for_status()
        with open(LOCAL_FILE, "w", encoding="utf-8") as f:
            f.write(r.text)
        print("Download complete. Bible loaded locally.")
    except Exception as e:
        print(f"Download failed: {e}")
        print("Cannot continue without the text file. Exiting.")
        exit(1)


def load_bible() -> List[Dict]:
    download_bible_if_needed()
    bible = []
    with open(LOCAL_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or "\t" not in line:
                continue
            ref, text = line.split("\t", 1)
            bible.append({"ref": ref.strip(), "text": text.strip()})
    print(f"Loaded {len(bible):,} verses into memory.\n")
    return bible


def get_context_around_match(text: str, phrase: str, context_words: int = 20) -> str:
    """
    Extract ~context_words before & after the phrase, with highlighting.
    Tries to stop at word boundaries.
    """
    phrase_lower = phrase.lower()
    text_lower = text.lower()
    pos = text_lower.find(phrase_lower)
    if pos == -1:
        return text

    phrase_len = len(phrase)

    # Find start of context before
    before_start = pos
    words_count = 0
    while before_start > 0 and words_count < context_words:
        before_start -= 1
        if text[before_start].isspace() and before_start > 0 and not text[before_start - 1].isspace():
            words_count += 1

    # Adjust to start after space if possible
    if before_start > 0 and text[before_start - 1].isspace():
        before_start -= 1
    before_text = text[before_start:pos].rstrip()
    if before_start > 0:
        before_text = "…" + before_text

    # Find end of context after
    after_end = pos + phrase_len
    words_count = 0
    while after_end < len(text) and words_count < context_words:
        after_end += 1
        if text[after_end - 1].isspace() and after_end < len(text) and not text[after_end].isspace():
            words_count += 1

    after_text = text[pos + phrase_len:after_end].lstrip()
    if after_end < len(text):
        after_text += "…"

    return f"{DIM}{before_text}{RESET} {YELLOW}{text[pos:pos + phrase_len]}{RESET} {DIM}{after_text}{RESET}"


def search_bible(phrase: str, bible_data: List[Dict]) -> List[Dict]:
    phrase = phrase.strip()
    if not phrase:
        return []

    print(f"\n{YELLOW}Searching for:{RESET} {BOLD}{phrase}{RESET}")
    matches = []

    for verse in bible_data:
        if phrase.lower() in verse["text"].lower():
            context = get_context_around_match(verse["text"], phrase)
            matches.append({
                "reference": verse["ref"],
                "context": context,
            })

    return matches


def print_matches(matches: List[Dict], phrase: str):
    if not matches:
        print(f"  No matches found for '{phrase}'.\n")
        return

    print(f"\n{BOLD}Found {len(matches)} occurrence{'s' if len(matches) > 1 else ''}:{RESET}\n")

    for i, m in enumerate(matches, 1):
        print(f"  {i:3d}. {BOLD}{m['reference']}{RESET}")
        print(f"      {m['context']}")
        print()


def main():
    print("Fast In-Memory KJV Bible Phrase Finder")
    print("(searches are instant after one-time ~4 MB download)\n")
    print("Tip: Press Ctrl+C or close the window to exit.\n")

    bible = load_bible()

    while True:
        try:
            phrase = input("Phrase / words to find: ").strip()
        except EOFError:
            print("\nGoodbye!\n")
            break

        if not phrase:
            print("Enter something to search (empty input ignored).\n")
            continue

        results = search_bible(phrase, bible)
        print_matches(results, phrase)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye!\n")
