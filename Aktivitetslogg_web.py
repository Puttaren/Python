import io
import csv
import os
from datetime import datetime
import smtplib
from email.message import EmailMessage

import streamlit as st
import pandas as pd

# ---------- Hjälpfunktioner ----------
def berakna_guldkrav(vklass: str, alder: int) -> int:
    gk = 42 if vklass == "A" else 45
    if alder <= 54:
        gk += 1
    return gk

def build_master_rows(datum, tid, namn, alder, plats, skjutledare, vklass, guldkrav, serier):
    rows = []
    for i, p in enumerate(serier, start=1):
        rows.append({
            "Datum": datum, "Tid": tid, "Namn": namn, "Ålder": alder, "Plats": plats,
            "Skjutledare": skjutledare, "Vapenklass": vklass, "Guldkrav": guldkrav,
            "SerieNr": i, "Poäng": p, "GuldSerie": "Ja" if p >= guldkrav else "Nej"
        })
    return rows

def build_session_row(datum, tid, namn, alder, plats, skjutledare, vklass, guldkrav, serier):
    total = sum(serier)
    snitt = total / len(serier)
    guld = sum(1 for p in serier if p >= guldkrav)
    return {
        "Datum": datum, "Tid": tid, "Namn": namn, "Ålder": alder, "Plats": plats,
        "Skjutledare": skjutledare, "Vapenklass": vklass, "Guldkrav": guldkrav,
        "AntalSerier": len(serier), "Totalpoäng": total, "Snittpoäng": f"{snitt:.2f}",
        "Guldserier": guld, "Serier": "|".join(map(str, serier))
    }

def rows_to_csv_bytes(rows, fieldnames) -> bytes:
    buff = io.StringIO()
    writer = csv.DictWriter(buff, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows if isinstance(rows, list) else [rows])
    return buff.getvalue().encode("utf-8")

def send_mail(to_addr: str, subject: str, body: str, attachments: list[tuple[str, bytes, str]]) -> str:
    """
    attachments: list of tuples (filename, content_bytes, mime)
    SMTP-uppgifter läses från st.secrets["smtp"].
    """
    smtp_cfg = st.secrets.get("smtp", {})
    host = smtp_cfg.get("host")
    port = int(smtp_cfg.get("port", 465))
    user = smtp_cfg.get("user")
    pwd  = smtp_cfg.get("password")
    from_addr = smtp_cfg.get("from", user)

    if not (host and port and user and pwd and from_addr):
        return "Saknar SMTP-uppgifter i .streamlit/secrets.toml."

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.set_content(body)

    for filename, content, mime in attachments:
        maintype, subtype = mime.split("/", 1)
        msg.add_attachment(content, maintype=maintype, subtype=subtype, filename=filename)

    # SSL (465) eller STARTTLS (587)
    if port == 465:
        with smtplib.SMTP_SSL(host, port) as s:
            s.login(user, pwd)
            s.send_message(msg)
    else:
        with smtplib.SMTP(host, port) as s:
            s.starttls()
            s.login(user, pwd)
            s.send_message(msg)

    return "OK"

# ---------- UI ----------
st.set_page_config(page_title="Aktivitetslogg", page_icon="⛳", layout="centered")
st.title("Aktivitetslogg")

with st.form("grundform"):
    col1, col2 = st.columns(2)
    namn = col1.text_input("Namn", "")
    plats = col2.text_input("Plats", "")
    skjutledare = col1.text_input("Skjutledare", "")
    alder = col2.number_input("Ålder", min_value=1, max_value=120, step=1, value=30)
    vklass = st.radio("Vapenklass", ["A", "C"], horizontal=True, index=0)
    epost = st.text_input("E-post för kvitto (frivilligt men behövs om du vill maila resultat)", "")

    st.markdown("**Serier (0–50)**")
    if "serier" not in st.session_state:
        st.session_state.serier = []

    c1, c2, c3 = st.columns([1,1,1])
    nytt_poang = c1.number_input("Poäng för nästa serie", min_value=0, max_value=50, step=1, value=0)
    add = c1.form_submit_button("Lägg till serie")
    undo = c2.form_submit_button("Ångra senaste")
    clear = c3.form_submit_button("Rensa alla")

    if add:
        if nytt_poang == 0:
            st.warning("0 används inte här — lägg till faktiska serier (1–50).")
        else:
            st.session_state.serier.append(int(nytt_poang))
    if undo and st.session_state.serier:
        st.session_state.serier.pop()
    if clear:
        st.session_state.serier = []

    submitted = st.form_submit_button("Uppdatera summering")

