#!/bin/bash
python3 page_looper.py
python3 single_analysis.py
pyhton3 create_readme.py
git add . -f
git commit -m "dayly batch"
git push