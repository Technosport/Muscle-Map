"""Assemble index.html (application autonome Muscle Map) à partir du gabarit et des tracés.

Usage : python build_app.py
"""
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

data_path = os.path.join(base_dir, "muscle_map_data.json")
if not os.path.exists(data_path):
    data_path = os.path.join(base_dir, "atlas_data.json")

template_path = os.path.join(base_dir, "app.template.html")
out_path = os.path.join(base_dir, "index.html")

print(f"Lecture des données depuis {os.path.basename(data_path)}...")
with open(data_path, "r", encoding="utf-8") as f:
    data = f.read()

print("Lecture du gabarit app.template.html...")
with open(template_path, "r", encoding="utf-8") as f:
    template = f.read()

assert "/*ATLAS_JSON*/" in template or "/*MUSCLE_MAP_DATA*/" in template

placeholder = "/*ATLAS_JSON*/" if "/*ATLAS_JSON*/" in template else "/*MUSCLE_MAP_DATA*/"
output = template.replace(placeholder, data)

with open(out_path, "w", encoding="utf-8") as f:
    f.write(output)

file_size_kb = os.path.getsize(out_path) / 1024
print(f"index.html généré avec succès ({file_size_kb:.1f} Ko, 100% autonome)")
