import streamlit as st
import xarray as xr
import numpy as np
import pandas as pd
import glob
import re
import pydeck as pdk

st.title("🌍 Carte climat raster (3 classes)")

# -----------------------------
# 🔹 fichiers
# -----------------------------
all_files = glob.glob("*.nc")

# -----------------------------
# 🔹 extract options
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
month = st.slider("Mois", 0, 11, 0)

# -----------------------------
# 🔹 filtrage fichiers
# -----------------------------
selected_files = [
    f for f in all_files
    if selected_tx in f and f"RWL-{selected_rwl}" in f
]

st.write(f"{len(selected_files)} fichiers")

# -----------------------------
# 🔹 fonction couleur 3 classes
# -----------------------------
def classify_colors(values):
    vmin = np.nanmin(values)
    vmax = np.nanmax(values)

    bins = np.linspace(vmin, vmax, 4)  # 3 classes

    colors = []
    for v in values:
        if np.isnan(v):
            colors.append([0, 0, 0, 0])
        elif v <= bins[1]:
            colors.append([200, 200, 200, 180])   # gris clair
        elif v <= bins[2]:
            colors.append([255, 200, 0, 180])     # jaune foncé
        else:
            colors.append([255, 0, 0, 180])       # rouge
    return colors

# -----------------------------
# 🔹 lecture data
# -----------------------------
@st.cache_data
def load_data(files, tx, month):
    dfs = []

    for f in files:
        try:
            ds = xr.open_dataset(f)
            if tx not in ds:
                continue

            data = ds[tx].isel(time=month).values
            lat = ds["lat"].values
            lon = ds["lon"].values

            lon2d, lat2d = np.meshgrid(lon, lat)

            values = data.ravel()

            df = pd.DataFrame({
                "lat": lat2d.ravel(),
                "lon": lon2d.ravel(),
                "value": values
            })

            df = df.dropna()

            # ✅ classification par fichier
            df["color"] = classify_colors(df["value"].values)

            dfs.append(df)

        except Exception as e:
            st.warning(f"Erreur fichier {f}")

    if dfs:
        return pd.concat(dfs)

    return pd.DataFrame(columns=["lat", "lon", "value", "color"])


df = load_data(selected_files, selected_tx, month)

# -----------------------------
# 🔹 calcul taille pixel réel
# -----------------------------
if not df.empty:
    # approx taille pixel en mètres (~3km chez toi)
    radius = 2000  # ajustable

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position='[lon, lat]',
        get_fill_color="color",
        get_radius=radius,
        pickable=True,
        opacity=0.8
    )

    view = pdk.ViewState(
        latitude=float(df["lat"].mean()),
        longitude=float(df["lon"].mean()),
        zoom=3
    )

    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view,
        tooltip={"text": "{value}"}
    ))

else:
    st.warning("Pas de données")
