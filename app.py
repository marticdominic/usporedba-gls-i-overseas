import io
import math
import re
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Logistički Simulator (GLS vs Overseas)", page_icon="🔀", layout="wide"
)

st.title("🔀 Simulator i Usporedba Osnovnih Cijena Prijevoza")
st.write(
    "Namjenska aplikacija za brzu usporedbu troškova osnovnog transporta između GLS-a i Overseasa na temelju ugovornih cjenika."
)

# ---------------------------------------------------------
# UGOVORNI PARAMETRI I CJENICI
# ---------------------------------------------------------
zona_3_pbr = [
    20000, 20205, 20207, 20210, 20213, 20215, 20216, 20217, 20218,
    20230, 20231, 20232, 20233, 20234, 20235, 20236, 20240, 20242, 20243,
    20244, 20245, 20246, 20247, 20248, 20250, 20260, 20263, 20264,
    20267, 20269, 20270, 20271, 20272, 20273, 20274, 20275, 21400,
    21403, 21404, 21405, 21410, 21412, 21413, 21420, 21423, 21424,
    21425, 21426, 21450, 21454, 21460, 21462, 21463, 21465, 21466,
    21467, 21468, 21469, 21480, 21483, 21485, 22240, 22242, 22243,
    22244, 23212, 23234, 23249, 23250, 23251, 23262, 23263, 23264,
    23271, 23272, 23273, 23274, 23275, 51280, 51281, 51500, 51511,
    51512, 51513, 51514, 51515, 51516, 51517, 51521, 51522, 51523,
    51550, 51551, 51554, 51555, 51556, 51557, 51559, 51564, 53291,
    53294, 53296,
]

zona_2_pbr = [
    23440, 23445, 23446, 31300, 31321, 31322, 31323, 31324, 31542, 31543,
    31555, 43270, 43271, 43273, 44202, 44203, 44210, 44213, 44214, 44221,
    44222, 44251, 44271, 44272, 44273, 44400, 44401, 44402, 44412, 44425,
    44430, 44450, 47220, 47221, 47222, 47245, 47246, 47304, 47305, 47306,
    47307, 47313, 47314, 48260, 48265, 48267, 48323, 51212, 51213, 51251,
    51300, 51311, 51312, 51313, 51314, 51315, 51316, 51321, 51322, 51323,
    51324, 51325, 51328, 51329, 51414, 51418, 52000, 52402, 52420, 52421,
    52422, 52425, 52426, 52427, 52428, 52434, 53000, 53202, 53203, 53205,
    53206, 53211, 53212, 53213, 53221, 53222, 53223, 53224, 53230, 53231,
    53234, 53235, 53244, 53250, 53252, 53260, 53261, 53262, 53284, 53285,
    53286, 53287, 53288,
]

cjenik_overseas = {
    "Zona 1": {1.0: 2.84*1.05, 2.0: 3.15*1.05, 5.0: 3.44*1.05, 10.0: 4.79*1.05, 15.0: 5.39*1.05, 20.0: 6.07*1.05, 25.0: 6.82*1.05, 30.0: 7.34*1.05, 35.0: 8.09*1.05, 40.0: 8.38*1.05, 45.0: 8.46*1.05, 50.0: 9.21*1.05},
    "Zona 2": {1.0: 3.31*1.05, 2.0: 3.80*1.05, 5.0: 4.19*1.05, 10.0: 5.54*1.05, 15.0: 6.29*1.05, 20.0: 7.18*1.05, 25.0: 8.09*1.05, 30.0: 8.68*1.05, 35.0: 9.59*1.05, 40.0: 10.04*1.05, 45.0: 10.49*1.05, 50.0: 11.24*1.05},
    "Zona 3": {1.0: 3.31*1.05, 2.0: 3.80*1.05, 5.0: 4.19*1.05, 10.0: 5.54*1.05, 15.0: 6.29*1.05, 20.0: 7.18*1.05, 25.0: 8.09*1.05, 30.0: 8.68*1.05, 35.0: 9.59*1.05, 40.0: 10.04*1.05, 45.0: 10.49*1.05, 50.0: 11.24*1.05},
}


def odredis_zonu_overseas(pbr):
    try:
        pbr = int(pbr)
    except:
        return "Zona 2"
    if pbr in zona_3_pbr:
        return "Zona 3"
    elif pbr in zona_2_pbr:
        return "Zona 2"
    elif 10000 <= pbr <= 10449:
        return "Zona 1"
    else:
        return "Zona 2"


def izracunaj_osnovnu_cijenu_overseas(masa, zona):
    granice = [1.0, 2.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0]
    z_tablica = cjenik_overseas.get(zona, cjenik_overseas["Zona 2"])
    if masa <= 50.0:
        for g in granice:
            if masa <= g:
                osnova = z_tablica[g]
                break
        else:
            osnova = z_tablica[50.0]
    else:
        baza = z_tablica[50.0]
        visak = math.ceil(masa - 50.0)
        dodatak_po_kg = (0.19 if zona == "Zona 1" else 0.22) * 1.05
        osnova = baza + visak * dodatak_po_kg
    if zona == "Zona 3":
        osnova = osnova * 1.25
    return osnova


OSNOVNA_CIJENA_GLS_STANDARD = 3.66  #[cite: 4]
OSNOVNA_CIJENA_GLS_SMALL = 4.38     #[cite: 4]


def izracunaj_osnovnu_cijenu_gls(masa):
    if masa < 2.0:
        return OSNOVNA_CIJENA_GLS_STANDARD
    else:
        return OSNOVNA_CIJENA_GLS_SMALL


