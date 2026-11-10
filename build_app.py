"""Assemble index.html (application autonome) à partir du gabarit et des tracés.

Usage : python build_app.py
"""
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

data_path = os.path.join(base_dir, "atlas_data.json")
template_path = os.path.join(base_dir, "app.template.html")
out_path = os.path.join(base_dir, "index.html")

with open(data_path, "r", encoding="utf-8") as f:
    data = f.read()
with open(template_path, "r", encoding="utf-8") as f:
    template = f.read()

assert "/*ATLAS_JSON*/" in template
with open(out_path, "w", encoding="utf-8") as f:
    f.write(template.replace("/*ATLAS_JSON*/", data))

print("index.html généré avec succès")
