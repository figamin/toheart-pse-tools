import os

INPUT_DIR = "scn_asm_half"
OUTPUT_DIR = "scn_asm_full"


def to_fullwidth(char):
    code = ord(char)

    # Space → full-width space
    if code == 0x20:
        return '\u3000'

    # ASCII printable characters
    if 0x21 <= code <= 0x7E:
        return chr(code + 0xFEE0)

    return char


def convert_text(text):
    result = []
    inside_tag = False

    for char in text:
        if char == '<':
            inside_tag = True
            result.append(char)
            continue
        elif char == '>':
            inside_tag = False
            result.append(char)
            continue

        if inside_tag:
            result.append(char)
        else:
            result.append(to_fullwidth(char))

    return ''.join(result)


def process_files():
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for root, _, files in os.walk(INPUT_DIR):
        for filename in files:
            input_path = os.path.join(root, filename)

            # Preserve folder structure
            relative_path = os.path.relpath(input_path, INPUT_DIR)
            output_path = os.path.join(OUTPUT_DIR, relative_path)

            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            try:
                with open(input_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                converted = convert_text(content)

                # Overwrite output file if it exists
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(converted)

                print(f"Processed: {relative_path}")

            except Exception as e:
                print(f"Skipped {relative_path}: {e}")


if __name__ == "__main__":
    process_files()

