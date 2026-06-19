import streamlit as st
import xarray as xr
import numpy as np
import pandas as pd
import glob
import re

st.title("🌍 Carte TXxD climat")

# -----------------------------
# 🔹 Charger tous les fichiers
# -----------------------------
all_files = glob.glob("*.nc")

# -----------------------------
# 🔹 Extraire TXxD et RWL
# -----------------------------
tx_set = set()
rwl_set = set()

for f in all_files:
    m_tx = re.search(r"(TX\d+D)", f)
    m_rwl = re.search(r"RWL-(\d+)", f)

    if m_tx:
        tx_set.add(m_tx.group(1))
    if m_rwl:
        rwl_set.add(m_rwl.group(1))

tx_list = sorted(tx_set)
rwl_list = sorted(rwl_set)

# -----------------------------
# 🔹 UI
# -----------------------------
selected_tx = st.selectbox("TXxD", tx_list)
selected_rwl = st.selectbox("RWL", rwl_list)
month = st.slider("Mois (0=Jan)", 0, 11, 0)

# -----------------------------
# 🔹 Filtrer fichiers
# -----------------------------
selected_files = [
    f for f in all_files
    if selected_tx in f and f"RWL-{selected_rwl}" in f
]

st.write(f"Fichiers utilisés : {len(selected_files)}")

# -----------------------------
# 🔹 Lecture des données
# -----------------------------
@st.cache_data
def load_data(files, tx, month):
    dfs = []

    for f in files:
        try:
            ds = xr.open_dataset(f)

            if tx not in ds:
                continue

            data = ds[tx].isel(time=month)

            lat = ds["lat"].values
            lon = ds["lon"].values

            lon2d, lat2d = np.meshgrid(lon, lat)

            df = pd.DataFrame({
                "lat": lat2d.ravel(),
                "lon": lon2d.ravel(),
                "value": data.values.ravel()
            })

            df = df.dropna()

            dfs.append(df)

        except Exception as e:
            st.warning(f"Erreur : {f}")

    if dfs:
        df_all = pd.concat(dfs)

        # ✅ moyenne si plusieurs fichiers (important)
        df_all = df_all.groupby(["lat", "lon"], as_index=False).mean()

        return df_all

    return pd.DataFrame(columns=["lat", "lon", "value"])


df = load_data(selected_files, selected_tx, month)

# -----------------------------
# 🔹 Affichage carte
# -----------------------------
if not df.empty:
    st.map(df, latitude="lat", longitude="lon", size="value")
else:
    st.warning("Aucune donnée trouvée")
