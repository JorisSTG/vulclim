import os
import glob
import shutil

# Motif de recherche
pattern = "/cnrm/socle/DATA/INDICATEURS/*_T/TX*D/ensemble_indicators/TX*D*mon_RWL*TIMEavg*ENSq50.nc"

# Dossier de destination
destination_dir = "/cnrm/socle/USERS/saint-genesj/vulclim"

# Création du dossier destination s'il n'existe pas
os.makedirs(destination_dir, exist_ok=True)

# Recherche des fichiers
files = glob.glob(pattern)

print(f"{len(files)} fichiers trouvés")

# Copie des fichiers
for file_path in files:
    filename = os.path.basename(file_path)
    dest_path = os.path.join(destination_dir, filename)
    
    shutil.copy2(file_path, dest_path)  # copy2 conserve les métadonnées
    print(f"Copié : {file_path} -> {dest_path}")

print("✅ Copie terminée")
