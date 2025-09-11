#!/usr/bin/env python3
"""
Binary file hex sequence replacer with CP932 encoding support.
Converts ASCII characters to full-width and performs find/replace operations.
"""

import sys
import os
import argparse
import importlib.util
from typing import List, Tuple, Union

def ascii_to_fullwidth(text: str) -> str:
    """
    Convert ASCII characters to full-width equivalents.
    """
    result = ""
    for char in text:
        # Convert ASCII characters (0x21-0x7E) to full-width
        if 0x21 <= ord(char) <= 0x7E:
            # Full-width characters start at U+FF01 for '!' (0x21)
            fullwidth_char = chr(ord(char) - 0x21 + 0xFF01)
            result += fullwidth_char
        else:
            result += char
    return result

def text_to_cp932_hex(text: str) -> bytes:
    """
    Convert text to CP932 encoded bytes.
    """
    try:
        return text.encode('cp932')
    except UnicodeEncodeError as e:
        print(f"Error encoding text to CP932: {text}")
        print(f"Error details: {e}")
        raise

def hex_string_to_bytes(hex_string: str) -> bytes:
    """
    Convert hex string to bytes, handling both with and without spaces/formatting.
    """
    # Remove spaces, newlines, and other whitespace
    hex_clean = ''.join(hex_string.split())
    
    # Remove common prefixes if present
    if hex_clean.startswith('0x'):
        hex_clean = hex_clean[2:]
    
    # Ensure even length
    if len(hex_clean) % 2 != 0:
        hex_clean = '0' + hex_clean
    
    try:
        return bytes.fromhex(hex_clean)
    except ValueError as e:
        print(f"Error converting hex string to bytes: {hex_string}")
        print(f"Error details: {e}")
        raise

def is_ascii_text(text: str) -> bool:
    """
    Check if text contains only ASCII characters.
    """
    return all(ord(c) < 128 for c in text)

def is_hex_string(text: str) -> bool:
    """
    Check if text appears to be a hex string.
    """
    return (text.startswith(('0x', '\\x')) or 
            all(c in '0123456789abcdefABCDEF \t\n' for c in text))

def process_text_with_width_mode(text: str, width_mode: Union[bool, str], operation: str, is_find: bool) -> bytes:
    """
    Process text based on the width mode and operation type.
    
    Args:
        text: The text to process
        width_mode: True/False for both same width, "full_to_half"/"half_to_full" for different widths
        operation: "Find" or "Replace" for logging
        is_find: True if this is find text, False if replace text
    """
    use_fullwidth = False
    
    if isinstance(width_mode, bool):
        # Simple boolean mode - both find and replace use same width
        use_fullwidth = width_mode
    elif width_mode == "full_to_half":
        # Find uses full-width, replace uses half-width
        use_fullwidth = is_find  # True for find, False for replace
    elif width_mode == "half_to_full":
        # Find uses half-width, replace uses full-width
        use_fullwidth = not is_find  # False for find, True for replace
    
    if use_fullwidth:
        if is_ascii_text(text):
            # ASCII text: convert to full-width first
            fullwidth_text = ascii_to_fullwidth(text)
            result_bytes = text_to_cp932_hex(fullwidth_text)
            print(f"  {operation} (ASCII->fullwidth): '{text}' -> '{fullwidth_text}' -> {result_bytes.hex()}")
        else:
            # Japanese or other non-ASCII text: encode directly
            result_bytes = text_to_cp932_hex(text)
            print(f"  {operation} (Japanese): '{text}' -> {result_bytes.hex()}")
    else:
        # Keep half-width: encode text directly without full-width conversion
        result_bytes = text_to_cp932_hex(text)
        if is_ascii_text(text):
            print(f"  {operation} (ASCII half-width): '{text}' -> {result_bytes.hex()}")
        else:
            print(f"  {operation} (Japanese): '{text}' -> {result_bytes.hex()}")
    
    return result_bytes

