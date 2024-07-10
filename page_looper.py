import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import datetime

def get_filename() -> str:
    dt = datetime.datetime.now()
    return f"./data/out_{dt.year}_{dt.month}_{dt.day}.csv"

def sanitize(txt: str) -> str:
    return txt.replace("\n", "").replace('\\xa', "").replace("\u202f", "").replace("\xa0", "")


def process_body(r) -> pd.DataFrame:
    body = BeautifulSoup(r.content, 'html.parser')
    results = body.find_all("div", {"class": "article-item-container"})
    out = []
    for art in results:
        try:
            texts = art.find("div", {"class": "d-flex align-items-center"})
            p = sanitize(art.find("div", {"class": "m-b-1"}).find("div", {"class": "text-bold"}).text)
            out.append({
                "name":  sanitize(texts.text),
                "reference":  sanitize(art.find("div", {"class": "m-b-2"}).text),
                "prix": re.findall("[0-9]+", p)[0],
                "currency": p.replace(str(re.findall("[0-9]+", p)[0]), ""),
                "uid": art.find("a").get("href"),
                "country": sanitize(art.find("span", {"class": "text-uppercase"}).text),
                "created_at": datetime.datetime.now()
            })
        except Exception:
            pass
    
    return pd.DataFrame({
        col: [out[i][col] for i in range(len(out))] for col in out[0]
    })


def scrapp_brand(name: str, max=250) -> pd.DataFrame:

    data = None
    try:
        data = pd.read_csv(get_filename(), sep=";", index_col=0)
    except Exception:
        pass

    try:
        no_new_counter = 0
        for i in range(max):
            url = f"https://www.chrono24.fr/{name}/index-{i}.htm?goal_suggest=1"
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'})
            
            if r.status_code != 200:
                break

            results = process_body(r)
            results["brand"] = results["uid"].apply(lambda x: name)

            last_length = 0 if data is None else len(data)
            data = results if data is None else pd.concat([data, results])
            print(i, len(data))
            data = data.drop_duplicates(subset="uid", keep="first")
            
            data.to_csv(get_filename(), sep=";", encoding="utf-8")

            no_new_counter = 0 if len(data) > last_length else no_new_counter + 1
            if no_new_counter > 5:
                break

    except Exception as e:
        print(e)

    data = data.drop_duplicates(subset="uid")
    return data

brands = [
    "tudor", "rolex", "omega", "tissot", "breitling",
    "patekphilippe", "jaegerlecoultre", "seiko", "cartier",
    "audemarspiguet", "tagheuer", "panerai", "hublot"
]
for b in brands:
    print("---------")
    print(b)
    scrapp_brand(b, max=350)
