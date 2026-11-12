#!/usr/bin/env python3
"""
Interactive Google Dork & Advanced Search Query Builder
Tampilan modern dengan dominant aksen Orange & Blue.
"""

import urllib.parse
import itertools
import webbrowser
import sys
import os

# --- PALET WARNA (ANSI 256 Color) ---
ORANGE_DARK  = "\033[38;5;202m"
ORANGE       = "\033[38;5;208m"
ORANGE_LIGHT = "\033[38;5;214m"
ORANGE_BOLD  = "\033[1;38;5;208m"

BLUE_DARK    = "\033[38;5;27m"
BLUE         = "\033[38;5;33m"
BLUE_CYAN    = "\033[38;5;39m"
BLUE_BOLD    = "\033[1;38;5;39m"

WHITE_BOLD   = "\033[1;97m"
GRAY         = "\033[38;5;244m"
LIGHT_GRAY   = "\033[38;5;252m"
GREEN        = "\033[38;5;82m"
RED          = "\033[38;5;196m"
RESET        = "\033[0m"

OPERATORS = {
    "1": ("site:", "Filter domain / subdomain spesifik (contoh: target.com, *.gov.id)"),
    "2": ("filetype:", "Ekstensi/tipe file (contoh: pdf, env, bak, sql, xlsx, txt)"),
    "3": ("inurl:", "Kata kunci di URL (contoh: admin, login, wp-content, api)"),
    "4": ("intitle:", "Kata kunci di judul dokumen/web (contoh: \"index of\", dashboard)"),
    "5": ("intext:", "Kata kunci di body konten teks (contoh: password, confidential)"),
    "6": ("ext:", "Sinonim filetype untuk search engine alternatif"),
    "7": ("cache:", "Melihat salinan cache Google dari suatu URL"),
    "8": ("related:", "Mencari situs yang mirip / berkaitan dengan domain"),
    "9": ("before:", "Hasil sebelum tanggal tertentu (format: YYYY-MM-DD)"),
    "10": ("after:", "Hasil sesudah tanggal tertentu (format: YYYY-MM-DD)"),
}

BANNER = f"""{ORANGE}
   ___             _        ___       _ _   _           
  |   \\ ___  _ _ | |__    | _ )_  _ (_) |__| |___ _ _  
  | |) / _ \\| '_|| / /    | _ \\ || || | / _` / -_) '_| 
  |___/\\___/|_|  |_\\_\\    |___/\\_,_||_|_\\__,_\\___|_|   
{RESET}{BLUE_BOLD}  :: GOOGLE DORK & RECONNAISSANCE QUERY BUILDER ::{RESET}
  {GRAY}Automated OSINT & Attack Surface Query Generator{RESET}
"""

def clean_input(prompt_text):
    try:
        return input(prompt_text).strip()
    except (KeyboardInterrupt, EOFError):
        print(f"\n\n{ORANGE}[!] {RED}Proses dibatalkan oleh user. Sampai jumpa!{RESET}\n")
        sys.exit(0)

def display_menu():
    print(f"\n{BLUE_CYAN}╭─────┬──────────────┬─────────────────────────────────────────────────────────────╮{RESET}")
    print(f"{BLUE_CYAN}│ {ORANGE_BOLD}NO{RESET}  {BLUE_CYAN}│ {ORANGE_BOLD}OPERATOR    {RESET} {BLUE_CYAN}│ {ORANGE_BOLD}DESKRIPSI & FUNGSI                                          {RESET}{BLUE_CYAN}│{RESET}")
    print(f"{BLUE_CYAN}├─────┼──────────────┼─────────────────────────────────────────────────────────────┤{RESET}")
    for key, (op, desc) in OPERATORS.items():
        k_str = f"{int(key):02d}"
        print(f"{BLUE_CYAN}│ {ORANGE_LIGHT}{k_str:<3}{RESET} {BLUE_CYAN}│ {BLUE_BOLD}{op:<12}{RESET} {BLUE_CYAN}│ {LIGHT_GRAY}{desc:<59}{RESET} {BLUE_CYAN}│{RESET}")
    print(f"{BLUE_CYAN}╰─────┴──────────────┴─────────────────────────────────────────────────────────────╯{RESET}")