gk = berakna_guldkrav(vklass, int(alder))
st.info(f"Guldkrav (klass {vklass}): **{gk}**")

# Tabell och summering
if st.session_state.serier:
    df = pd.DataFrame({"SerieNr": range(1, len(st.session_state.serier)+1),
                       "Poäng": st.session_state.serier})
    df["GuldSerie"] = df["Poäng"] >= gk
    st.dataframe(df, width="stretch", hide_index=True)
    total = int(df["Poäng"].sum())
    snitt = float(df["Poäng"].mean())
    guld = int(df["GuldSerie"].sum())
    st.success(f"Serier: {len(df)}  |  Totalpoäng: {total}  |  Snitt: {snitt:.2f}  |  Guldserier: {guld}")
else:
    st.warning("Inga serier ännu.")

st.divider()

# ---------- Export/epost ----------
disabled = len(st.session_state.serier) == 0 or namn.strip() == "" or plats.strip() == "" or skjutledare.strip() == ""

colA, colB, colC = st.columns([1,1,1])
if st.session_state.serier:
    now = datetime.now()
    datum = now.strftime("%Y-%m-%d")
    tid = now.strftime("%H:%M:%S")

    master_rows = build_master_rows(datum, tid, namn, int(alder), plats, skjutledare, vklass, gk, st.session_state.serier)
    session_row = build_session_row(datum, tid, namn, int(alder), plats, skjutledare, vklass, gk, st.session_state.serier)

    master_fields = ["Datum","Tid","Namn","Ålder","Plats","Skjutledare","Vapenklass","Guldkrav","SerieNr","Poäng","GuldSerie"]
    session_fields = ["Datum","Tid","Namn","Ålder","Plats","Skjutledare","Vapenklass","Guldkrav",
                      "AntalSerier","Totalpoäng","Snittpoäng","Guldserier","Serier"]

    master_csv = rows_to_csv_bytes(master_rows, master_fields)
    session_csv = rows_to_csv_bytes(session_row, session_fields)

    colA.download_button(
        label="Ladda ner per-serie CSV",
        data=master_csv,
        file_name="aktivitetslogg.csv",
        mime="text/csv",
    )
    colB.download_button(
        label="Ladda ner session CSV",
        data=session_csv,
        file_name="aktivitetslogg_sessioner.csv",
        mime="text/csv",
    )

# Mailknapp längst ned
st.write("")
maila = st.button("✉️ Maila resultat", disabled=disabled)

if maila:
    if not epost or "@" not in epost:
        st.error("Fyll i en giltig e-postadress högre upp.")
    else:
        body = (f"Namn: {namn}\nPlats: {plats}\nSkjutledare: {skjutledare}\n"
                f"Ålder: {alder}\nVapenklass: {vklass}\nGuldkrav: {gk}\n"
                f"Serier: {', '.join(map(str, st.session_state.serier))}\n"
                f"Datum/Tid: {datum} {tid}\n")
        result = send_mail(
            to_addr=epost,
            subject=f"Aktivitetslogg {datum} {tid}",
            body=body,
            attachments=[
                ("aktivitetslogg.csv", master_csv, "text/csv"),
                ("aktivitetslogg_sessioner.csv", session_csv, "text/csv"),
            ],
        )
        if result == "OK":
            st.success(f"Skickat till {epost}.")
        else:
            st.error(f"Kunde inte skicka e-post: {result}\n"
                     "Kontrollera SMTP-uppgifterna i .streamlit/secrets.toml.")
