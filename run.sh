#/bin/bash

echo "Extraindo dados do site da SESAB..."
python3 01_extract_boletins.py

# Obtendo último arquivo salvo
repo_path=~/boletins_sesab/
raw_path=./boletins_sesab/raw/
last_boletim_path=./boletins_sesab/last_boletim/
last_file=$(for f in `ls -lt $raw_path`; do echo $f; done | grep ".pdf" | head -n 1)
dt_last_file=$(date -d $(date -r $last_boletim_path$last_file +"%Y-%m-%d") +%s)
dt_final_file=$(date -d $(date -r cases-covid19-bahia.csv +"%Y-%m-%d") +%s)
dt_now=$(date -d $(date +"%Y-%m-%d") +"%s")

#if [ $dt_last_file -eq $dt_now -a $dt_final_file -eq $dt_now ]
if [ $(sed -n "/$(date +"%Y-%m-%d")/p" $repo_path/cases-covid19-bahia.csv | wc -l) -ne 0 ]
then
	echo "Dados já estão atualizados!"
	echo "Data de modificação do ultimo boletim: $(date -r $last_boletim_path$last_file)"
	echo "Data de atualização dos dados em CSV: $(date -r cases-covid19-bahia.csv)"
else
	echo "Novo arquivo encontrado: $last_file | Date: $(date -r $last_boletim_path$last_file +"%Y-%m-%d")";

	echo "Transformando dados..."
	python3 02_transform_boletins.py

	echo "Gerando análise..."
	jupyter nbconvert --ExecutePreprocessor.timeout=None --to notebook --execute --inplace 03_analysis.ipynb

	echo "Gerando html..."
	jupyter nbconvert --to html 03_analysis.ipynb
	python3 hide_input_cells_notebook_html.py
	rm -rf 03_analysis.html
fi