def process_replacement_pairs(replacements: List[Tuple[str, str, Union[bool, str]]]) -> List[Tuple[bytes, bytes]]:
    """
    Process replacement pairs with flexible width control:
    - replacements: List of (find_text, replace_text, width_mode) tuples
    - width_mode options:
      - True: both find and replace use full-width
      - False: both find and replace use half-width
      - "full_to_half": find uses full-width, replace uses half-width
      - "half_to_full": find uses half-width, replace uses full-width
    """
    processed_pairs = []
    
    for find_text, replace_text, width_mode in replacements:
        print(f"Processing: '{find_text}' -> '{replace_text}' (mode: {width_mode})")
        
        # Process FIND text
        if is_hex_string(find_text):
            try:
                find_bytes = hex_string_to_bytes(find_text)
                print(f"  Find (hex): '{find_text}' -> {find_bytes.hex()}")
            except ValueError:
                find_bytes = process_text_with_width_mode(find_text, width_mode, "Find", is_find=True)
        else:
            find_bytes = process_text_with_width_mode(find_text, width_mode, "Find", is_find=True)
        
        # Process REPLACE text
        if is_hex_string(replace_text):
            try:
                replace_bytes = hex_string_to_bytes(replace_text)
                print(f"  Replace (hex): '{replace_text}' -> {replace_bytes.hex()}")
            except ValueError:
                replace_bytes = process_text_with_width_mode(replace_text, width_mode, "Replace", is_find=False)
        else:
            replace_bytes = process_text_with_width_mode(replace_text, width_mode, "Replace", is_find=False)
        
        processed_pairs.append((find_bytes, replace_bytes))
        print()
    
    return processed_pairs

