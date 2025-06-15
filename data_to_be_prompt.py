import json

# clothes data
# Load clothes data from files
with open("clothes_data/all_clothing_types.json", "r") as f1:
    clothing_types = json.load(f1)

with open("clothes_data/all_material_data.json", "r") as f2:
    material_data = json.load(f2)

# Combine into a structured dictionary
clothes_data = {"types": clothing_types, "materials": material_data}
  
  