import sys
import os
import shutil
import importlib.util
from typing import List, Tuple

def to_fullwidth(text: str) -> str:
    """Convert text to fullwidth characters with lowercase letter shift"""
    result = []
    for ch in text:
        code = ord(ch)
        if ch == " ":
            result.append("　")
        elif ch == "'":
            result.append("")
        elif ch == '"':
            result.append('')
        #elif code == 0x61:  # lowercase 'a' - special case
        #    shifted_code = code - 3
        #    result.append(chr(shifted_code + 0xFEE0))
        elif 0x41 <= code <= 0x5A:  # lowercase letters b-z
            # Shift lowercase letters one position back (b -> a, c -> b, etc.)
            shifted_code = code + 1
            result.append(chr(shifted_code + 0xFEE0))
        elif 0x21 <= code <= 0x7E:  # other printable ASCII
            result.append(chr(code + 0xFEE0))
        else:
            result.append(ch)
    return "".join(result)

def text_to_hex(text: str) -> str:
    """Convert text to hex format (same process as original function)"""
    fullwidth = to_fullwidth(text)
    encoded = fullwidth.encode("cp932", errors="strict")
    
    hex_pairs = []
    for b in encoded:
        hex_pairs.append(f"{b:02X}")
    
    reversed_pairs = []
    for i in range(0, len(hex_pairs), 2):
        if i + 1 < len(hex_pairs):
            reversed_pairs.append(hex_pairs[i+1] + hex_pairs[i])
        else:
            reversed_pairs.append(hex_pairs[i])
    
    return "".join(reversed_pairs)

def hex_to_bytes(hex_string: str) -> bytes:
    """Convert hex string to bytes"""
    return bytes.fromhex(hex_string)

def load_translation_array(py_file_path: str) -> List[Tuple[str, str]]:
    """Load the translation array from a Python file"""
    spec = importlib.util.spec_from_file_location("translations", py_file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Look specifically for text_array
    if hasattr(module, 'text_array'):
        attr = getattr(module, 'text_array')
        if isinstance(attr, list):
            return attr
    
    raise ValueError(f"No 'text_array' found in {py_file_path}")

def process_dat_file(dat_file_path: str, translations: List[Tuple[str, str]], output_path: str):
    """Process a single DAT file with its translations"""
    # Read the DAT file as binary
    with open(dat_file_path, 'rb') as f:
        dat_data = f.read()
    
    print(f"Processing {os.path.basename(dat_file_path)}...")
    print(f"Original file size: {len(dat_data)} bytes")
    
    # Hiroyuki (text box 1) replacement
    target_hexes = ["5704000058040000590400005a0400005b0400005c040000",
                    # A different Hiroyuki replacement
                  "4D0400004E0400004F040000500400005104000052040000",
                  # Left quote and long dash
                  "7581a286a286",
                  # accents
                  "0400005181",
                  # あかりは、近所に住んでる同い年の幼なじみ。
                  "A082A982E882CD824181DF8B8A8FC9825A8FF182C582E982AF93A2824E94CC826397C882B682DD8242810A"
                  ]
    #f003010000001e00 - slow elipsis?
    
    # Remove all instances of target hex sequences
    total_instances = 0
    for target_hex in target_hexes:
        target_bytes = hex_to_bytes(target_hex)
        instances_found = dat_data.count(target_bytes)
        if instances_found > 0:
            print(f"  Found {instances_found} instances of hex sequence '{target_hex}' - removing them")
            dat_data = dat_data.replace(target_bytes, b'')
            total_instances += instances_found
    
    if total_instances > 0:
        print(f"  File size after removing {total_instances} hex sequences: {len(dat_data)} bytes")
    
    replacements_made = 0
    
    # Process each translation tuple
    for japanese_text, english_text in translations:
        if not japanese_text:
            continue
        
        # Skip if English text is blank/empty
        if not english_text or english_text.strip() == "":
            continue
            
        try:
            # Convert Japanese text to hex bytes
            japanese_hex = text_to_hex(japanese_text)
            japanese_bytes = hex_to_bytes(japanese_hex)
            
            # Convert English text to hex bytes
            english_hex = text_to_hex(english_text)
            english_bytes = hex_to_bytes(english_hex)
            
            # Find and replace Japanese bytes with English bytes
            if japanese_bytes in dat_data:
                print(f"  Found: '{japanese_text[:50]}...' -> '{english_text[:50]}...'")
                dat_data = dat_data.replace(japanese_bytes, english_bytes)
                replacements_made += 1
                
        except Exception as e:
            print(f"  Error processing translation '{japanese_text[:30]}...': {e}")
            continue
    
    # Write the modified DAT file
    with open(output_path, 'wb') as f:
        f.write(dat_data)
    
    print(f"  Replacements made: {replacements_made}")
    print(f"  New file size: {len(dat_data)} bytes")
    print(f"  Saved to: {output_path}")
    print()

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 script.py <dat_folder> <py_folder> <output_folder>")
        print("  dat_folder: Folder containing .DAT files")
        print("  py_folder: Folder containing .py files with translation arrays")
        print("  output_folder: Folder to save modified .DAT files")
        sys.exit(1)
    
    dat_folder = sys.argv[1]
    py_folder = sys.argv[2]
    output_folder = sys.argv[3]
    
    # Validate input folders
    if not os.path.isdir(dat_folder):
        print(f"Error: DAT folder '{dat_folder}' does not exist")
        sys.exit(1)
    
    if not os.path.isdir(py_folder):
        print(f"Error: Python folder '{py_folder}' does not exist")
        sys.exit(1)
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Get all DAT files
    dat_files = [f for f in os.listdir(dat_folder) if f.lower().endswith('.dat')]
    
    if not dat_files:
        print(f"No .DAT files found in '{dat_folder}'")
        sys.exit(1)
    
    print(f"Found {len(dat_files)} DAT files to process")
    print()
    
    processed_files = 0
    
    # Process each DAT file
    for dat_file in dat_files:
        base_name = os.path.splitext(dat_file)[0]
        py_file = base_name + '.py'
        
        dat_path = os.path.join(dat_folder, dat_file)
        py_path = os.path.join(py_folder, py_file)
        output_path = os.path.join(output_folder, dat_file)
        
        # Check if corresponding Python file exists
        if not os.path.exists(py_path):
            print(f"Warning: No corresponding Python file found for '{dat_file}' (looking for '{py_file}')")
            continue
        
        try:
            # Load translation array
            translations = load_translation_array(py_path)
            
            # If array is empty, just copy the original DAT file
            if not translations:
                print(f"Empty translation array in {py_file}, copying original DAT file...")
                shutil.copy2(dat_path, output_path)
                print(f"  Copied to: {output_path}")
                print()
                processed_files += 1
                continue
            
            print(f"Loaded {len(translations)} translations from {py_file}")
            
            # Process the DAT file
            process_dat_file(dat_path, translations, output_path)
            processed_files += 1
            
        except Exception as e:
            print(f"Error processing {dat_file}: {e}")
            print()
            continue
    
    print(f"Processing complete! Successfully processed {processed_files} files.")

if __name__ == "__main__":
    main()