def load_replacements_from_file(file_path: str) -> List[Tuple[str, str, Union[bool, str]]]:
    """
    Load replacement tuples from a Python file.
    Expected format: replacements = [("find", "replace", width_mode), ...]
    width_mode can be:
    - True: both find and replace use full-width
    - False: both find and replace use half-width  
    - "full_to_half": find uses full-width, replace uses half-width
    - "half_to_full": find uses half-width, replace uses full-width
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Replacements file not found: {file_path}")
    
    # Load the Python file as a module
    spec = importlib.util.spec_from_file_location("replacements_module", file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load Python file: {file_path}")
    
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Look for 'replacements' variable in the module
    if not hasattr(module, 'replacements'):
        raise ValueError(f"No 'replacements' variable found in {file_path}")
    
    replacements = module.replacements
    
    # Validate the format
    if not isinstance(replacements, list):
        raise ValueError("'replacements' must be a list")
    
    validated_replacements = []
    for i, item in enumerate(replacements):
        if not isinstance(item, tuple) or len(item) != 3:
            raise ValueError(f"Item {i} must be a tuple with 3 elements: (find, replace, width_mode)")
        
        find_text, replace_text, width_mode = item
        
        if not isinstance(find_text, str) or not isinstance(replace_text, str):
            raise ValueError(f"Item {i}: find and replace text must be strings")
        
        # Validate width_mode
        valid_modes = [True, False, "full_to_half", "half_to_full"]
        if width_mode not in valid_modes:
            raise ValueError(f"Item {i}: width_mode must be one of {valid_modes}")
        
        validated_replacements.append((find_text, replace_text, width_mode))
    
    print(f"Loaded {len(validated_replacements)} replacement(s) from {file_path}")
    return validated_replacements

def replace_in_binary(data: bytes, replacements: List[Tuple[bytes, bytes]]) -> bytes:
    """
    Perform find and replace operations on binary data.
    Only replaces the FIRST occurrence of each pattern.
    """
    result = data
    
    for find_bytes, replace_bytes in replacements:
        # Find the first occurrence
        index = result.find(find_bytes)
        if index != -1:
            # Replace only the first occurrence
            result = result[:index] + replace_bytes + result[index + len(find_bytes):]
            print(f"Replaced first occurrence of {find_bytes.hex()} with {replace_bytes.hex()} at position {index}")
        else:
            print(f"Pattern {find_bytes.hex()} not found in file")
    
    return result

def main():
    parser = argparse.ArgumentParser(description='Replace hex sequences in binary files with CP932 encoding support')
    parser.add_argument('input_file', help='Input binary file path')
    parser.add_argument('-o', '--output', help='Output file path (default: input_file.modified)')
    
    # Create mutually exclusive group for replacement input methods
    replacement_group = parser.add_mutually_exclusive_group(required=True)
    replacement_group.add_argument('-r', '--replacements', nargs=2, action='append', 
                                 metavar=('FIND', 'REPLACE'),
                                 help='Find and replace pair (can be used multiple times). Uses fullwidth by default.')
    replacement_group.add_argument('-f', '--file', help='Python file containing replacements list')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' does not exist.")
        sys.exit(1)
    
    # Set output file
    output_file = args.output or f"{args.input_file}.modified"
    
    try:
        # Load replacements
        if args.file:
            # Load from Python file
            replacements = load_replacements_from_file(args.file)
        else:
            # Convert command-line replacements to 3-tuple format (default to fullwidth=True)
            replacements = [(find, replace, True) for find, replace in args.replacements]
        
        # Read input file
        print(f"Reading binary file: {args.input_file}")
        with open(args.input_file, 'rb') as f:
            data = f.read()
        
        print(f"File size: {len(data)} bytes")
        print()
        
        # Process replacement pairs
        print("Processing replacement pairs:")
        processed_replacements = process_replacement_pairs(replacements)
        
        # Perform replacements
        print("Performing replacements...")
        modified_data = replace_in_binary(data, processed_replacements)
        
        # Write output file
        print(f"Writing modified data to: {output_file}")
        with open(output_file, 'wb') as f:
            f.write(modified_data)
        
        print(f"Operation completed successfully!")
        print(f"Original size: {len(data)} bytes")
        print(f"Modified size: {len(modified_data)} bytes")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

# Example usage as a module
def example_usage():
    """
    Example of how to use this script programmatically.
    """
    # Example replacement pairs with width control
    replacements = [
        # Japanese -> ASCII (full-width)
        ("こんにちは", "Hello", True),     # Japanese to full-width ASCII
        ("世界", "World", True),           # Japanese to full-width ASCII
        
        # ASCII -> ASCII (half-width for both find and replace)
        ("test", "TEST", False),           # Half-width ASCII to half-width ASCII
        ("123", "456", False),            # Half-width numbers to half-width numbers
        
        # Mixed scenarios
        ("データ", "DATA", True),          # Japanese to full-width ASCII
        ("Error", "エラー", False),       # Half-width ASCII to Japanese
        
        # Direct hex replacement (width flag ignored for hex)
        ("0xFF0A", "0x0D0A", False),      # Direct hex replacement
    ]
    
    # This would be used like:
    # processed = process_replacement_pairs(replacements)
    # modified_data = replace_in_binary(original_data, processed)

def create_example_replacements_file():
    """
    Create an example replacements.py file.
    """
    example_content = '''# Example replacements file
# Format: (find_text, replace_text, use_fullwidth)
# use_fullwidth: True = convert ASCII to full-width, False = keep half-width

replacements = [
    # Japanese to full-width ASCII
    ("こんにちは", "Hello", True),
    ("世界", "World", True),
    ("データ", "DATA", True),
    
    # Half-width ASCII operations
    ("test", "TEST", False),
    ("debug", "release", False),
    
    # Mixed cases
    ("エラー", "ERROR", True),  # Japanese to full-width ASCII
    ("OK", "完了", False),       # Half-width ASCII to Japanese
    
    # Hex replacements (width flag ignored)
    ("0xFF", "0x00", False),
]
'''
    
    with open('example_replacements.py', 'w', encoding='utf-8') as f:
        f.write(example_content)
    
    print("Created example_replacements.py")

if __name__ == "__main__":
    main()