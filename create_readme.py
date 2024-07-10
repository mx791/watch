import pandas as pd
import plotly.express as px
import plotly
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
"""

open("./README.md", "w+").write(txt)