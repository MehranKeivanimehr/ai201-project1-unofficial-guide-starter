"""
Milestone 3: Document Ingestion & Chunking Pipeline
Loads .txt documents, cleans headers, splits into overlapping chunks.
"""

import os
import sys
import json
import re

# Force UTF-8 for Windows console output
sys.stdout.reconfigure(encoding='utf-8')


def load_documents(folder="documents"):
    """Load all .txt files from the given folder."""
    documents = []
    for filename in sorted(os.listdir(folder)):
        if filename.endswith(".txt"):
            filepath = os.path.join(folder, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                raw_text = f.read()
            documents.append({
                "filename": filename,
                "raw_text": raw_text
            })
    print(f"Loaded {len(documents)} documents from '{folder}/'")
    return documents


def clean_document(text, filename):
    """
    Remove header metadata (everything before ---REVIEWS START--- or ---THREAD START---).
    Also strip leftover metadata lines like 'Quality', 'Difficulty', course codes, dates,
    and tag lines (e.g., 'Tough grader', 'Test heavy') to keep only substantive review text.
    For Reddit files, stop processing when we hit the related-posts section (marked by
    a standalone subreddit name like 'r/ufl' after the thread has already started).
    """
    # Find the content after the start marker
    start_marker = None
    for marker in ["---REVIEWS START---", "---THREAD START---"]:
        if marker in text:
            start_marker = marker
            break

    if start_marker:
        text = text.split(start_marker, 1)[1]

    lines = text.splitlines()
    cleaned_lines = []
    seen_start = False

    # Patterns to skip: standalone metadata/tag lines
    skip_patterns = [
        # Rate My Professors metadata
        r"^Quality$",
        r"^Difficulty$",
        r"^\d+\.\d+$",           # numeric ratings like 4.0, 5.0
        r"^(For Credit|Attendance|Would Take Again|Grade|Textbook|Online Class):",
        r"^[A-Z]{2,}\d{3,}[A-Z]?$",  # course codes like COT3100, COP3503C
        r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}[a-z]{0,2},\s+\d{4}$",
        r"^(Tough grader|Test heavy|Get ready to read|Lots of homework|Lecture heavy|Graded by few things|Clear grading criteria|Beware of pop quizzes|EXTRA CREDIT|Caring|Accessible outside class|Participation matters|Hilarious|Inspirational|Respected|Amazing lectures|Gives good feedback|Skip class\? You won't pass\.|Online Savvy)$",
        # Reddit UI cruft
        r"^u/[A-Za-z0-9_]+\s+avatar$",
        r"^\d+\s+(upvotes?|downvotes?|comments?)$",  # "9 upvotes · 18 comments" or parts
        r"^\d+\s+upvotes\s*·\s*\d+\s+comments$",
        r"^-?\d+$",  # vote scores like -2, -1, 0, 1
        r"^\d+[ymd]o?\s+ago$",  # Reddit timestamps: "8y ago", "6d ago", "5mo ago"
        r"^\d+\s+(minutes?|hours?|days?|weeks?|months?|years?)\s+ago$",
        r"^r/\w+\s+•$",  # "r/ufl •"
        r"^•$",  # standalone bullet
        r"^(OP|Promoted|Sign Up|Join|Public|Top Posts|Reddit|Community Info Section)$",
        r"^reReddit:.*$",
        r"^Thumbnail image:.*$",
        r"^\[deleted\]$",
        r"^Comment deleted by user$",
        r"^Continue this thread$",
        r"^\w+\.(com|net|org)$",  # bare URLs like squarespace.com
        # Reddit usernames: CamelCase OR contains numbers/underscores
        r"^[A-Z][a-z]+[A-Z][a-zA-Z0-9_]*$",  # CamelCase usernames like BreakingBadgauss
        r"^[A-Za-z0-9_]*[0-9_]+[A-Za-z0-9_]*$",  # usernames with numbers or underscores
    ]

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Reddit: once we see a standalone subreddit name AFTER the thread start,
        # we've reached the related-posts sidebar. Stop processing entirely.
        if re.match(r"^r/\w+$", stripped):
            break

        # Check if line matches any skip pattern
        skip = False
        for pattern in skip_patterns:
            if re.match(pattern, stripped, re.IGNORECASE):
                skip = True
                break
        if not skip:
            cleaned_lines.append(stripped)

    cleaned_text = "\n".join(cleaned_lines)
    return cleaned_text


def chunk_text(text, chunk_size=600, overlap=150):
    """
    Split text into overlapping chunks using a sliding window.
    Tries to break at word boundaries (spaces) to avoid cutting words.
    """
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)

        # If we're not at the end, try to find the last space before the cut
        if end < text_len:
            # Look backwards for a space
            search_start = max(start, end - 50)  # don't search back more than 50 chars
            last_space = text.rfind(" ", search_start, end)
            if last_space != -1 and last_space > start:
                end = last_space

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move window forward by chunk_size - overlap
        next_start = start + chunk_size - overlap
        if next_start <= start:
            next_start = start + 1  # safety to prevent infinite loop
        start = next_start

        # If we're near the end and already captured it, stop
        if start >= text_len:
            break

    return chunks


def build_chunks(documents, chunk_size=600, overlap=150):
    """Clean and chunk all documents."""
    all_chunks = []
    for doc in documents:
        cleaned = clean_document(doc["raw_text"], doc["filename"])
        chunks = chunk_text(cleaned, chunk_size=chunk_size, overlap=overlap)
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "filename": doc["filename"],
                "chunk_index": i,
                "text": chunk
            })
        print(f"  {doc['filename']}: {len(chunks)} chunks")
    return all_chunks


def inspect_chunks(all_chunks):
    """Print sample chunks and overlap verification."""
    print(f"\nTotal chunks across all documents: {len(all_chunks)}")

    print("\n" + "=" * 60)
    print("5 REPRESENTATIVE CHUNKS FOR INSPECTION")
    print("=" * 60)

    sample_indices = [
        len(all_chunks) // 10,
        len(all_chunks) // 4,
        len(all_chunks) // 2,
        len(all_chunks) * 3 // 4,
        len(all_chunks) - 5
    ]

    for idx in sample_indices:
        if idx < len(all_chunks):
            chunk = all_chunks[idx]
            print(f"\n--- Chunk {chunk['chunk_index']} from {chunk['filename']} ---")
            print(chunk["text"][:500] + ("..." if len(chunk["text"]) > 500 else ""))
            print(f"[Length: {len(chunk['text'])} characters]")

    print("\n" + "=" * 60)
    print("OVERLAP VERIFICATION")
    print("=" * 60)
    if len(all_chunks) >= 2:
        c1 = all_chunks[0]["text"]
        c2 = all_chunks[1]["text"]
        max_overlap = 0
        for i in range(1, min(len(c1), len(c2), 200)):
            if c1[-i:] == c2[:i]:
                max_overlap = i
        print(f"Overlap between chunk 0 and chunk 1: ~{max_overlap} characters")
        print(f"Expected overlap: ~150 characters")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunk-size", type=int, default=600)
    parser.add_argument("--overlap", type=int, default=150)
    parser.add_argument("--output", type=str, default="chunks.json")
    args = parser.parse_args()

    # 1. Load
    documents = load_documents("documents")

    # 2. Clean & Chunk
    all_chunks = build_chunks(documents, chunk_size=args.chunk_size, overlap=args.overlap)

    # 3. Inspect
    inspect_chunks(all_chunks)

    # 4. Save
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    print(f"\nSaved all chunks to '{args.output}'")


if __name__ == "__main__":
    main()
