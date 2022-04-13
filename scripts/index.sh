conda activate rents
python 01_get_data.py
python 02_postcode.py
python 03_cleaning.py
python 04_calculation.py
git add .
git commit -m "update"
git push
cd ..
cd app
git add .
git commit -m "update"
git push