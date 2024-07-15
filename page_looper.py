import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import datetime
from multiprocessing import Process, Lock
import time


mutex = Lock()

def wrap(val: int) -> str:
    if val >= 10:
        return str(val)
    return "0" + str(val)


def get_filename() -> str:
    dt = datetime.datetime.now()
    return f"./data/out_{dt.year}_{wrap(dt.month)}_{wrap(dt.day)}.csv"

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
                "prix": float(re.findall("[0-9.]+", p.replace(",", "."))[0]),
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
    print("scraping", name)

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
            # print(name, i, len(data))
            data = data.drop_duplicates(subset="uid", keep="first")

            no_new_counter = 0 if len(data) > last_length else no_new_counter + 1
            if no_new_counter > 5:
                break

    except Exception as e:
        print(e)

    data = data.drop_duplicates(subset="uid")

    with mutex:
        print(name, len(data), "annonces", i, "pages")

        try:
            data2 = pd.read_csv(get_filename(), sep=";", index_col=0)
            data = pd.concat([data2, data]).drop_duplicates("uid")
        except:
            pass
        
        data.to_csv(get_filename(), sep=";", encoding="utf-8")
        
    return data


if __name__ == '__main__':

    start = time.time()

    brands = [
        "tudor", "rolex", "omega", "tissot", "breitling",
        "patekphilippe", "jaegerlecoultre", "seiko", "cartier",
        "audemarspiguet", "tagheuer", "panerai", "hublot"
    ]
    processes = []
    for b in brands:
        p = Process(target=scrapp_brand, args=(b, 1500))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    end = time.time()
    data = pd.read_csv(get_filename(), sep=";", index_col=0)
    print(len(data), "annonces")
    print("done in", end-start, "s")
