import csv
import os
from datetime import datetime

print("Aktivitetslogg\n")

# --- Grundinfo ---
namn = input("Ditt namn? ").strip()
plats = input("Skjutplats? ").strip()
skjutledare = input("Skjutledare? ").strip()

# --- Ålder ---
while True:
    s = input("Din ålder? ").strip()
    try:
        alder = int(s)
    except ValueError:
        print("Ange ett heltal för ålder.")
        continue
    svar = input(f"Är {alder} korrekt? (j/n): ").strip().lower()
    if svar in {"j", "ja"}:
        break
    elif svar in {"n", "nej"}:
        continue
    else:
        print("Svara j eller n.")
        continue

# --- Vapenklass ---
while True:
    vapenklass = input("Vapenklass (A/C)? ").strip().upper()
    if vapenklass in {"A", "C"}:
        break
    print("Ogiltig inmatning. Skriv A eller C.")

# Grundkrav + åldersjustering
guldkrav = 42 if vapenklass == "A" else 45
if alder <= 54:
    guldkrav += 1

# --- Registrera serier ---
print("\nRegistrera poäng (0 avslutar). Maxpoäng per serie: 50.")
resultat = []
avsluta = False

while not avsluta:
    serienr = len(resultat) + 1
    while True:
        s = input(f"Poäng (Serie {serienr})? ").strip()
        if not s:
            continue
        try:
            p = int(s)
        except ValueError:
            print("Ange ett heltal.")
            continue

        if p == 0:
            avsluta = True
            break
        if p < 0:
            print("Poäng kan inte vara negativt.")
            continue
        if p > 50:
            print("Maxpoängen är 50. Ange 50 eller lägre.")
            continue

        svar = input(f"Serie {serienr}: Är {p} korrekt? (j/n): ").strip().lower()
        if svar in {"j", "ja"}:
            resultat.append(p)
            break
        elif svar in {"n", "nej"}:
            print("Okej, ange poängen på nytt.")
            continue
        else:
            print("Svara j eller n.")
            continue

# Hantera fallet med inga serier
if not resultat:
    print("\nInga serier registrerade. Avslutar utan export.")
    raise SystemExit(0)

# --- Sammanställ ---
nu = datetime.now()
datum = nu.strftime("%Y-%m-%d")
tid = nu.strftime("%H:%M:%S")

totalpoang = sum(resultat)
snitt = totalpoang / len(resultat)

# --- Utskrift ---
print("\nResultat:")
guld = 0
for i, poang in enumerate(resultat, start=1):
    if poang >= guldkrav:
        print(f"Serie {i}: {poang}*")
        guld += 1
    else:
        print(f"Serie {i}: {poang}")

print(f"\nGuldkrav (klass {vapenklass}): {guldkrav}")
print(f"Antal serier: {len(resultat)}")
print(f"Totalpoäng: {totalpoang}")
print(f"Snittpoäng: {snitt:.2f}")
print(f"Guldserier: {guld}")
print("Bra jobbat idag. Välkommen åter!")

# --- CSV-export: per-serie masterfil ---
master_fil = "aktivitetslogg.csv"
fält_master = [
    "Datum", "Tid", "Namn", "Ålder", "Plats", "Skjutledare",
    "Vapenklass", "Guldkrav", "SerieNr", "Poäng", "GuldSerie"
]

def skriv_master(csv_fil):
    nyskapad = not os.path.exists(csv_fil)
    with open(csv_fil, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fält_master)
        if nyskapad:
            writer.writeheader()
        for i, poang in enumerate(resultat, start=1):
            writer.writerow({
                "Datum": datum,
                "Tid": tid,
                "Namn": namn,
                "Ålder": alder,
                "Plats": plats,
                "Skjutledare": skjutledare,
                "Vapenklass": vapenklass,
                "Guldkrav": guldkrav,
                "SerieNr": i,
                "Poäng": poang,
                "GuldSerie": "Ja" if poang >= guldkrav else "Nej",
            })

skriv_master(master_fil)
print(f"\nData (per serie) sparad i '{master_fil}'.")

# --- CSV-export: session på en rad ---
session_fil = "aktivitetslogg_sessioner.csv"
fält_session = [
    "Datum", "Tid", "Namn", "Ålder", "Plats", "Skjutledare",
    "Vapenklass", "Guldkrav", "AntalSerier", "Totalpoäng",
    "Snittpoäng", "Guldserier", "Serier"
]

def join_serier(values):
    return "|".join(str(v) for v in values)

nyskapad = not os.path.exists(session_fil)
with open(session_fil, mode="a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fält_session)
    if nyskapad:
        writer.writeheader()
    writer.writerow({
        "Datum": datum,
        "Tid": tid,
        "Namn": namn,
        "Ålder": alder,
        "Plats": plats,
        "Skjutledare": skjutledare,
        "Vapenklass": vapenklass,
        "Guldkrav": guldkrav,
        "AntalSerier": len(resultat),
        "Totalpoäng": totalpoang,
        "Snittpoäng": f"{snitt:.2f}",
        "Guldserier": guld,
        "Serier": join_serier(resultat),
    })
print(f"Session (en rad) sparad i '{session_fil}'.")

#Testar ändring igen