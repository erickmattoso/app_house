conda activate rents
python 01-get_data.py
python 02-coordinates.py
python 03-calculation.py
python 04-get_dates.py
python 05-cost_living.py
git add .
git commit -m "update"
git push
cd ..
cd app
git add .
git commit -m "update"
git push