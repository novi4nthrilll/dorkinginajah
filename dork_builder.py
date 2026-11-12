#!/usr/bin/env python3
"""
Interactive Google Dork & Advanced Search Query Builder
Didesain dengan Rich UI: Auto-responsive terminal width, warna dominan Orange & Blue.
"""

import sys
import os
import urllib.parse
import itertools
import webbrowser

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich import box
from rich.align import Align

console = Console()

# --- DEFINISI OPERATOR & DESKRIPSI ---
OPERATORS = {
    "1": ("site:", "Filter domain atau subdomain", "target.com, *.gov.id, *.ac.id"),
    "2": ("filetype:", "Ekstensi dokumen / file penting", "pdf, env, bak, sql, xlsx, txt"),
    "3": ("inurl:", "Kata kunci wajib di dalam URL", "admin, login, wp-content, api/v1"),
    "4": ("intitle:", "Kata kunci di judul dokumen / web", "\"index of\", dashboard, portal"),
    "5": ("intext:", "Kata kunci wajib di body teks", "password, confidential, api_key"),
    "6": ("ext:", "Sinonim filetype untuk search engine", "log, config, json, yml"),
    "7": ("cache:", "Melihat salinan snapshot cache Google", "https://example.com"),
    "8": ("related:", "Mencari situs yang mirip / relevan", "target.com"),
    "9": ("before:", "Hasil indeks sebelum tanggal tertentu", "2023-01-01"),
    "10": ("after:", "Hasil indeks sesudah tanggal tertentu", "2022-01-01"),
}

def render_banner():
    banner_text = Text()
    banner_text.append("⚡ GOOGLE DORK QUERY BUILDER ⚡\n", style="bold #FF8C00")
    banner_text.append("OSINT Reconnaissance & Attack Surface Auditor\n", style="bold #00D4FF")
    banner_text.append("Dirancang otomatis menyesuaikan ukuran layar terminal Anda.", style="dim italic #90CAF9")
    
    panel = Panel(
        Align.center(banner_text),
        box=box.ROUNDED,
        border_style="#0099FF",
        padding=(1, 2)
    )
    console.print(panel)

def display_operator_table():
    table = Table(
        box=box.ROUNDED,
        border_style="#0099FF",
        header_style="bold #FF8C00",
        expand=True
    )
    table.add_column("No", justify="center", style="bold #FFA726", width=4, no_wrap=True)
    table.add_column("Operator", style="bold #00D4FF", width=12, no_wrap=True)
    table.add_column("Fungsi & Kegunaan", style="white")
    table.add_column("Contoh Nilai", style="#90CAF9")

    for key, (op, desc, example) in OPERATORS.items():
        k_str = f"{int(key):02d}"
        table.add_row(k_str, op, desc, example)

    console.print(table)

def get_operator_choices():
    display_operator_table()
    
    info_panel = Panel(
        Text.from_markup(
            "[bold white]Ketik nomor atribut yang ingin digunakan[/bold white] (pisahkan koma).\n"
            "[dim]Contoh:[/] [bold #FFA726]1,2,5[/] atau [bold #FFA726]4,5[/] atau [bold #FFA726]1[/] "
            "atau ketik [bold #FF8C00]all[/] untuk memilih semua operator."
        ),
        box=box.ROUNDED,
        border_style="#FF8C00",
        title="[bold #FF8C00]Pilih Atribut[/bold #FF8C00]",
        title_align="left"
    )
    console.print(info_panel)
    
    while True:
        try:
            choice = Prompt.ask("[bold #00D4FF]❯ Masukkan pilihan[/bold #00D4FF]").strip()
        except (KeyboardInterrupt, EOFError):
            abort_program()
            
        if choice.lower() == 'all':
            return list(OPERATORS.keys())
        
        selected = [x.strip() for x in choice.split(',') if x.strip() in OPERATORS]
        if selected:
            # Hilangkan duplikat dan jaga urutan
            seen = set()
            ordered = [x for x in selected if not (x in seen or seen.add(x))]
            return ordered
        else:
            console.print("[bold #FF3333][!] Pilihan tidak valid.[/bold #FF3333] [dim]Silakan masukkan nomor dari tabel (contoh: 1,2,4).[/dim]")

def collect_attribute_values(chosen_keys):
    collected = []
    console.print("\n[bold #00D4FF]▼ Masukkan Nilai untuk Tiap Atribut:[/bold #00D4FF]")
    console.print("[dim white]Tekan Enter tanpa isi jika ingin mengosongkan/melewati atribut tersebut.[/dim white]\n")
    
    for key in chosen_keys:
        op_prefix, desc, example = OPERATORS[key]
        try:
            prompt_label = f"[bold #FF8C00]{op_prefix:<11}[/bold #FF8C00] [dim white]({desc})[/dim white]"
            val = Prompt.ask(prompt_label).strip()
        except (KeyboardInterrupt, EOFError):
            abort_program()
            
        if val:
            collected.append((op_prefix, val))
        else:
            console.print(f"            [dim #666666]↳ dilewati (kosong)[/dim #666666]")
            
    # Kata kunci bebas tambahan
    console.print()
    try:
        free_text = Prompt.ask("[bold #FFA726]Kata Kunci Bebas / Quote Tambahan[/bold #FFA726] [dim]('contoh: \"admin dashboard\"' / kosongkan)[/dim]").strip()
    except (KeyboardInterrupt, EOFError):
        abort_program()
        
    if free_text:
        collected.append(("", free_text))
        
    return collected

