import os
import glob
import re
import shutil

base_dir = "."

for x in range(1, 51):
    prefix = f"TX{x}D"
    pattern = os.path.join(base_dir, f"{prefix}*.nc")
    files = glob.glob(pattern)

    if not files:
        continue

    tx_dir = os.path.join(base_dir, prefix)
    os.makedirs(tx_dir, exist_ok=True)

    for file in files:
        filename = os.path.basename(file)

        # ✅ regex corrigée (tiret et non underscore)
        match = re.search(r"socleOM-(.+?)-T_MF", filename)

        if match:
            nom = match.group(1)
        else:
            nom = "INCONNU"

        nom_dir = os.path.join(tx_dir, nom)
        os.makedirs(nom_dir, exist_ok=True)

        dest = os.path.join(nom_dir, filename)
        shutil.copy2(file, dest)

        print(f"{filename} → {nom}")