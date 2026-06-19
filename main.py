import streamlit as st
import xarray as xr
import numpy as np
import pandas as pd
import glob
import re
import pydeck as pdk

st.title("🌍 Carte climat (par endroit)")

# -----------------------------
# 🔹 fichiers
# -----------------------------
all_files = glob.glob("*.nc")

# -----------------------------
# 🔹 extraction des métadonnées
# -----------------------------
info = []

for f in all_files:
    m_tx = re.search(r"(TX\d+D)", f)
    m_rwl = re.search(r"RWL-(\d+)", f)
    m_loc = re.search(r"FR-([^_]+)", f)

    if m_tx and m_rwl and m_loc:
        info.append({
            "file": f,
            "tx": m_tx.group(1),
            "rwl": m_rwl.group(1),
            "loc": m_loc.group(1)
        })

df_info = pd.DataFrame(info)

# -----------------------------
# 🔹 UI (ordre demandé)
# -----------------------------
loc_list = sorted(df_info["loc"].unique())
selected_loc = st.selectbox("Endroit", loc_list)

df_loc = df_info[df_info["loc"] == selected_loc]

tx_list = sorted(df_loc["tx"].unique())
selected_tx = st.selectbox("TXxD", tx_list)

df_tx = df_loc[df_loc["tx"] == selected_tx]

rwl_list = sorted(df_tx["rwl"].unique())
selected_rwl = st.selectbox("RWL", rwl_list)

mode = st.selectbox("Mode", ["Mensuel", "Annuel"])

month = 0
if mode == "Mensuel":
    month = st.slider("Mois (0=Janvier)", 0, 11, 0)

# -----------------------------
# 🔹 filtrer fichiers
# -----------------------------
selected_files = df_tx[df_tx["rwl"] == selected_rwl]["file"].tolist()

st.write(f"{len(selected_files)} fichier(s)")

# -----------------------------
# 🔹 classification couleurs
# -----------------------------
def classify_colors(values):
    vmin = np.nanmin(values)
    vmax = np.nanmax(values)

    bins = np.linspace(vmin, vmax, 4)

    colors = []
    for v in values:
        if np.isnan(v):
            colors.append([0, 0, 0, 0])
        elif v <= bins[1]:
            colors.append([200, 200, 200, 180])  # gris clair
        elif v <= bins[2]:
            colors.append([255, 200, 0, 180])    # jaune
        else:
            colors.append([255, 0, 0, 180])      # rouge
    return colors

# -----------------------------
# 🔹 lecture NetCDF
# -----------------------------
@st.cache_data
def load_data(files, tx, mode, month):
    dfs = []

    for f in files:
        try:
            ds = xr.open_dataset(f)

            if tx not in ds:
                continue

            var = ds[tx]

            if mode == "Annuel":
                data = var.sum(dim="time").values
            else:
                data = var.isel(time=month).values

            lat = ds["lat"].values
            lon = ds["lon"].values

            lon2d, lat2d = np.meshgrid(lon, lat)

            values = data.ravel()

            df = pd.DataFrame({
                "lat": lat2d.ravel(),
                "lon": lon2d.ravel(),
                "value": values
            }).dropna()

            # ✅ classification PAR FICHIER (donc PAR ENDROIT)
            df["color"] = classify_colors(df["value"].values)

            dfs.append(df)

        except Exception as e:
            st.warning(f"Erreur fichier {f}")

    if dfs:
        return pd.concat(dfs)

    return pd.DataFrame(columns=["lat", "lon", "value", "color"])


df = load_data(selected_files, selected_tx, mode, month)

# -----------------------------
# 🔹 affichage carte
# -----------------------------
if not df.empty:

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position='[lon, lat]',
        get_fill_color="color",
        get_radius=2000,  # ~taille pixel (à ajuster)
        pickable=True,
        opacity=0.9
    )

    view = pdk.ViewState(
        latitude=float(df["lat"].mean()),
        longitude=float(df["lon"].mean()),
        zoom=5,
    )

    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view,
        tooltip={"text": "Valeur: {value}"}
    ))

else:
    st.warning("Pas de données")
