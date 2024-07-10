import os


def listdir_nohidden(path: str):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f