def get_operator_choices():
    display_menu()
    print(f"\n{BLUE_CYAN}╭─[{ORANGE_BOLD} PILIH ATRIBUT {RESET}{BLUE_CYAN}]───────────────────────────────────────────────────────────╮{RESET}")
    print(f"{BLUE_CYAN}│{LIGHT_GRAY} Masukkan nomor atribut yang ingin dipakai (pisahkan dengan koma).         {BLUE_CYAN}│{RESET}")
    print(f"{BLUE_CYAN}│{GRAY} Contoh: {ORANGE_LIGHT}1,2,5{GRAY} atau {ORANGE_LIGHT}4,5{GRAY} atau {ORANGE_LIGHT}1{GRAY} atau ketik {ORANGE_BOLD}all{GRAY} untuk semua atribut.        {BLUE_CYAN}│{RESET}")
    print(f"{BLUE_CYAN}╰────────────────────────────────────────────────────────────────────────────╯{RESET}")
    
    while True:
        raw_choice = clean_input(f"{BLUE_CYAN}╭─[{ORANGE_BOLD}Pilih nomor{RESET}{BLUE_CYAN}]\n╰──❯ {ORANGE_LIGHT}")
        print(RESET, end="")
        if raw_choice.lower() == 'all':
            return list(OPERATORS.keys())
        
        selected = [x.strip() for x in raw_choice.split(',') if x.strip() in OPERATORS]
        if selected:
            seen = set()
            ordered = [x for x in selected if not (x in seen or seen.add(x))]
            return ordered
        else:
            print(f"{ORANGE}[!] {RED}Pilihan tidak valid.{LIGHT_GRAY} Contoh valid: {ORANGE_LIGHT}1,3,4{RESET}")

def collect_attribute_values(chosen_keys):
    collected = []
    print(f"\n{BLUE_BOLD}▼ MASUKKAN NILAI ATRIBUT:{RESET}")
    
    for key in chosen_keys:
        op_prefix, desc = OPERATORS[key]
        clean_desc = desc.split('(')[0].strip()
        print(f"{BLUE_CYAN}┌── {ORANGE_BOLD}{op_prefix}{RESET} {GRAY}({clean_desc}){RESET}")
        val = clean_input(f"{BLUE_CYAN}└──❯ {LIGHT_GRAY}")
        print(RESET, end="")
        if val:
            collected.append((op_prefix, val))
        else:
            print(f"    {GRAY}[dikosongkan - dilewati]{RESET}")
            
    print(f"\n{BLUE_CYAN}┌── {ORANGE_BOLD}Kata Kunci Bebas / Quote Tambahan{RESET} {GRAY}(opsional, tekan Enter jika tidak ada){RESET}")
    free_text = clean_input(f"{BLUE_CYAN}└──❯ {LIGHT_GRAY}")
    print(RESET, end="")
    if free_text:
        collected.append(("", free_text))
        
    return collected

def build_query_string(items):
    query_parts = []
    for prefix, val in items:
        if ' ' in val and not (val.startswith('"') and val.endswith('"')):
            val = f'"{val}"'
        if prefix:
            query_parts.append(f"{prefix}{val}")
        else:
            query_parts.append(val)
    return " ".join(query_parts)

def generate_combinations(collected_items):
    all_combos = []
    n = len(collected_items)
    for r in range(1, n + 1):
        for combo in itertools.combinations(collected_items, r):
            all_combos.append(combo)
    return all_combos

