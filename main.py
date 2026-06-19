import streamlit as st
import xarray as xr
import numpy as np
import pandas as pd
import glob
import re
import pydeck as pdk

st.title("🌍 Carte climat géoréférencée")

# -----------------------------
# 🔹 fichiers
# -----------------------------
all_files = glob.glob("*.nc")

# -----------------------------
# 🔹 extraire options
# -----------------------------
tx_set, rwl_set = set(), set()

for f in all_files:
    m_tx = re.search(r"(TX\d+D)", f)
    m_rwl = re.search(r"RWL-(\d+)", f)

    if m_tx:
        tx_set.add(m_tx.group(1))
    if m_rwl:
        rwl_set.add(m_rwl.group(1))

selected_tx = st.selectbox("TXxD", sorted(tx_set))
selected_rwl = st.selectbox("RWL", sorted(rwl_set))
month = st.slider("Mois (0=Janvier)", 0, 11, 0)

# -----------------------------
# 🔹 filtrer fichiers
# -----------------------------
selected_files = [
    f for f in all_files
    if selected_tx in f and f"RWL-{selected_rwl}" in f
]

st.write(f"{len(selected_files)} fichiers chargés")

# -----------------------------
# 🔹 lecture
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

        except:
            st.warning(f"Erreur fichier {f}")

    if dfs:
        return pd.concat(dfs, ignore_index=True)

    return pd.DataFrame(columns=["lat", "lon", "value"])


df = load_data(selected_files, selected_tx, month)

# -----------------------------
# 🔹 carte pydeck (propre)
# -----------------------------
if not df.empty:

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position='[lon, lat]',
        get_radius=30000,   # taille point (adapter)
        get_fill_color='[255, 140, 0, 150]',
        pickable=True
    )

    view_state = pdk.ViewState(
        latitude=df["lat"].mean(),
        longitude=df["lon"].mean(),
        zoom=2,
        pitch=0,
    )

    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "{value}"}
    ))

else:
    st.warning("Pas de données")