def build_query_string(items):
    query_parts = []
    for prefix, val in items:
        # Jika nilai ada spasi dan belum dibungkus kutip, tambahkan kutip ganda
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

def abort_program():
    console.print("\n\n[bold #FF8C00][!][/bold #FF8C00] [bold #FF3333]Proses dibatalkan oleh pengguna. Sampai jumpa![/bold #FF3333]\n")
    sys.exit(0)

def main():
    console.clear()
    render_banner()
    
    chosen_keys = get_operator_choices()
    collected = collect_attribute_values(chosen_keys)
    
    if not collected:
        console.print("\n[bold #FF3333][!] Tidak ada nilai atribut yang diisi. Program selesai.[/bold #FF3333]\n")
        return

    # Pemilihan mode
    mode_panel = Panel(
        Text.from_markup(
            "[bold #FF8C00][1] Query Tunggal[/bold #FF8C00]     : Gabungkan seluruh atribut yang diisi menjadi satu query utuh.\n"
            "[bold #00D4FF][2] Segala Kombinasi[/bold #00D4FF] : Otomatis buat semua variasi kombinasi (dari 1 atribut s/d lengkap)."
        ),
        box=box.ROUNDED,
        border_style="#0099FF",
        title="[bold #FF8C00]Pilih Mode Hasil Dork[/bold #FF8C00]",
        title_align="left"
    )
    console.print(mode_panel)
    
    try:
        mode = Prompt.ask("[bold #00D4FF]❯ Pilih mode [1/2][/bold #00D4FF]", choices=["1", "2"], default="1")
    except (KeyboardInterrupt, EOFError):
        abort_program()
    
    results = []
    if mode == "2":
        combos = generate_combinations(collected)
        for c in combos:
            results.append(build_query_string(c))
        console.print(f"\n[bold #00FF66]✓[/bold #00FF66] [bold white]Berhasil menghasilkan [bold #FF8C00]{len(results)}[/bold #FF8C00] kombinasi dork:[/bold white]\n")
    else:
        results.append(build_query_string(collected))
        console.print(f"\n[bold #00FF66]✓[/bold #00FF66] [bold white]Hasil Query Dork:[/bold white]\n")

    # Render Card Output
    for idx, query in enumerate(results, start=1):
        encoded = urllib.parse.quote_plus(query)
        url = f"https://www.google.com/search?q={encoded}"
        
        card_content = Text()
        card_content.append("QUERY : ", style="bold #FF8C00")
        card_content.append(f"{query}\n", style="bold white")
        card_content.append("URL   : ", style="bold #00D4FF")
        card_content.append(f"{url}", style="underline #00D4FF")
        
        console.print(
            Panel(
                card_content,
                box=box.ROUNDED,
                border_style="#0099FF",
                title=f"[bold #FF8C00]#{idx:02d}[/bold #FF8C00]",
                title_align="left"
            )
        )

    # Simpan ke file teks
    console.print()
    try:
        save_file = Confirm.ask("[bold #00D4FF]Simpan semua hasil ke file teks?[/bold #00D4FF]", default=True)
    except (KeyboardInterrupt, EOFError):
        abort_program()
        
    if save_file:
        try:
            filename = Prompt.ask("[bold #FF8C00]Nama file[/bold #FF8C00]", default="dork_results.txt").strip()
        except (KeyboardInterrupt, EOFError):
            abort_program()
            
        with open(filename, "w", encoding="utf-8") as f:
            for idx, query in enumerate(results, start=1):
                encoded = urllib.parse.quote_plus(query)
                url = f"https://www.google.com/search?q={encoded}"
                f.write(f"[{idx:02d}] Query: {query}\n     URL  : {url}\n\n")
        console.print(f"[bold #00FF66]✓[/bold #00FF66] [dim white]Hasil disimpan di:[/dim white] [bold #FF8C00]{os.path.abspath(filename)}[/bold #FF8C00]\n")

    # Buka di browser
    try:
        open_web = Confirm.ask("[bold #00D4FF]Buka query pertama di web browser sekarang?[/bold #00D4FF]", default=False)
    except (KeyboardInterrupt, EOFError):
        abort_program()
        
    if open_web and results:
        target_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(results[0])}"
        console.print(f"[dim #00D4FF]Membuka browser...[/dim #00D4FF]")
        webbrowser.open(target_url)

    console.print(Panel(Align.center("[bold #FF8C00]Selesai! Gunakan dork ini dengan bijak & etis. 🚀[/bold #FF8C00]"), box=box.ROUNDED, border_style="#0099FF"))

if __name__ == "__main__":
    main()
