import sqlite3
import os

# Pfad zu deiner SQLite-Datenbank
DB_PATH = "/media/Volume/Dokumente/Bier brauen/Programme/Kleiner-Brauhelfer/kb_daten_V2.6.sqlite"

# Zielordner für die HTML-Dateien
OUTPUT_DIR = "html_rezepte"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Verbindung zur Datenbank
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row   # Zeilen wie Dictionaries
cursor = conn.cursor()

# Rezepte + Mengen auslesen
cursor.execute("""
    With GesamtMalz as (
		SELECT
			SudID,        
			Round(Sum(erg_Menge),1) as TotalMalz
		FROM Malzschuettung    
		Group by SudID),
	GesamtHopfen as (
		SELECT
			SudID,        
			Round(Sum(erg_Menge)) as TotalHopfen
		FROM Hopfengaben
		Group by SudID),
	MalzProSorte as (
		SELECT
			SudID,
			Name,
			Round(Sum(erg_Menge),1) as TotalMalzSorte
		FROM Malzschuettung
		Group by SudID, Name
        Order by TotalMalzSorte Desc),
	HopfenProSorte as (
		SELECT
			SudID,
			Name,
			Round(Sum(erg_Menge),1) as TotalHopfenSorte
		FROM Hopfengaben
		Group by SudID, Name
        Order by TotalHopfenSorte Desc),
	Malzliste as (
		SELECT
			GM.SudID,
			GM.TotalMalz,
			Group_Concat(
				(Cast(Round((MS.TotalMalzSorte * 100) / GM.TotalMalz) as Integer) || '% ' || MS.Name), ', '
				--Order by MS.TotalMalzSorte Desc, MS.Name ASC
				 ) as MalzListe
		FROM GesamtMalz GM
		Join MalzProSorte MS on GM.SudID = MS.SudID
		Group by MS.SudID),
	Hopfenliste as (
		SELECT
			GH.SudID,
			GH.TotalHopfen,
			Group_Concat(
				(Cast(Round((HS.TotalHopfenSorte * 100) / GH.TotalHopfen) as Integer) || '% ' || HS.Name), ', '
				--Order by HS.TotalHopfenSorte Desc, HS.Name ASC
				 ) as HopfenListe
		FROM GesamtHopfen GH
		Join HopfenProSorte HS on GH.SudID = HS.SudID
		Group by GH.SudID),
    Hefeliste as (
		SELECT
			SudID,			
			Group_Concat(Name, ', ') as HefeListe
		FROM Hefegaben 
		Group by SudID)           
	SELECT
        Sud.ID,
        Sud.Sudname as name,
        Sud.Sudnummer as sudnummer,
        Round(Sud.SW, 1) as stammwuerze,
        Cast(Round(Sud.IBU, 1) as Integer) as ibu,
        Cast(Round(Sud.erg_Farbe, 0) as Integer) as farbe,
        Round(Sud.erg_Alkohol, 1) as alkohol,
        Cast(Round(Sud.Menge) as Integer) as menge,
        Strftime('%d.%m.%Y', Sud.Braudatum) as braudatum,
        Strftime('%d.%m.%Y', Sud.Abfuelldatum) as abfuelldatum,
        Cast(ML.TotalMalz as Integer) as TotalMalz,
        ML.Malzliste,
        Cast(HL.TotalHopfen as Integer) as TotalHopfen,
        HL.HopfenListe,
        HL2.HefeListe
	From Sud
	Left Join Malzliste ML on Sud.ID = ML.SudID
	Left Join Hopfenliste HL on Sud.ID = HL.SudID
	Left Join Hefeliste HL2 on Sud.ID = HL2.SudID
	Where Sud.braudatum is not null
    order by Sud.Sudnummer asc
""")
rezepte = cursor.fetchall()

# Übersichtseite erstellen
overview_path = os.path.join(OUTPUT_DIR, "UebersichtBraurezepte.html")
with open(overview_path, "w", encoding="utf-8") as f:
    f.write("<!DOCTYPE html><html><head><meta charset='UTF-8'><title>Braurezepte</title></head><body>\n")    
    f.write("<h2><a href=\"../index.html\">Home</a></h2>\n")
    f.write("<h1>Meine Braurezepte</h1><ul>\n")
    for r in rezepte:
        filename = f"Rezept_{r['sudnummer']}_{r['name']}.html"
        f.write(f"<li><a href='{filename}'>{r['sudnummer']} – {r['name']}</a></li>\n")
    f.write("</ul></body></html>\n")

# Einzelseiten pro Rezept erstellen
for r in rezepte:
    filename = os.path.join(OUTPUT_DIR, f"Rezept_{r['sudnummer']}_{r['name']}.html")
    with open(filename, "w", encoding="utf-8") as f:
        f.write("<!DOCTYPE html><html><head><meta charset='UTF-8'></head><body>\n")
        f.write(f"<h2><a href='UebersichtBraurezepte.html'>Übersicht Braurezepte</a></h2>\n")
        f.write(f"<h1>{r['name']}</h1>\n")       
        f.write(f"<p><strong>Stammwürze:</strong> {r['stammwuerze']} °P</p>\n")
        f.write(f"<p><strong>Alkohol:</strong> {r['alkohol']} % vol</p>\n")
        f.write(f"<p><strong>Bittere:</strong> {r['ibu']} IBU</p>\n")
        f.write(f"<p><strong>Farbe:</strong> {r['farbe']} EBC</p>\n")
        f.write(f"<p><strong>Menge:</strong> {r['menge']} l</p>\n")
        f.write(f"<p><strong>Braudatum:</strong> {r['braudatum']}</p>\n")
        f.write(f"<p><strong>Abfülldatum:</strong> {r['abfuelldatum']}</p>\n")
        f.write(f"<p><strong>Malz Menge:</strong> {r['TotalMalz']} kg</p>\n")
        f.write(f"<p><strong>Malz Liste:</strong> {r['MalzListe']}</p>\n")
        f.write(f"<p><strong>Hopfen Menge:</strong> {r['TotalHopfen']} g</p>\n")
        f.write(f"<p><strong>Hopfen Liste:</strong> {r['HopfenListe']}</p>\n")
        f.write(f"<p><strong>Hefe Liste:</strong> {r['HefeListe']}</p>\n")
        f.write("</body></html>\n")

conn.close()

print(f"HTML-Dateien wurden in {OUTPUT_DIR} erstellt.")

