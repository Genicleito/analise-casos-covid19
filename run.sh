#/bin/bash

echo "Extraindo dados do site da SESAB..."
python3 01_extract_boletins.py

echo "Transformando dados..."
python3 02_transform_boletins.py

echo "Gerando análise..."
jupyter nbconvert --to notebook --execute --inplace 03_analysis.ipynb

echo "Gerando html..."
jupyter nbconvert --to html 03_analysis.ipynb
python3 hide_input_cells_notebook_html.py
rm -rf 03_analysis.html
