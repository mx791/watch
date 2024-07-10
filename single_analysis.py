import pandas as pd
import plotly.express as px
import os
from utils import listdir_nohidden

name = list(listdir_nohidden("./data"))[0]
print(name)
data = pd.read_csv(f"./data/{name}", index_col=0, sep=";")
theme = "plotly_white"


count_per_brands = data["brand"].value_counts()
f = px.bar(
    x=count_per_brands.index, y=count_per_brands.values, template=theme,
    title="Nombre d'annonces par marque"
).update_layout(xaxis_title="", yaxis_title="", width=1000)
f.write_image("./out/count_per_brand.jpeg", format="jpeg")


data_ = data[~data["name"].str.lower().isin(data["brand"].unique())]
count_per_brands = data_["name"].value_counts()[0:25]

f = px.bar(
    y=list(reversed(count_per_brands.index)), x=list(reversed(count_per_brands.values)), template=theme,
    title="Modèles les plus présents",
).update_layout(
    xaxis_title="Nombre d'annonces", yaxis_title="", height=800, width=700, title_x=0.5
)
f.write_image("./out/count_per_name.jpeg", format="jpeg")



price_per_model = data[["name", "prix"]].groupby(by="name").mean().sort_values("prix", ascending=False)
f = px.bar(
    x=price_per_model.index[0:15], y=price_per_model["prix"].values[0:15], template=theme,
    title="Modèles les plus chers (par prix moyen)",
).update_layout(
    xaxis_title="", yaxis_title="", height=500, width=1200, title_x=0.5, 
).update_yaxes(type="log")

f.write_image("./out/avg_price_per_name_desc.jpeg", format="jpeg")


f = px.bar(
    x=price_per_model.index[-15:], y=price_per_model["prix"].values[-15:], template=theme,
    title="Modèles les moins chers (par prix moyen)",
).update_layout(
    xaxis_title="", yaxis_title="", height=500, width=1200, title_x=0.5, 
)
f.write_image("./out/avg_price_per_name_asc.jpeg", format="jpeg")