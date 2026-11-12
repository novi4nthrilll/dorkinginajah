#!/usr/bin/env python3
"""
Interactive Google Dork & Advanced Search Query Builder
Dibuat untuk kebutuhan OSINT, security auditing, dan advanced reconnaissance.
"""

import urllib.parse
import itertools
import webbrowser
import sys
import os

OPERATORS = {
    "1": ("site:", "Filter domain atau subdomain spesifik (contoh: example.com, *.gov.id)"),
    "2": ("filetype:", "Ekstensi/tipe file (contoh: pdf, env, bak, sql, xlsx, txt)"),
    "3": ("inurl:", "Kata kunci yang harus ada di dalam URL (contoh: admin, login, wp-content)"),
    "4": ("intitle:", "Kata kunci yang harus ada di judul halaman (contoh: \"index of\", dashboard)"),
    "5": ("intext:", "Kata kunci yang harus ada di body teks konten (contoh: password, confidential)"),
    "6": ("ext:", "Sinonim filetype untuk beberapa search engine (contoh: log, config)"),
    "7": ("cache:", "Melihat salinan cache Google dari suatu URL"),
    "8": ("related:", "Mencari situs yang mirip/berkaitan dengan domain tertentu"),
    "9": ("before:", "Hasil sebelum tanggal tertentu (contoh: 2023-01-01)"),
    "10": ("after:", "Hasil sesudah tanggal tertentu (contoh: 2022-01-01)"),
}

BANNER = """
=============================================================
           GOOGLE DORK & ADVANCED SEARCH BUILDER             
     Auditing & OSINT Reconnaissance Query Generator         
=============================================================
"""

def clean_input(prompt_text):
    try:
        return input(prompt_text).strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\nProses dibatalkan.")
        sys.exit(0)

def display_menu():
    print("\n[+] Atribut / Operator yang tersedia:")
    for key, (op, desc) in OPERATORS.items():
        print(f"  [{key}] {op:<12} -> {desc}")

def get_operator_choices():
    display_menu()
    print("\nMasukkan nomor atribut yang ingin kamu gunakan (pisahkan dengan koma).")
    print("Contoh: 1,2,5 atau 4,5 atau 'all' untuk semua atribut.")
    
    while True:
        raw_choice = clean_input("\nPilih atribut > ")
        if raw_choice.lower() == 'all':
            return list(OPERATORS.keys())
        
        selected = [x.strip() for x in raw_choice.split(',') if x.strip() in OPERATORS]
        if selected:
            # Urutkan dan hilangkan duplikat sambil mempertahankan urutan
            seen = set()
            ordered = [x for x in selected if not (x in seen or seen.add(x))]
            return ordered
        else:
            print("[!] Pilihan tidak valid. Silakan pilih nomor dari menu (contoh: 1,3,4).")

def collect_attribute_values(chosen_keys):
    collected = []
    print("\n[+] Masukkan nilai untuk setiap atribut yang dipilih:")
    for key in chosen_keys:
        op_prefix, desc = OPERATORS[key]
        val = clean_input(f"  {op_prefix} ({desc.split('(')[0].strip()}) > ")
        if val:
            # Format query: jika operator sudah mengandung titik dua, gabungkan
            collected.append((op_prefix, val))
        else:
            print(f"    [-] Dikosongkan (dilewati).")
            
    # Tambahan kata kunci bebas (opsional)
    free_text = clean_input("\nTambahan kata kunci bebas / quote khusus (opsional, tekan Enter jika tidak ada) > ")
    if free_text:
        collected.append(("", free_text))
        
    return collected

def build_query_string(items):
    query_parts = []
    for prefix, val in items:
        # Jika nilai memiliki spasi dan belum di-quote, bungkus dengan kutip
        if ' ' in val and not (val.startswith('"') and val.endswith('"')):
            val = f'"{val}"'
        if prefix:
            query_parts.append(f"{prefix}{val}")
        else:
            query_parts.append(val)
    return " ".join(query_parts)

def generate_combinations(collected_items):
    """
    Menghasilkan kombinasi dari atribut yang diinput (dari panjang 1 hingga N).
    """
    all_combos = []
    n = len(collected_items)
    for r in range(1, n + 1):
        for combo in itertools.combinations(collected_items, r):
            all_combos.append(combo)
    return all_combos

def main():
    print(BANNER)
    
    chosen_keys = get_operator_choices()
    collected = collect_attribute_values(chosen_keys)
    
    if not collected:
        print("\n[!] Tidak ada nilai atribut yang diisi. Keluar.")
        return

    print("\n" + "="*60)
    print("PILIH METODE HASIL DORK:")
    print("  [1] Query Tunggal (Gabungkan semua atribut yang diisi)")
    print("  [2] Otomatis Segala Kombinasi (Dari 1 atribut, 2 atribut, hingga kombinasi penuh)")
    print("="*60)
    
    mode = clean_input("Pilih mode [1 / 2] (Default: 1) > ") or "1"
    
    results = []
    if mode == "2":
        combos = generate_combinations(collected)
        for c in combos:
            q = build_query_string(c)
            results.append(q)
        print(f"\n[+] Berhasil menghasilkan {len(results)} kombinasi dork:")
    else:
        q = build_query_string(collected)
        results.append(q)
        print("\n[+] Hasil Query Dork:")

    for idx, query in enumerate(results, start=1):
        encoded = urllib.parse.quote_plus(query)
        url = f"https://www.google.com/search?q={encoded}"
        print(f"\n{idx}. Query : {query}")
        print(f"   URL   : {url}")

    # Opsi Simpan ke File atau Buka di Browser
    print("\n" + "-"*60)
    save_choice = clean_input("Simpan hasil ke file teks? (y/n, default: y) > ").lower() or "y"
    if save_choice == 'y':
        filename = clean_input("Nama file (default: dork_results.txt) > ") or "dork_results.txt"
        with open(filename, "w", encoding="utf-8") as f:
            for idx, query in enumerate(results, start=1):
                encoded = urllib.parse.quote_plus(query)
                url = f"https://www.google.com/search?q={encoded}"
                f.write(f"[{idx}] Query: {query}\n    URL  : {url}\n\n")
        print(f"[+] Hasil tersimpan di: {os.path.abspath(filename)}")

    open_browser = clean_input("\nBuka query pertama di browser sekarang? (y/n, default: n) > ").lower() or "n"
    if open_browser == 'y' and results:
        target_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(results[0])}"
        print(f"[+] Membuka {target_url} ...")
        webbrowser.open(target_url)

if __name__ == "__main__":
    main()

