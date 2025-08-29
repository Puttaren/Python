import csv
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

MASTER_FIL = "aktivitetslogg.csv"
SESSION_FIL = "aktivitetslogg_sessioner.csv"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aktivitetslogg")
        self.geometry("680x520")
        self.resizable(False, False)

        # --- State ---
        self.resultat = []

        # --- Formvariabler ---
        self.namn = tk.StringVar()
        self.plats = tk.StringVar()
        self.skjutledare = tk.StringVar()
        self.alder = tk.StringVar()
        self.vapenklass = tk.StringVar(value="A")
        self.poang = tk.StringVar()

        # --- UI ---
        self._build_form()
        self._build_series()

        self.status = tk.StringVar(value="Välkommen! Fyll i grunddata och lägg till serier.")
        ttk.Label(self, textvariable=self.status).pack(anchor="w", padx=12, pady=(8, 0))

    # --------- UI-byggare ----------
    def _build_form(self):
        frm = ttk.LabelFrame(self, text="Grundinformation")
        frm.pack(fill="x", padx=12, pady=12)

        def add_row(row, label, var, width=28):
            ttk.Label(frm, text=label).grid(row=row, column=0, sticky="w", padx=8, pady=6)
            e = ttk.Entry(frm, textvariable=var, width=width)
            e.grid(row=row, column=1, sticky="w")
            return e

        self.e_namn = add_row(0, "Namn", self.namn)
        add_row(1, "Plats", self.plats)
        add_row(2, "Skjutledare", self.skjutledare)

        ttk.Label(frm, text="Ålder").grid(row=0, column=2, sticky="w", padx=(24,8))
        self.e_alder = ttk.Entry(frm, textvariable=self.alder, width=10)
        self.e_alder.grid(row=0, column=3, sticky="w")

        ttk.Label(frm, text="Vapenklass").grid(row=1, column=2, sticky="w", padx=(24,8))
        ttk.Radiobutton(frm, text="A", variable=self.vapenklass, value="A").grid(row=1, column=3, sticky="w")
        ttk.Radiobutton(frm, text="C", variable=self.vapenklass, value="C").grid(row=1, column=4, sticky="w")

    def _build_series(self):
        frm = ttk.LabelFrame(self, text="Serier")
        frm.pack(fill="both", expand=True, padx=12, pady=(0,12))

        left = ttk.Frame(frm); left.pack(side="left", fill="y", padx=8, pady=8)
        right = ttk.Frame(frm); right.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        # Inmatning av poäng
        ttk.Label(left, text="Poäng (0–50), 0 avslutar:").grid(row=0, column=0, sticky="w")
        e = ttk.Entry(left, textvariable=self.poang, width=8)
        e.grid(row=1, column=0, sticky="w", pady=(2,6))
        e.bind("<Return>", lambda _e: self.lagg_till_serie())

        ttk.Button(left, text="Lägg till serie", command=self.lagg_till_serie).grid(row=2, column=0, sticky="w")
        ttk.Button(left, text="Ångra senaste", command=self.angra).grid(row=3, column=0, sticky="w", pady=(6,0))
        ttk.Button(left, text="Spara & avsluta", command=self.spara_och_avsluta).grid(row=4, column=0, sticky="w", pady=(12,0))

        # Lista med registrerade serier
        self.listbox = tk.Listbox(right, height=14)
        self.listbox.pack(fill="both", expand=True)

        # Summering
        self.lbl_sum = ttk.Label(right, text="Inga serier ännu.")
        self.lbl_sum.pack(anchor="w", pady=(8,0))

    # --------- Logik ----------
    @staticmethod
    def berakna_guldkrav(vapenklass: str, alder: int) -> int:
        guldkrav = 42 if vapenklass == "A" else 45
        if alder <= 54:
            guldkrav += 1
        return guldkrav

    def validera_grunddata(self) -> tuple[bool, str]:
        if not self.namn.get().strip():
            return False, "Skriv in Namn."
        if not self.plats.get().strip():
            return False, "Skriv in Plats."
        if not self.skjutledare.get().strip():
            return False, "Skriv in Skjutledare."
        try:
            a = int(self.alder.get().strip())
            if a <= 0 or a > 120:
                return False, "Ogiltig ålder."
        except ValueError:
            return False, "Ålder måste vara ett heltal."
        return True, ""

    def uppdatera_sum(self):
        if not self.resultat:
            self.lbl_sum.config(text="Inga serier ännu.")
            return
        alder = int(self.alder.get().strip())
        gk = self.berakna_guldkrav(self.vapenklass.get(), alder)
        total = sum(self.resultat)
        snitt = total / len(self.resultat)
        guld = sum(1 for p in self.resultat if p >= gk)
        self.lbl_sum.config(
            text=f"Serier: {len(self.resultat)}   Total: {total}   Snitt: {snitt:.2f}   "
                 f"Guldkrav {self.vapenklass.get()}: {gk}   Guldserier: {guld}"
        )

    def lagg_till_serie(self):
        ok, msg = self.validera_grunddata()
        if not ok:
            messagebox.showwarning("Validering", msg)
            return
        s = self.poang.get().strip()
        try:
            p = int(s)
        except ValueError:
            messagebox.showwarning("Validering", "Poäng måste vara heltal.")
            return
        if p == 0:
            # Motsvarar "avsluta" i CLI – här gör vi bara en sammanfattning
            self.spara_och_avsluta()
            return
        if not (0 <= p <= 50):
            messagebox.showwarning("Validering", "Poäng ska vara 0–50.")
            return

        self.resultat.append(p)
        self.listbox.insert(tk.END, f"Serie {len(self.resultat)}: {p}")
        self.poang.set("")
        self.uppdatera_sum()
        self.status.set("Serie tillagd.")

    def angra(self):
        if self.resultat:
            self.resultat.pop()
            self.listbox.delete(tk.END)
            self.uppdatera_sum()
            self.status.set("Senaste serie borttagen.")

    def spara_och_avsluta(self):
        # Grunddata
        ok, msg = self.validera_grunddata()
        if not ok:
            messagebox.showwarning("Validering", msg)
            return
        if not self.resultat:
            messagebox.showinfo("Inget att spara", "Inga serier registrerade.")
            return

        namn = self.namn.get().strip()
        plats = self.plats.get().strip()
        skjutledare = self.skjutledare.get().strip()
        alder = int(self.alder.get().strip())
        vklass = self.vapenklass.get().strip().upper()

        nu = datetime.now()
        datum = nu.strftime("%Y-%m-%d")
        tid = nu.strftime("%H:%M:%S")
        guldkrav = self.berakna_guldkrav(vklass, alder)
        totalpoang = sum(self.resultat)
        snitt = totalpoang / len(self.resultat)
        guld = sum(1 for p in self.resultat if p >= guldkrav)

        # Skriv master (per serie)
        falt_master = ["Datum","Tid","Namn","Ålder","Plats","Skjutledare",
                       "Vapenklass","Guldkrav","SerieNr","Poäng","GuldSerie"]
        nyskapad = not os.path.exists(MASTER_FIL)
        with open(MASTER_FIL, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=falt_master)
            if nyskapad: w.writeheader()
            for i, poang in enumerate(self.resultat, start=1):
                w.writerow({
                    "Datum": datum, "Tid": tid, "Namn": namn, "Ålder": alder,
                    "Plats": plats, "Skjutledare": skjutledare,
                    "Vapenklass": vklass, "Guldkrav": guldkrav,
                    "SerieNr": i, "Poäng": poang,
                    "GuldSerie": "Ja" if poang >= guldkrav else "Nej"
                })

        # Skriv session (en rad)
        falt_session = ["Datum","Tid","Namn","Ålder","Plats","Skjutledare",
                        "Vapenklass","Guldkrav","AntalSerier","Totalpoäng",
                        "Snittpoäng","Guldserier","Serier"]
        nyskapad = not os.path.exists(SESSION_FIL)
        with open(SESSION_FIL, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=falt_session)
            if nyskapad: w.writeheader()
            w.writerow({
                "Datum": datum, "Tid": tid, "Namn": namn, "Ålder": alder,
                "Plats": plats, "Skjutledare": skjutledare, "Vapenklass": vklass,
                "Guldkrav": guldkrav, "AntalSerier": len(self.resultat),
                "Totalpoäng": totalpoang, "Snittpoäng": f"{snitt:.2f}",
                "Guldserier": guld, "Serier": "|".join(map(str, self.resultat))
            })

        messagebox.showinfo(
            "Sparat",
            f"Per-serie: {MASTER_FIL}\nSessioner: {SESSION_FIL}\n\nTack för idag!"
        )
        self.status.set("Allt sparat. Du kan fortsätta lägga serier eller stänga fönstret.")

if __name__ == "__main__":
    App().mainloop()
