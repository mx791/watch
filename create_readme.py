import pandas as pd
import plotly.express as px
import os
import datetime
from utils import listdir_nohidden


theme = "plotly_white"

files = listdir_nohidden("./data")
sizes = []
names = []

for f in reversed(list(files)):
    df = pd.read_csv(f"./data/{f}", sep=";")
    sizes.append(len(df))
    names.append(f)

f = px.bar(
    x=names, y=sizes, template=theme,
    title="Nombre d'annonces"
).update_layout(xaxis_title="", yaxis_title="", width=1000)
f.write_image("./out/count_per_day.jpeg", format="jpeg")

name = os.listdir("./data")[0]

txt = f"""
## Données
![image](./out/count_per_day.jpeg)

## Analyse des dernières données
Nom du dernier fichier: {name}
![image](./out/count_per_brand.jpeg)
![image](./out/count_per_name.jpeg)
![image](./out/avg_price_per_name_desc.jpeg)
![image](./out/avg_price_per_name_asc.jpeg)

## Détails des marques
|Marque|Nombre d'annonces|Prix moyen|Prix max|Prix median|
|------|-----------------|----------|--------|-----------|
"""

aggregated = df.groupby("brand").aggregate({"uid": "count", "prix": ["mean", "max", "median", "std"]})
for i in range(len(aggregated)):
    txt += f"|{aggregated.index[i]}|{aggregated["uid"].values[i][0]}|{int(aggregated["prix"].values[i][0])} €|{int(aggregated["prix"].values[i][1])} €|{int(aggregated["prix"].values[i][2])} €| \n"


txt += """
## Détails des modèles
Nom du modèle|Nombre d'annonces|Prix moyen|Prix median|
|-------------|-----------------|----------|-----------|
"""
aggregated = df.groupby("name").aggregate({
    "uid": "count", "prix": ["mean", "median", "std"], "brand": "first"
}).sort_values(("uid", "count"), ascending=False)[0:30]
for i in range(len(aggregated)):
    txt += f"|{aggregated.index[i]}|{aggregated["uid"].values[i][0]}|{int(aggregated["prix"].values[i][0])} €|{int(aggregated["prix"].values[i][1])} €| \n"

open("./README.md", "w+").write(txt)