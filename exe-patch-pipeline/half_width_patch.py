import sys, struct, mmap, os

EXE_PATH = sys.argv[1] if len(sys.argv) > 1 else "game.exe"

# Constants (RVA/VA for a PE with ImageBase 0x400000)
IMAGE_BASE    = 0x400000
HOOK_ADDR     = 0x00414790                 # start of: mov edi,[ebp+14] ; cmp edi,0x80
HOOK_LEN      = 9                          # 3 (mov) + 6 (cmp)
BACK_ADDR     = HOOK_ADDR + HOOK_LEN       # resume at 0x00414799

def read_u32(b, off):  return struct.unpack_from("<I", b, off)[0]
def write_u32(mm, off, val): mm[off:off+4] = struct.pack("<I", val)

def load_sections(mm):
    # DOS
    if mm[0:2] != b"MZ":
        raise RuntimeError("Not a PE/MZ file")
    pe_off = read_u32(mm, 0x3C)
    if mm[pe_off:pe_off+4] != b"PE\x00\x00":
        raise RuntimeError("Bad PE header")
    num_sections = struct.unpack_from("<H", mm, pe_off+6)[0]
    opt_hdr_size = struct.unpack_from("<H", mm, pe_off+20)[0]
    opt_hdr_off  = pe_off + 24
    # ImageBase from Optional Header
    img_base = read_u32(mm, opt_hdr_off+28)  # should be 0x400000
    sect_off = opt_hdr_off + opt_hdr_size

    sections = []
    for i in range(num_sections):
        off = sect_off + 40*i
        name = mm[off:off+8].rstrip(b"\x00").decode("ascii", errors="ignore")
        VirtualSize        = read_u32(mm, off+8)
        VirtualAddress     = read_u32(mm, off+12)
        SizeOfRawData      = read_u32(mm, off+16)
        PointerToRawData   = read_u32(mm, off+20)
        sections.append({
            "name": name,
            "va":   IMAGE_BASE + VirtualAddress,
            "rva":  VirtualAddress,
            "vsize":VirtualSize,
            "rawsize": SizeOfRawData,
            "rawptr": PointerToRawData
        })
    return sections

def rva_to_file_offset(rva, sections):
    for s in sections:
        start = s["rva"]
        end   = s["rva"] + s["rawsize"]  # restrict to data backed by file
        if start <= rva < end:
            return s["rawptr"] + (rva - start)
    raise ValueError(f"RVA {hex(rva)} not in any section")

def find_text_section(sections):
    for s in sections:
        if s["name"] == ".text":
            return s
    raise RuntimeError("No .text section found")

def find_cave(mm, sect, min_size, scan_back=0x2000):
    """
    Find a run of 0x00 bytes near the end of .text large enough to hold min_size.
    Scans the last `scan_back` bytes (or entire section if smaller).
    Returns (cave_va, cave_rva, cave_file_off).
    """
    raw_start = sect["rawptr"]
    raw_end   = raw_start + sect["rawsize"]
    window_start = max(raw_start, raw_end - scan_back)
    window = mm[window_start:raw_end]

    need = min_size
    run_len = 0
    run_end = len(window)

    # Search from the end backwards for a contiguous zero run
    i = len(window) - 1
    best_start = None
    best_len = 0
    while i >= 0:
        if window[i] == 0:
            j = i
            while j >= 0 and window[j] == 0:
                j -= 1
            # run is (j+1 .. i)
            run_start = j + 1
            run_len = i - j
            if run_len >= need:
                best_start = run_start
                best_len = run_len
                break
            i = j
        else:
            i -= 1

    if best_start is None:
        raise RuntimeError("No suitable code cave found in .text")

    cave_file_off = window_start + best_start
    cave_rva      = (cave_file_off - sect["rawptr"]) + sect["rva"]
    cave_va       = IMAGE_BASE + cave_rva
    return cave_va, cave_rva, cave_file_off

