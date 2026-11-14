#!/usr/bin/env python3
"""
Interactive Google Dork & Advanced Search Query Builder
Didesain dengan Rich UI: Auto-responsive terminal width, warna dominan Orange & Blue.
Dilengkapi Buku Panduan & Cheatsheet Google Dorking manual.
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
from rich.rule import Rule

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

GUIDE_OPTION_KEY = "11"

def render_banner():
    banner_text = Text()
    banner_text.append("⚡ GOOGLE DORK QUERY BUILDER ⚡\n", style="bold #FF8C00")
    banner_text.append("OSINT Reconnaissance & Attack Surface Auditor\n", style="bold #00D4FF")
    banner_text.append("Dirancang otomatis menyesuaikan ukuran layar terminal Anda.", style="dim italic #90CAF9")
    
    panel = Panel(
        Align.center(banner_text),
        box=box.ROUNDED,
        border_style="#0099FF",
        padding=(0, 1)
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
    table.add_column("Operator", style="bold #00D4FF", width=14, no_wrap=True)
    table.add_column("Fungsi & Kegunaan", style="white")
    table.add_column("Contoh Nilai", style="#90CAF9")

    for key, (op, desc, example) in OPERATORS.items():
        k_str = f"{int(key):02d}"
        table.add_row(k_str, op, desc, example)

    # Opsi Paling Akhir: Buku Panduan / Guidebook
    table.add_section()
    table.add_row(
        GUIDE_OPTION_KEY,
        "📖 PANDUAN",
        "[bold #FF8C00]Buku Panduan & Cheatsheet Google Dorking (Manual Guide)[/bold #FF8C00]",
        "[italic #FFA726]Pilih opsi 11 untuk melihat panduan[/italic #FFA726]"
    )

    console.print(table)

def display_guidebook():
    """
    Menampilkan buku panduan komprehensif, cheatsheet, dan contoh nyata penggunaan Google Dork.
    """
    console.print(Rule(title="[bold #FF8C00]📖 BUKU PANDUAN LENGKAP GOOGLE DORKING (CHEATSHEET)[/bold #FF8C00]", style="#0099FF"))
    
    intro_panel = Panel(
        Text.from_markup(
            "[bold white]Google Dorking[/bold white] (dikenal juga sebagai [bold #00D4FF]Google Hacking / Advanced Search[/bold #00D4FF]) "
            "adalah teknik pencarian menggunakan operator khusus untuk mengungkap informasi sensitif, file tersembunyi, "
            "panel login, maupun kesalahan konfigurasi yang tidak sengaja terindeks oleh mesin pencari Google.\n\n"
            "[bold #FF8C00]⚠️ Aturan Sintaks Penting:[/] Antara operator dan nilai [bold red]TIDAK BOLEH[/bold red] ada spasi. "
            "Contoh benar: [bold #00D4FF]site:target.com[/bold #00D4FF] (bukan [dim]site: target.com[/dim])."
        ),
        box=box.ROUNDED,
        border_style="#FF8C00",
        title="[bold #FF8C00]1. Konsep Dasar & Sintaks[/bold #FF8C00]",
        title_align="left"
    )
    console.print(intro_panel)

    # 1. Penjelasan Atribut
    attr_table = Table(
        title="[bold #00D4FF]2. Penjelasan Mendalam Setiap Atribut & Contohnya[/bold #00D4FF]",
        box=box.ROUNDED,
        border_style="#0099FF",
        header_style="bold #FF8C00",
        expand=True
    )
    attr_table.add_column("Operator", style="bold #00D4FF", width=12, no_wrap=True)
    attr_table.add_column("Cara Kerja & Trik Penggunaan", style="white")
    attr_table.add_column("Contoh Nyata", style="#FFA726")

    attr_table.add_row(
        "site:",
        "Membatasi pencarian hanya pada domain atau TLD spesifik. Bisa gunakan wildcard (*) atau minus (-) untuk exclude.",
        "site:target.com\nsite:*.target.com -site:www.target.com\nsite:gov.id"
    )
    attr_table.add_row(
        "filetype: / ext:",
        "Menyaring dokumen berdasarkan ekstensi file. Sangat ampuh untuk audit dokumen publik atau file konfigurasi.",
        "site:target.com filetype:pdf\nsite:target.com (ext:sql OR ext:env OR ext:bak)"
    )
    attr_table.add_row(
        "inurl:",
        "Memaksa Google mencari kata tertentu di dalam string URL / path halaman.",
        "site:target.com inurl:admin\ninurl:wp-login.php\ninurl:api/v1"
    )
    attr_table.add_row(
        "intitle:",
        "Mengharuskan kata kunci berada pada tag <title> dokumen / halaman web.",
        "intitle:\"index of /\"\nsite:target.com intitle:\"dashboard\"\nintitle:\"login portal\""
    )
    attr_table.add_row(
        "intext:",
        "Mencari kata kunci spesifik di seluruh body teks konten halaman.",
        "site:target.com intext:\"confidential\"\nintext:\"DB_PASSWORD\" filetype:env"
    )
    attr_table.add_row(
        "cache:",
        "Menampilkan snapshot salinan web yang tersimpan di server Google (berguna jika web target sedang down / diedit).",
        "cache:https://target.com/private-doc"
    )
    attr_table.add_row(
        "related:",
        "Menemukan website lain yang memiliki keterkaitan topik atau struktur dengan domain sasaran.",
        "related:target.com"
    )
    attr_table.add_row(
        "before: / after:",
        "Memfilter hasil indeks berdasarkan kurun waktu (format tanggal: YYYY-MM-DD). Bagus untuk investigasi insiden.",
        "site:target.com after:2024-01-01 before:2024-12-31"
    )
    console.print(attr_table)

    # 2. Resep Dorking Populer
    recipe_panel = Panel(
        Text.from_markup(
            "[bold #FF8C00]📂 1. Open Directory (Folder Server Terbuka):[/]\n"
            "   [bold white]site:target.com intitle:\"index of /\" \"parent directory\"[/bold white]\n"
            "   [dim white]→ Menemukan folder server web yang indexing-nya terbuka tanpa index.html.[/dim white]\n\n"

            "[bold #FF8C00]🔐 2. Panel Login & Area Administrasi Tersembunyi:[/] \n"
            "   [bold white]site:target.com (inurl:admin OR inurl:login OR inurl:cpanel OR inurl:portal) intitle:login[/bold white]\n"
            "   [dim white]→ Mendeteksi endpoint autentikasi pengelola sistem yang terindeks publik.[/dim white]\n\n"

            "[bold #FF8C00]🗄️ 3. File Backup & Database Dump Bocor:[/] \n"
            "   [bold white]site:target.com (ext:sql OR ext:bak OR ext:dump OR ext:old OR ext:tar.gz)[/bold white]\n"
            "   [dim white]→ Menemukan backup database atau arsip server yang tertinggal di webroot.[/dim white]\n\n"

            "[bold #FF8C00]⚙️ 4. File Konfigurasi & Environment:[/] \n"
            "   [bold white]site:target.com (ext:env OR ext:conf OR ext:ini OR ext:yml) intext:\"DB_HOST\"[/bold white]\n"
            "   [dim white]→ Memeriksa apakah file kredensial aplikasi (.env / config) dapat diakses bebas.[/dim white]\n\n"

            "[bold #FF8C00]📄 5. Dokumen Internal & Rahasia Perusahaan:[/] \n"
            "   [bold white]site:target.com filetype:pdf (intext:\"confidential\" OR intext:\"internal use only\")[/bold white]\n"
            "   [dim white]→ Mengaudit dokumen PDF internal yang tidak sengaja dipublikasikan.[/dim white]\n\n"

            "[bold #FF8C00]🪵 6. Log Server & Debug Information:[/] \n"
            "   [bold white]site:target.com (ext:log OR inurl:logs) (intext:\"error\" OR intext:\"exception\")[/bold white]\n"
            "   [dim white]→ Mencari file catatan log error yang mengungkap arsitektur internal server.[/dim white]"
        ),
        box=box.ROUNDED,
        border_style="#0099FF",
        title="[bold #00D4FF]3. Resep Kombinasi Nyata (Real-World Dork Recipes)[/bold #00D4FF]",
        title_align="left"
    )
    console.print(recipe_panel)

    # 3. Tips Operator Logika
    tips_panel = Panel(
        Text.from_markup(
            "• [bold #FFA726]Tanda Petik Ganda (\"...\")[/]: Wajib untuk frasa persis (exact phrase), contoh: [bold white]\"index of /admin\"[/bold white].\n"
            "• [bold #FFA726]Operator Minus (-)[/]: Mengecualikan hasil, contoh: [bold white]site:target.com -site:www.target.com[/bold white] (fokus subdomain selain www).\n"
            "• [bold #FFA726]Operator OR / Pipet (|)[/]: Logika boolean ATAU (harus huruf kapital), contoh: [bold white]ext:sql OR ext:bak[/bold white].\n"
            "• [bold #FFA726]Tanda Kurung ( ... )[/]: Mengelompokkan logika multi-kondisi, contoh: [bold white]site:target.com (inurl:admin | inurl:login)[/bold white]."
        ),
        box=box.ROUNDED,
        border_style="#FF8C00",
        title="[bold #FF8C00]4. Tips & Logika Boolean Tambahan[/bold #FF8C00]",
        title_align="left"
    )
    console.print(tips_panel)

    console.print("\n[bold #00D4FF]Tekan [bold #FF8C00][Enter][/bold #FF8C00] untuk kembali ke Menu Utama, atau ketik [bold #FF3333]'q'[/bold #FF3333] untuk keluar.[/bold #00D4FF]")
    try:
        nav = Prompt.ask("❯ Navigasi", default="").strip().lower()
    except (KeyboardInterrupt, EOFError):
        abort_program()

    if nav == 'q':
        abort_program()

def get_operator_choices():
    while True:
        display_operator_table()
        
        info_panel = Panel(
            Text.from_markup(
                "[bold white]Ketik nomor atribut yang ingin digunakan[/bold white] (pisahkan koma).\n"
                "[dim]Contoh:[/] [bold #FFA726]1,2,5[/] atau [bold #FFA726]4,5[/] atau [bold #FFA726]1[/] "
                "atau ketik [bold #FF8C00]all[/] untuk memilih semua atribut.\n"
                "[dim]Ketik[/] [bold #FF8C00]11[/] [dim]untuk membuka[/] [bold #FFA726]Buku Panduan & Cheatsheet Dorking Manual[/bold #FFA726]."
            ),
            box=box.ROUNDED,
            border_style="#FF8C00",
            title="[bold #FF8C00]Pilih Atribut / Menu[/bold #FF8C00]",
            title_align="left"
        )
        console.print(info_panel)
        
        try:
            choice = Prompt.ask("[bold #00D4FF]❯ Masukkan pilihan[/bold #00D4FF]").strip()
        except (KeyboardInterrupt, EOFError):
            abort_program()
            
        if choice == GUIDE_OPTION_KEY or choice.lower() in ['guide', 'panduan', 'help']:
            display_guidebook()
            render_banner()
            continue

        if choice.lower() == 'all':
            return list(OPERATORS.keys())
        
        selected = [x.strip() for x in choice.split(',') if x.strip() in OPERATORS]
        if selected:
            # Hilangkan duplikat dan jaga urutan
            seen = set()
            ordered = [x for x in selected if not (x in seen or seen.add(x))]
            return ordered
        else:
            console.print("[bold #FF3333][!] Pilihan tidak valid.[/bold #FF3333] [dim]Silakan masukkan nomor dari tabel (contoh: 1,2,4 atau 11 untuk Panduan).[/dim]")

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
            return []  # unreachable safety net
            
        if val:
            # Peringatan duplikat: filetype: dan ext: dengan nilai yang sama
            if op_prefix in ("filetype:", "ext:"):
                sibling_op = "ext:" if op_prefix == "filetype:" else "filetype:"
                for existing_prefix, existing_val in collected:
                    if existing_prefix == sibling_op and existing_val == val:
                        console.print(f"            [bold #FFA726]⚠ Peringatan:[/bold #FFA726] [dim]'{op_prefix}{val}' redundan dengan '{sibling_op}{val}' yang sudah diisi — tetap ditambahkan.[/dim]")
                        break
            collected.append((op_prefix, val))
        else:
            console.print(f"            [dim #666666]↳ dilewati (kosong)[/dim #666666]")
            
    # Kata kunci bebas tambahan
    console.print()
    try:
        free_text = Prompt.ask("[bold #FFA726]Kata Kunci Bebas / Quote Tambahan[/bold #FFA726] [dim]('contoh: \"admin dashboard\"' / kosongkan)[/dim]").strip()
    except (KeyboardInterrupt, EOFError):
        abort_program()
        return []  # unreachable safety net
        
    if free_text:
        collected.append(("", free_text))
        
    return collected

def _needs_quoting(prefix, val):
    """
    Tentukan apakah nilai perlu dibungkus kutip ganda.
    - Operator yang nilainya selalu single-token (site, filetype, ext, cache,
      related, before, after) TIDAK BOLEH di-quote.
    - Operator frase (intitle, inurl, intext) di-quote hanya jika ada spasi
      DAN belum dibungkus kutip.
    - Kata kunci bebas (prefix kosong) tidak di-auto-quote karena user mungkin
      memasukkan ekspresi boolean (OR, |, tanda kurung) yang harus tetap utuh.
    """
    NO_QUOTE_OPS = {"site:", "filetype:", "ext:", "cache:", "related:", "before:", "after:"}
    if prefix in NO_QUOTE_OPS:
        return False
    if not prefix:
        # Kata kunci bebas — jangan auto-quote, biarkan user mengontrol sendiri
        return False
    # Operator frase: quote hanya jika ada spasi dan belum dikutip
    if ' ' in val and not (val.startswith('"') and val.endswith('"')):
        return True
    return False

def build_query_string(items):
    query_parts = []
    for prefix, val in items:
        if _needs_quoting(prefix, val):
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
