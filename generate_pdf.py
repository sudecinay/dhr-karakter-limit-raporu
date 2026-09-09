# -*- coding: utf-8 -*-
import re
import subprocess
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "index.html"
PRINT = ROOT / "print.html"
PDF = ROOT / "dhr-karakter-limit-raporu.pdf"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

source = INDEX.read_text(encoding="utf-8")
match = re.search(r"const FIELDS = \[(.*?)\];", source, re.S)
if not match:
    raise SystemExit("FIELDS not found")
fields = re.findall(r'\["((?:\\.|[^"])*)","((?:\\.|[^"])*)","((?:\\.|[^"])*)","((?:\\.|[^"])*)","((?:\\.|[^"])*)","((?:\\.|[^"])*)"\]', match.group(1))
if not fields:
    raise SystemExit("no field rows parsed")

def rows(items):
    out = []
    for row in items:
        cells = "".join(f"<td>{escape(col)}</td>" for col in row)
        out.append(f"<tr>{cells}</tr>")
    return "\n".join(out)

PRINT.write_text(f"""<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8" />
  <title>DHR karakter limit raporu</title>
  <style>
    @page {{ size: A4 landscape; margin: 10mm; }}
    html, body {{ margin: 0; background: #fff; color: #1b2130; }}
    body {{ font: 10px/1.35 "Segoe UI", "Noto Sans", sans-serif; padding: 8px 12px; }}
    h1 {{ font-size: 18px; margin: 0 0 4px; }}
    h2 {{ font-size: 12px; margin: 14px 0 6px; }}
    .lead, .note {{ color: #44506a; margin: 0 0 10px; }}
    .note {{ background: #fff6e5; border: 1px solid #e2c37a; padding: 8px 10px; }}
    .stats {{ display: flex; gap: 10px; margin: 0 0 10px; }}
    .stat {{ border: 1px solid #d5dbe7; padding: 6px 10px; min-width: 120px; }}
    .stat b {{ display: block; font-size: 16px; color: #0f7a70; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border: 1px solid #d5dbe7; padding: 4px 6px; text-align: left; vertical-align: top; }}
    th {{ background: #eef1f7; font-size: 9px; }}
    td:nth-child(5) {{ font-weight: 700; color: #0f7a70; white-space: nowrap; }}
    .box {{ border: 1px solid #d5dbe7; padding: 8px; }}
    .templates {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }}
  </style>
</head>
<body>
  <h1>DHR karakter limit raporu</h1>
  <p class="lead">Dropdown, tarih ve dosya yükleme hariç. Limit hem yazmayı kesmeli hem kaydı reddetmeli. Sayaç: n / limit.</p>
  <div class="stats">
    <div class="stat"><b>{len(fields)}</b>Toplam alan</div>
    <div class="stat"><b>100</b>Standart başlık</div>
    <div class="stat"><b>500</b>Standart açıklama</div>
  </div>
  <div class="note">Doküman Gönder açıklamasında 30 / 500 sayacı var. Aynı formdaki doküman adında ve Yeni Çalışan Ekle sekmelerinde maxlength yok.</div>
  <h2>Alan tipi standardı</h2>
  <table>
    <thead><tr><th>Tip</th><th>Limit</th><th>Kural</th></tr></thead>
    <tbody>
      <tr><td>Başlık / ad</td><td>80 veya 100</td><td>Tek satır. Liste ve modal başlıklarını bozmamalı.</td></tr>
      <tr><td>Açıklama / not</td><td>500 (görev/ticket/not: 1000)</td><td>Doküman Gönder’deki 500 sayacı ürün standardı.</td></tr>
      <tr><td>Kod</td><td>20 (seri no: 50)</td><td>Kısa teknik kimlik. Seri numarası ayrı, daha uzun.</td></tr>
      <tr><td>Adres</td><td>255</td><td>Tek satır açık adres.</td></tr>
      <tr><td>Telefon</td><td>20 (ülke kodu ayrıysa 15)</td><td>Sadece + ve rakam.</td></tr>
      <tr><td>E-posta</td><td>100</td><td>Format: adı@alan.tld.</td></tr>
      <tr><td>Kimlik no</td><td>sabit hane</td><td>TCKN 11, vergi 10, SGK 13, pasaport 15.</td></tr>
      <tr><td>Tutar</td><td>12+2 hane</td><td>Virgülden sonra 2 basamak. Negatif yok.</td></tr>
      <tr><td>Sayı</td><td>alana göre 2–6 hane</td><td>Min–max ayrıca yazılmalı.</td></tr>
      <tr><td>Koordinat</td><td>12 karakter</td><td>Enlem −90…90, boylam −180…180.</td></tr>
    </tbody>
  </table>
  <h2>Alan bazlı önerilen limitler</h2>
  <table>
    <thead>
      <tr><th>Modül</th><th>Ekran</th><th>Alan</th><th>Tip</th><th>Önerilen limit</th><th>Gerekçe</th></tr>
    </thead>
    <tbody>
      {rows(fields)}
    </tbody>
  </table>
  <h2>Bug cümlesi şablonu</h2>
  <div class="templates">
    <div class="box"><b>Metin alanı</b><p>[Modül] / [ekran] içindeki [alan] alanında karakter sınırı yok. Beklenen: maxlength = [sayı], sayaç “n / [sayı]”, limit aşınca yazım durmalı ve kayıt gitmemeli.</p></div>
    <div class="box"><b>Sayı / tutar / kimlik</b><p>[Alan] alanında hane / değer sınırı yok. Beklenen: [min]–[max]. TCKN tam 11, vergi tam 10. Negatif ve harf reddedilmeli.</p></div>
  </div>
</body>
</html>
""", encoding="utf-8")

subprocess.run([
    CHROME,
    "--headless=new",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={PDF}",
    PRINT.resolve().as_uri(),
], check=True)
print(f"rows={len(fields)}")
print(f"pdf={PDF} size={PDF.stat().st_size}")
