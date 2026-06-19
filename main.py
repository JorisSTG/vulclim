import streamlit as st
import xarray as xr
import os
import re
import glob
import numpy as np
import pandas as pd

st.title("🌍 Visualisation TXxD")

base_dir = "."

# -----------------------------
# 🔹 Extraction des options
# -----------------------------
tx_values = sorted([d for d in os.listdir(base_dir)
                    if d.startswith("TX") and d.endswith("D")])

selected_tx = st.selectbox("Choisir TXxD", tx_values)

# Trouver tous les fichiers du TX choisi
pattern = os.path.join(base_dir, selected_tx, "*", "*.nc")
files = glob.glob(pattern)

# Extraire RWL disponibles
rwl_set = set()
for f in files:
    m = re.search(r"RWL-(\d+)", f)
    if m:
        rwl_set.add(m.group(1))

rwl_list = sorted(list(rwl_set))
selected_rwl = st.selectbox("Choisir RWL", rwl_list)

# Mois (0-11)
selected_month = st.slider("Choisir mois (index)", 0, 11, 0)

# -----------------------------
# 🔹 Chargement des données
# -----------------------------
@st.cache_data
def load_data(files, tx, rwl, month):
    all_data = []

    for f in files:
        if f"RWL-{rwl}" not in f:
            continue

        try:
            ds = xr.open_dataset(f)

            var_name = tx  # ex: TX40D
            if var_name not in ds:
                continue

            data = ds[var_name].isel(time=month)

            lat = ds["lat"].values
            lon = ds["lon"].values

            # meshgrid
            lon2d, lat2d = np.meshgrid(lon, lat)

            df = pd.DataFrame({
                "lat": lat2d.ravel(),
                "lon": lon2d.ravel(),
                "value": data.values.ravel()
            })

            df.dropna(inplace=True)

            all_data.append(df)

        except Exception as e:
            st.warning(f"Erreur fichier {f}: {e}")

    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame(columns=["lat", "lon", "value"])


df = load_data(files, selected_tx, selected_rwl, selected_month)

# -----------------------------
# 🔹 Affichage carte
# -----------------------------
st.write(f"Points affichés: {len(df)}")

if not df.empty:
    st.map(df, latitude="lat", longitude="lon", size="value")
else:
    st.warning("Aucune donnée trouvée")
