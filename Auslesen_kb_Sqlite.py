import sqlite3
import os

# Pfad zu deiner SQLite-Datenbank
DB_PATH = "/home/Thomas/Dokumente/Dokumente D (symlink)/Bier brauen/Programme/Kleiner-Brauhelfer/kb_daten_V2.6 (Kopie 1).sqlite"

# Zielordner für die HTML-Dateien
OUTPUT_DIR = "html_rezepte"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Verbindung zur Datenbank
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Beispiel: Rezepte auslesen (Tabellenname kann je nach Version variieren!)
cursor.execute("""
    SELECT                
        Sudnummer           as id,
        Sudname             as name,
        Round(SW, 1)        as stammwuerze,       
        Round(ibu, 1)   as ibu,
        Round(erg_Farbe, 0) as farbe,               
        Round(erg_Alkohol, 1)   as alkohol,
        strftime('%d.%m.%Y', Braudatum) as Braudatum,
        strftime('%d.%m.%Y', Abfuelldatum) as Abfuelldatum
        --ID,
        --Kategorie,
        --Anlage,
        --Menge,        
        --highGravityFaktor,
        --FaktorHauptguss,
        --Wasserprofil,
        --RestalkalitaetSoll,
        --CO2,        
        --berechnungsArtHopfen,
        --Kochdauer,
        --Nachisomerisierungszeit,
        --Reifezeit,
        --KostenWasserStrom,
        --Kommentar,
        --Status,        
        --Erstellt,
        --Gespeichert,
        --erg_S_Gesamt,
        --erg_W_Gesamt,
        --erg_WHauptguss,
        --erg_WNachguss,        
        --SWKochende,
        --SWAnstellen,
        --SchnellgaerprobeAktiv,
        --SWSchnellgaerprobe,
        --SWJungbier,
        --TemperaturJungbier,
        --WuerzemengeVorHopfenseihen,
        --WuerzemengeKochende,
        --WuerzemengeAnstellen,
        --Spunden,
        --Speisemenge,
        --JungbiermengeAbfuellen,
        --erg_AbgefuellteBiermenge,
        --erg_Sudhausausbeute,
        --erg_EffektiveAusbeute,
        --erg_Preis,        
        --AusbeuteIgnorieren,
        --MerklistenID,
        --Sudhausausbeute,
        --Verdampfungsrate,
        --Vergaerungsgrad,
        --WuerzemengeKochbeginn,
        --SWKochbeginn,
        --VerschneidungAbfuellen,
        --TemperaturKarbonisierung,
        --BemerkungBrauen,
        --BemerkungAbfuellen,
        --BemerkungGaerung,
        --ReifungStart,
        --VerduennungAnstellen,
        --BemerkungZutatenMaischen,
        --BemerkungZutatenKochen,
        --BemerkungZutatenGaerung,
        --BemerkungMaischplan,
        --BemerkungWasseraufbereitung,
        --MengeHefestarter,
        --SWHefestarter
  FROM Sud Where braudatum IS NOT NULL
""")
rezepte = cursor.fetchall()

# Übersichtseite erstellen
overview_path = os.path.join(OUTPUT_DIR, "UebersichtBraurezepte.html")
with open(overview_path, "w", encoding="utf-8") as f:
    f.write("<!DOCTYPE html><html><head><meta charset='UTF-8'><title>Braurezepte</title></head><body>\n")
    f.write("<h2><a href=\"https://thomas-lehmenkoetter.github.io/Homebrew/index.html\">Home</a></h2>\n")
    f.write("<h1>Meine Braurezepte</h1><ul>\n")
    for r in rezepte:
        rid, name, _, _, _, _, _, _ = r
        filename = f"Rezept_{rid}_{name}.html"
        f.write(f"<li><a href='{filename}'>{rid}_{name}</a></li>\n")
    f.write("</ul></body></html>\n")

# Einzelseiten pro Rezept erstellen
for r in rezepte:
    rid, name, stammwuerze, alkohol, ibu, farbe, braudatum, abfuelldatum = r
    filename = os.path.join(OUTPUT_DIR, f"Rezept_{rid}_{name}.html")
    with open(filename, "w", encoding="utf-8") as f:
        f.write("<!DOCTYPE html><html><head><meta charset='UTF-8'></head><body>\n")
        f.write(f"<h2><a href='UebersichtBraurezepte.html'>Übersicht Braurezepte</a></h2>\n")
        f.write(f"<h1>{name}</h1>\n")
        f.write(f"<p><strong>Stammwürze:</strong> {stammwuerze} °P</p>\n")
        f.write(f"<p><strong>Alkohol:</strong> {alkohol} % vol</p>\n")
        f.write(f"<p><strong>Bittere:</strong> {ibu} IBU</p>\n")
        f.write(f"<p><strong>Farbe:</strong> {farbe} EBC</p>\n")
        f.write(f"<p><strong>Braudatum:</strong> {braudatum}</p>\n")
        f.write(f"<p><strong>Abfülldatum:</strong> {abfuelldatum}</p>\n")
        f.write("</body></html>\n")

conn.close()

print(f"HTML-Dateien wurden in {OUTPUT_DIR} erstellt.")