def main():
    os.system('clear' if os.name == 'posix' else 'cls')
    print(BANNER)
    
    chosen_keys = get_operator_choices()
    collected = collect_attribute_values(chosen_keys)
    
    if not collected:
        print(f"\n{ORANGE}[!] {RED}Tidak ada nilai atribut yang diisi. Program berhenti.{RESET}\n")
        return

    print(f"\n{BLUE_CYAN}╭───────────────────────── PILIH METODE HASIL DORK ─────────────────────────╮{RESET}")
    print(f"{BLUE_CYAN}│  {ORANGE_BOLD}[1]{RESET} {WHITE_BOLD}Query Tunggal{RESET}       {GRAY}-> Gabungkan semua atribut yang diisi          {BLUE_CYAN}│{RESET}")
    print(f"{BLUE_CYAN}│  {ORANGE_BOLD}[2]{RESET} {WHITE_BOLD}Segala Kombinasi{RESET}    {GRAY}-> Otomatis buat semua variasi (1 s/d N atribut) {BLUE_CYAN}│{RESET}")
    print(f"{BLUE_CYAN}╰────────────────────────────────────────────────────────────────────────────╯{RESET}")
    
    mode = clean_input(f"{BLUE_CYAN}╭─[{ORANGE_BOLD}Pilih mode 1 / 2{RESET}{BLUE_CYAN}] (Default: 1)\n╰──❯ {ORANGE_LIGHT}") or "1"
    print(RESET, end="")
    
    results = []
    if mode == "2":
        combos = generate_combinations(collected)
        for c in combos:
            results.append(build_query_string(c))
        print(f"\n{GREEN}[✓]{RESET} {WHITE_BOLD}Berhasil menghasilkan {ORANGE_BOLD}{len(results)}{RESET} {WHITE_BOLD}kombinasi dork:{RESET}")
    else:
        results.append(build_query_string(collected))
        print(f"\n{GREEN}[✓]{RESET} {WHITE_BOLD}Hasil Query Dork:{RESET}")

    for idx, query in enumerate(results, start=1):
        encoded = urllib.parse.quote_plus(query)
        url = f"https://www.google.com/search?q={encoded}"
        
        print(f"\n{BLUE_CYAN}╭─[{ORANGE_BOLD} #{idx} {RESET}{BLUE_CYAN}]" + "─"*65 + f"╮{RESET}")
        print(f"{BLUE_CYAN}│ {ORANGE}QUERY {RESET}: {WHITE_BOLD}{query}{RESET}")
        print(f"{BLUE_CYAN}│ {BLUE_BOLD}URL   {RESET}: {BLUE_CYAN}{url}{RESET}")
        print(f"{BLUE_CYAN}╰" + "─"*72 + f"╯{RESET}")

    # Simpan ke file
    print(f"\n{BLUE_CYAN}──────────────────────────────────────────────────────────────────────────────{RESET}")
    save_choice = clean_input(f"{BLUE_CYAN}Simpan hasil ke file teks? ({ORANGE_LIGHT}y/n{RESET}{BLUE_CYAN}, default: y) ❯ {ORANGE_LIGHT}").lower() or "y"
    print(RESET, end="")
    
    if save_choice == 'y':
        filename = clean_input(f"{BLUE_CYAN}Nama file ({GRAY}default: dork_results.txt{RESET}{BLUE_CYAN}) ❯ {ORANGE_LIGHT}") or "dork_results.txt"
        print(RESET, end="")
        with open(filename, "w", encoding="utf-8") as f:
            for idx, query in enumerate(results, start=1):
                encoded = urllib.parse.quote_plus(query)
                url = f"https://www.google.com/search?q={encoded}"
                f.write(f"[{idx}] Query: {query}\n    URL  : {url}\n\n")
        print(f"{GREEN}[✓]{RESET} Hasil berhasil disimpan di: {ORANGE_LIGHT}{os.path.abspath(filename)}{RESET}")

    # Buka di Browser
    open_browser = clean_input(f"\n{BLUE_CYAN}Buka query pertama di browser? ({ORANGE_LIGHT}y/n{RESET}{BLUE_CYAN}, default: n) ❯ {ORANGE_LIGHT}").lower() or "n"
    print(RESET, end="")
    if open_browser == 'y' and results:
        target_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(results[0])}"
        print(f"{BLUE_CYAN}[i] Membuka browser: {target_url}{RESET}")
        webbrowser.open(target_url)
    
    print(f"\n{ORANGE_BOLD}Selesai! Happy Hunting & Stay Safe!{RESET}\n")

if __name__ == "__main__":
    main()