def build_cave_code(cave_va):
    """
    Hand-assembled logic:
      mov  edi,[ebp+14]
      if ((edi & 0xFF00) == 0x8200) {
          low = edi & 0xFF
          if (0x4F<=low<=0x58) ascii = low-0x1F;        // digits
          else if (0x60<=low<=0x79) ascii = low-0x1F;   // A..Z
          else if (0x81<=low<=0x9A) ascii = low-0x20;   // a..z
          if (mapped) { edi=ascii; [ebp+14]=edi; }
      }
      cmp  edi,0x80
      jmp  BACK_ADDR
    """
    code  = bytearray()

    code += b"\x8B\x7D\x18"                   # 00: mov edi,[ebp+14]
    code += b"\x8B\xC7"                       # 03: mov eax,edi
    code += b"\x25\x00\xFF\x00\x00"           # 05: and eax,0x0000FF00
    code += b"\x3D\x00\x82\x00\x00"           # 0A: cmp eax,0x00008200
    code += b"\x75\x37"                       # 0F: jnz skip  (+0x37 -> to pos 0x48 / 72)

    code += b"\x8B\xC7"                       # 11: mov eax,edi
    code += b"\x25\xFF\x00\x00\x00"           # 13: and eax,0xFF
    code += b"\x83\xF8\x4F"                   # 18: cmp eax,0x4F
    code += b"\x72\x0A"                       # 1B: jb  check_upper (to 0x27 -> pos 39)
    code += b"\x83\xF8\x58"                   # 1D: cmp eax,0x58
    code += b"\x77\x05"                       # 20: ja  check_upper (to 0x27 -> pos 39)
    code += b"\x83\xE8\x1F"                   # 22: sub eax,0x1F  (digits)
    code += b"\xEB\x1C"                       # 25: jmp store     (to 0x3D -> pos 67)

    # check_upper:
    code += b"\x83\xF8\x60"                   # 27: cmp eax,0x60
    code += b"\x72\x0A"                       # 2A: jb  check_lower (to 0x36 -> pos 54)
    code += b"\x83\xF8\x9A"                   # 2C: cmp eax,0x79
    code += b"\x77\x05"                       # 2F: ja  check_lower (to 0x36 -> pos 54)
    code += b"\x83\xE8\x20"                   # 31: sub eax,0x1F   (A..Z)
    code += b"\xEB\x0D"                       # 34: jmp store      (to 0x3D -> pos 67)

    # check_lower:
    code += b"\x83\xF8\x81"                   # 36: cmp eax,0x81
    code += b"\x72\x0D"                       # 39: jb  skip       (to 0x48 -> pos 72)
    code += b"\x83\xF8\x9A"                   # 3B: cmp eax,0x9A
    code += b"\x77\x08"                       # 3E: ja  skip       (to 0x48 -> pos 72)
    code += b"\x83\xE8\x20"                   # 40: sub eax,0x20   (a..z)

    # store:
    code += b"\x89\xC7"                       # 43: mov edi,eax
    code += b"\x89\x7D\x18"                   # 45: mov [ebp+14],edi

    # skip:
    code += b"\x81\xFF\x80\x00\x00\x00"       # 48: cmp edi,0x80
    code += b"\xE9\x00\x00\x00\x00"           # 4E: jmp back  (fill later)

    # sanity
    assert len(code) == 83, len(code)

    # patch the final back jump
    cave_rva = cave_va - IMAGE_BASE
    jmp_off_in_code = 0x4F  # where the rel32 starts (at E9's +1)
    rel = (BACK_ADDR - (cave_va + jmp_off_in_code + 4)) & 0xFFFFFFFF
    struct.pack_into("<I", code, jmp_off_in_code, rel)

    return bytes(code)

def patch_game():
    with open(EXE_PATH, "r+b") as f, mmap.mmap(f.fileno(), 0) as mm:
        print("[+] Loaded sections:", [s["name"] for s in load_sections(mm)])
        sects = load_sections(mm)
        text  = find_text_section(sects)

        # Build cave code first to know how large a hole we need
        dummy_va  = text["va"]  # temp just to get size; we'll re-build with real VA
        tmp_code  = build_cave_code(dummy_va)  # size stable regardless of VA except back jmp
        need_size = len(tmp_code) + 16         # headroom

        cave_va, cave_rva, cave_off = find_cave(mm, text, need_size)
        # rebuild cave with correct VA (for accurate back jump)
        cave_code = build_cave_code(cave_va)

        print(f"[+] Using cave at VA {hex(cave_va)}, file offset {hex(cave_off)} (size {len(cave_code)} bytes)")

        # Write cave
        mm[cave_off:cave_off+len(cave_code)] = cave_code

        # Install hook at 0x00414790 (write 5-byte JMP rel32 + NOPs to cover 9 bytes)
        hook_rva = HOOK_ADDR - IMAGE_BASE
        hook_off = rva_to_file_offset(hook_rva, sects)

        rel = (cave_va - (HOOK_ADDR + 5)) & 0xFFFFFFFF
        mm[hook_off:hook_off+5] = b"\xE9" + struct.pack("<I", rel)
        # pad remaining 4 bytes (we overwrote 9 bytes total)
        mm[hook_off+5:hook_off+HOOK_LEN] = b"\x90" * (HOOK_LEN - 5)

        mm.flush()

        # Quick verification
        ok_hook = mm[hook_off] == 0xE9
        ok_cave = mm[cave_off:cave_off+2] == b"\x8B\x7D" and mm[cave_off+0x48:cave_off+0x4E] == b"\x81\xFF\x80\x00\x00\x00"
        if ok_hook and ok_cave:
            print("[+] Patch applied successfully (hook + cave present).")
        else:
            print("[!] Patch write did not verify cleanly.")

if __name__ == "__main__":
    if not os.path.exists(EXE_PATH):
        print(f"Usage: {os.path.basename(sys.argv[0])} <path_to_game.exe>")
        sys.exit(1)
    patch_game()
