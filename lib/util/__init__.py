import pandas as pd
import numpy as np
import os, re
import geopandas as gpd
import matplotlib.pyplot as plt
import bar_chart_race as bcr
from IPython import display
import datetime
from matplotlib.dates import DateFormatter

wcota_path = 'https://raw.githubusercontent.com/wcota/covid19br/master/cases-brazil-cities-time.csv.gz'
pop_path = 'extract_data_from_sesab/cidades_bahia_covid19.csv'
base_path = 'cases-covid19-bahia.csv.zip'
path_to_write_charts = "charts/"
# Fonte do shapefile: https://mapas.ibge.gov.br/bases-e-referenciais/bases-cartograficas/malhas-digitais
path_to_shapefile = 'shapefile_municipios_baciadojacuipe'
now = lambda: datetime.datetime.now()

time_start = now()
t_s = now()

dic_cities = {
    '^[^A-Z]*BAIXA GRANDE[^A-Z]*$': 'Baixa Grande',
    '^[^A-Z]*CAPELA DO ALTO ALEGRE[^A-Z]*$': 'Capela do Alto Alegre',
    '^[^A-Z]*CAPIM GROSSO[^A-Z]*$': 'Capim Grosso',
    '^[^A-Z]*GAVIÃO[^A-Z]*$': 'Gavião',
    '^[^A-Z]*GAVIAO[^A-Z]*$': 'Gavião',
    '^[^A-Z]*IPIRÁ[^A-Z]*$': 'Ipirá',
    '^[^A-Z]*IPIRA[^A-Z]*$': 'Ipirá',
    '^[^A-Z]*MAIRI[^A-Z]*$': 'Mairi',
    '^[^A-Z]*NOVA FÁTIMA[^A-Z]*$': 'Nova Fátima',
    '^[^A-Z]*NOVA FATIMA[^A-Z]*$': 'Nova Fátima',
    '^[^A-Z]*PÉ DE SERRA[^A-Z]*$': 'Pé de Serra',
    '^[^A-Z]*PE DE SERRA[^A-Z]*$': 'Pé de Serra',
    '^[^A-Z]*PINTADAS[^A-Z]*$': 'Pintadas',
    '^[^A-Z]*QUIXABEIRA[^A-Z]*$': 'Quixabeira',
    '^[^A-Z]*RIACHÃO DO JACUÍPE[^A-Z]*$': 'Riachão do Jacuípe',
    '^[^A-Z]*RIACHAO DO JACUIPE[^A-Z]*$': 'Riachão do Jacuípe',
    '^[^A-Z]*SÃO JOSÉ DO JACUÍPE[^A-Z]*$': 'São José do Jacuípe',
    '^[^A-Z]*SAO JOSE DO JACUIPE[^A-Z]*$': 'São José do Jacuípe',
    '^[^A-Z]*SERRA PRETA[^A-Z]*$': 'Serra Preta',
    '^[^A-Z]*VÁRZEA DA ROÇA[^A-Z]*$': 'Várzea da Roça',
    '^[^A-Z]*VARZEA DA ROCA[^A-Z]*$': 'Várzea da Roça',
    '^[^A-Z]*VÁRZEA DO POÇO[^A-Z]*$': 'Várzea do Poço',
    '^[^A-Z]*VARZEA DO POCO[^A-Z]*$': 'Várzea do Poço'
}

def get_today(type=None):
	# Data atual
	return now().strftime("%d-%m-%Y") if type == str else now()
today = get_today(str)

def start_timer():
    t_s = now()
    
def print_timer():
    print('Execution time:', now() - t_s)

def execution_time():
    print('Total execution time:', now() - time_start)

def create_mortality_rate(df, var_deaths='deaths', var_totalCases='totalCases'):
    tmp = df.copy()
    tmp['mortalityRate'] = (tmp[var_deaths] / tmp[var_totalCases].where(tmp[var_totalCases] != 0, 1) * 100).apply(lambda x: round(x, 2))
    tmp['mortalityRate'] = tmp['mortalityRate'].fillna(value=0)
    return tmp

def create_recovered(df):
    df_ = pd.DataFrame()
    for city in df['city'].unique():
        tmp = df[df['city'] == city]
        df_ = df_.append(tmp.assign(recoveredCases=np.where(tmp['totalCases'].shift(14) > tmp['totalCases'], 
                                                            (tmp['totalCases'] - tmp['deaths']).fillna(0).astype(int), 
                                                            (tmp['totalCases'].shift(14) - tmp['deaths']).fillna(0).astype(int)
                                                           ))
                        )
    return df_

def create_active(df):
    df_ = pd.DataFrame()
    for city in df['city'].unique():
        tmp = df[df['city'] == city]
        df_ = df_.append(tmp.assign(activeCases=(tmp['totalCases']-tmp['deaths']-tmp['recoveredCases']).astype(int)))
    return df_

def preprocessing(read_path=wcota_path, write_path=base_path, compression='infer', ret=True, exec_time=False):
	if exec_time: start_timer()
	df = pd.read_csv(wcota_path).query('state == "BA"')
	# df = df[df['state'] == 'BA']
	df['city'] = df['city'].replace(to_replace="/BA", value="", regex=True)
	df = df.sort_values(by=['date', 'city'])
	# display.display(df[['city']].assign(count=1).groupby('city').count().sort_values(by=['count'], ascending=False).reset_index().head(10))
	df = create_recovered(df)
	df = create_active(df)
	df = df.drop('country', axis=1, errors='ignore')
	pop_cities = pd.read_csv(pop_path)
	df = df.merge(pop_cities[['ibgeID', 'population']].drop_duplicates('ibgeID'), on='ibgeID', how='left')
	if write_path:
		# print(f'writing in [{write_path}]...')
		if compression != 'infer': write_path = write_path.replace('.csv', f'.{compression}')
		df.to_csv(write_path, index=False, compression=compression)
		if exec_time: print_timer()
		if ret: return df
	else:
		if exec_time: print_timer()
		return df
