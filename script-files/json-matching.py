import json
import os
import re

# ==== CONFIG ====
JSON_FILE = "text.json"
INPUT_FOLDER = "scn_asm_auto_replace"
OUTPUT_FOLDER = "scn_asm_auto_replace_en_2"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ==== NORMALIZATION ====

def normalize(text):
    text = text.strip()

    text = re.sub(r'[「」『』（）【】]', '', text)
    text = text.replace("バカ", "馬鹿")

    text = re.sub(r'[。、．，,!?！？…\s　]', '', text)

    return text


# ==== SIMILARITY ====

def similarity(a, b):
    """Simple similarity score"""
    if not a or not b:
        return 0

    # exact match = best
    if a == b:
        return 1.0

    # partial overlap
    shorter = min(len(a), len(b))
    matches = sum(1 for i in range(shorter) if a[i] == b[i])

    return matches / max(len(a), len(b))


# ==== LOAD JSON ====

with open(JSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

entries = []

for entry in data:
    jp = entry.get("jaJP")
    en = entry.get("enUS")

    if not jp or not en:
        continue

    jp_lines = jp.split("\n")

    entries.append({
        "jp_norm": normalize("".join(jp_lines)),
        "en_lines": en.split("\n"),
        "used": False
    })


# ==== SORT FILES ====
filenames = sorted(os.listdir(INPUT_FOLDER))


# ==== PROCESS ====

for filename in filenames:
    if not filename.endswith(".txt"):
        continue

    input_path = os.path.join(INPUT_FOLDER, filename)
    output_path = os.path.join(OUTPUT_FOLDER, filename)

    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    i = 0
    new_lines = []

    while i < len(lines):
        best_match = None
        best_score = 0
        best_size = 0
        best_entry = None

        # Try chunk sizes
        for size in range(1, 6):
            if i + size > len(lines):
                continue

            block = lines[i:i+size]
            joined = "".join(block)
            norm_block = normalize(joined)

            for entry in entries:
                if entry["used"]:
                    continue

                score = similarity(norm_block, entry["jp_norm"])

                if score > best_score:
                    best_score = score
                    best_match = block
                    best_size = size
                    best_entry = entry

        # Threshold to avoid bad matches
        if best_score > 0.85:
            block = best_match

            starts_with_quote = block[0].strip().startswith(("「", "『", '"'))
            ends_with_quote = block[-1].strip().endswith(("」", "』", '"'))

            en_lines = best_entry["en_lines"][:]

            if starts_with_quote:
                en_lines[0] = '"' + en_lines[0]
            if ends_with_quote:
                en_lines[-1] = en_lines[-1] + '"'

            for line in en_lines:
                new_lines.append(line + "\n")

            best_entry["used"] = True
            i += best_size
        else:
            new_lines.append(lines[i])
            i += 1

    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

print("Done!")