def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Usporedba_Cijena")
    return output.getvalue()


uploaded_file = st.file_uploader(
    "Učitajte fakturu bilo kojeg kurira (GLS ili Overseas Excel/CSV)", type=["xlsx", "csv"]
)

if uploaded_file is not None:
    if uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    je_gls = "Parcel number" in df.columns or "Parcel orientation" in df.columns
    je_overseas = "Shipment ID" in df.columns or "Consignee ZIP Code" in df.columns

    if je_gls:
        st.success("📌 Detektiran format: **GLS Faktura**")
        if st.button("Pokreni usporedbu s Overseas cjenikom"):
            rezultati = []
            gls_ukupno_transport = 0.0
            overseas_simulirano_ukupno = 0.0

            for idx, row in df.iterrows():
                masa = float(row.get("Weight / Size", 1.0))
                gls_trans = float(row.get("Transport fee", 0.0))
                adresa = str(row.get("Delivery address", ""))

                match = re.search(r"(?:HR-)?(\d{5})", adresa)
                pbr = int(match.group(1)) if match else 10000

                gls_osnova = izracunaj_osnovnu_cijenu_gls(masa)
                zona_ovs = odredis_zonu_overseas(pbr)
                ovs_osnova = izracunaj_osnovnu_cijenu_overseas(masa, zona_ovs)

                gls_ukupno_transport += gls_trans
                overseas_simulirano_ukupno += ovs_osnova

                rezultati.append({
                    "ID Paketa": row.get("Parcel number", idx + 1),
                    "Masa (kg)": masa,
                    "Poštanski broj": pbr,
                    "Overseas Zona": zona_ovs,
                    "Stvarni GLS Transport (€)": round(gls_trans, 2),
                    "Simulirani Overseas Transport (€)": round(ovs_osnova, 2),
                    "Razlika (GLS vs Overseas €)": round(gls_trans - ovs_osnova, 2),
                })

            res_df = pd.DataFrame(rezultati)

            st.markdown("### 📊 Rezultat usporedbe osnovnih cijena")
            c1, c2, c3 = st.columns(3)
            c1.metric("Stvarni GLS Transport", f"{gls_ukupno_transport:,.2f} €")
            c2.metric("Simulirani Overseas Transport", f"{overseas_simulirano_ukupno:,.2f} €")
            razlika = gls_ukupno_transport - overseas_simulirano_ukupno
            c3.metric(
                "Ukupna razlika",
                f"{abs(razlika):,.2f} €",
                delta="GLS povoljniji" if razlika < 0 else "Overseas povoljniji",
                delta_color="normal" if razlika < 0 else "inverse"
            )

            st.markdown("---")
            st.dataframe(res_df, use_container_width=True)
            st.download_button(
                "📥 Preuzmi izvještaj usporedbe (Excel)",
                to_excel(res_df),
                "usporedba_gls_prema_overseas.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

    elif je_overseas:
        st.success("📌 Detektiran format: **Overseas Faktura**")
        if st.button("Pokreni usporedbu s GLS cjenikom"):
            rezultati = []
            overseas_ukupno_transport = 0.0
            gls_simulirano_ukupno = 0.0

            for idx, row in df.iterrows():
                pbr = int(row.get("Consignee ZIP Code", 10000))
                masa = float(row.get("Weight", 1.0))
                broj_paketa = int(row.get("Number of Parcels", 1))
                ovs_trans = float(row.get("Transport Price", 0.0))

                zona_ovs = odredis_zonu_overseas(pbr)
                ovs_osnova = izracunaj_osnovnu_cijenu_overseas(masa, zona_ovs)

                prosjecna_masa = masa / max(1, broj_paketa)
                gls_po_paketu = izracunaj_osnovnu_cijenu_gls(prosjecna_masa)
                gls_osnova = gls_po_paketu * broj_paketa

                overseas_ukupno_transport += ovs_trans
                gls_simulirano_ukupno += gls_osnova

                rezultati.append({
                    "Pošiljka ID": row.get("Shipment ID", idx + 1),
                    "Broj paketa": broj_paketa,
                    "Masa (kg)": masa,
                    "Poštanski broj": pbr,
                    "Stvarni Overseas Transport (€)": round(ovs_trans, 2),
                    "Simulirani GLS Transport (€)": round(gls_osnova, 2),
                    "Razlika (Overseas vs GLS €)": round(ovs_trans - gls_osnova, 2),
                })

            res_df = pd.DataFrame(rezultati)

            st.markdown("### 📊 Rezultat usporedbe osnovnih cijena")
            c1, c2, c3 = st.columns(3)
            c1.metric("Stvarni Overseas Transport", f"{overseas_ukupno_transport:,.2f} €")
            c2.metric("Simulirani GLS Transport", f"{gls_simulirano_ukupno:,.2f} €")
            razlika = overseas_ukupno_transport - gls_simulirano_ukupno
            c3.metric(
                "Ukupna razlika",
                f"{abs(razlika):,.2f} €",
                delta="GLS povoljniji" if razlika > 0 else "Overseas povoljniji",
                delta_color="normal" if razlika > 0 else "inverse"
            )

            st.markdown("---")
            st.dataframe(res_df, use_container_width=True)
            st.download_button(
                "📥 Preuzmi izvještaj usporedbe (Excel)",
                to_excel(res_df),
                "usporedba_overseas_prema_gls.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
    else:
        st.warning("Format tablice nije prepoznat. Provjerite sadrži li datoteka GLS ili Overseas stupce.")
