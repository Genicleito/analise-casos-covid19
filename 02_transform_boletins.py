#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import requests, os, datetime
import re


# In[2]:


refined_path = './boletins_sesab/refined/'
today = datetime.datetime.now().strftime("%Y-%m-%d")
print("Today:", today)


# In[3]:


base = refined_path + sorted(os.listdir(refined_path), reverse=True)[0] + "/01_extract/01_boletim.txt"
base_extracted_csv = base.replace(".txt", "_extracted_tab_acum_cases.csv")


# In[4]:


date_base = base.split("/")[-3]
print("Base", base, "Data da base", date_base)


# In[5]:


transform_path = './boletins_sesab/refined/' + date_base + "/02_transform/"


# In[6]:


if not os.path.exists(transform_path): os.mkdir(transform_path)


# In[7]:


sed_command = "sed -r 's/^[^[:alpha:]]+//g;/^Pagina/d;/^[[:blank:]]*$/d;/^[a-z]/d;/[a-z]/d;s/\.//g;/[A-Z]+ *\**[[:blank:]]+[[:digit:]]+[[:blank:]]*[[:digit:]]*[\,]*[[:digit:]]*$/d;/\)$/d;/\%/d;s/\,/\./g;s/ +/,/g;/^LACEN/d;/NUCLEO[^A-Z]+REGIONAL/d;s/ +\,/,/g'"


# In[8]:


os.system("iconv -f utf-8 -t ascii//TRANSLIT -c " + base + " | " + sed_command + " > " + base.replace(".txt", ".csv.part"))


os.system("iconv -f utf-8 -t ascii//TRANSLIT -c " + base + " | sed -r '/\,/d;/[a-z]/d;s/\".*[\"]*.*\"//g;s/^[^A-Z0-9]+//g;/^[^A-Z]*$/d;/^[A-Za-z]+/d;s/  +/\,/g;s/ +\,/\,/g' | sed -z 's/\\([[:digit:]]\\)[[:blank:]]*\\([A-Z]\\)/\\1,\\2/g' > " + base.replace(".txt", "_tabs_ativos_obitosmunres_obitosmunocor.csv"))


# In[11]:


header = ['municipio', 'confirmados_laboratorial', 'confirmados_clinico_epidemiologico', 
          'confirmados_teste_rapido', 'total_confirmados', 'aguardando_validacao_dos_municipios', 
          'porcentagem', 'populacao', 'coef_incidencia_100k_hab', 'qtd_dias_ultimo_caso'
         ]

f = open(base.replace(".txt", ".csv.part"))
arq = f.readlines()
f.close()


# In[13]:


new_file = [",".join(header) + "\n"]
j = -1
for i in range(len(arq)):
    # Ignorar as linhas que já foram adicionadas
    if i < j:
        continue
    line = arq[i].replace("\n", "")
    j = i
    # Verifica se a linha está quebrada
    if len(line.split(",")) != len(header):
        # Verifica se há números na linha (isso indica que há mais valores e apenas o nome do municipio quebrou)
        if not re.search("\d", line):
            line = line.replace(",", " ")
            j = i + 1
            # Enquanto a linha não estiver completa
            while((j < len(arq) - 1) and (not re.search("\d", arq[j]))):
                line += " " + arq[j].replace(",", " ")
                j += 1
            new_file[-1] = new_file[-1].split(",")[0] + " " + line.replace("\n", "").strip() + "," + ",".join(new_file[-1].split(",")[1:])
            new_file[-1] = re.sub(" +", " ", new_file[-1])
        else:
            # Foi deslocado para a segunda coluna partes do nome do município
            line = re.findall("^[^\d]+", line)[0].replace(",", " ") + "," + re.findall("\d.*$", line)[0]
            line = re.sub("[^A-z\.\,\d]+", " ", line)
    # Se i == j então é um append de uma linha nova, caso contrário foi feita a substituição de uma linha que ja existia
    if j == i: new_file.append(line.replace("\n", "") + "\n")


print("qtd_registros:", len(new_file))


os.system("rm -rf " + os.path.dirname(base) + "/*.part*")

f = open(base_extracted_csv, "w")
f.write('date,' + new_file[0]) # write header
for i in range(1, len(new_file)):
    line = re.sub(" +\,|\, +", ",", date_base + "," + new_file[i])
    f.write(line)
f.close()

df = pd.read_csv(base_extracted_csv)
df_full = pd.read_csv('cases-covid19-bahia.csv')
df_full = df_full.drop(labels=[x for x in df_full.columns if "_x" in x or "_y" in x], axis=1)
print("Shape DataFrame:", df.shape, " - Shape DataFrame full:", df_full.shape)

df_full = df_full[df_full['date'] != date_base]
print("df_full sem os registros com a data {} de execuções anteriores: {}".format(date_base, df_full.shape))

f = open(base.replace(".txt", "_tabs_ativos_obitosmunres_obitosmunocor.csv"))
arq = f.readlines()
f.close()

tuples = [
    (os.path.dirname(base) + '/01_boletim_extracted_tab_ativos.csv', 'date,id,municipio,total_ativos\n'),
    (os.path.dirname(base) + '/01_boletim_extracted_tab_obitos_munres.csv', 'date,id,municipio,total_obitos_munres\n'),
    (os.path.dirname(base) + '/01_boletim_extracted_tab_obitos_munocor.csv', 'date,id,municipio,total_obitos_munocor\n')
]

ids_tabs = []
j = 0
print("Escrevendo arquivo:", tuples[j][0])
f = open(tuples[j][0], 'w')
f.write(tuples[j][1]) # cabeçalho
f.write(date_base + "," + arq[0])
for i in range(1, len(arq)):
    f.write(date_base + "," + arq[i])
    if int(arq[i].split(",")[0]) < int(arq[i - 1].split(",")[0]):
        f.close()
        j += 1
        if j > 2:
            break
        print("Escrevendo arquivo:", tuples[j][0])
        f = open(tuples[j][0], 'w')
        f.write(tuples[j][1]) # cabeçalho

for i in range(len(tuples)):
    tmp = pd.read_csv(tuples[i][0]).drop('id', axis=1)
    print(df_full.shape)
    tmp = tmp[~ tmp['municipio'].str.contains('(^|[^A-z]+)TOTAL($|[^A-z]+)')]
    df = df.merge(tmp, on=['date', 'municipio'], how='left')

df = df.where(df.notna(), 0)

df.to_csv(transform_path + "boletim_sesab_" + date_base + ".csv", index=False)
print("Colunas salvas boletim full:", list(df_full.columns))
print("Colunas salvas boletim {}: {}".format(date_base, list(df_full.columns)))

df_full = df_full.append(df).drop(['novos_casos', 'novos_obitos', 'taxa_letalidade', 'total_recuperados'], axis=1)
df_full = df_full[~ df_full['municipio'].str.contains('(^|[^A-z]+)TOTAL($|[^A-z]+)')]

df_nomes_cidades = pd.read_csv("cidades_bahia_covid19.csv")

for i in range(df_nomes_cidades.shape[0]):
    exp = df_nomes_cidades['regex'].iloc[i]
    name = df_nomes_cidades['municipio'].iloc[i]
    df_full['municipio'] = df_full['municipio'].str.replace(exp, name)

def fill_gaps_between_dates(dataset, var):
    df = dataset.copy()
    df = df[df[var].notnull()]
    levels = list(df[var].unique())
    
    # Garante a transformação da data para o formato datetime
    df.date = pd.to_datetime(df.date, infer_datetime_format=True)

    df_without_gaps = pd.DataFrame()
    for level in levels:
        df_level = df[df[var] == level].sort_values(by='date')
        
        # Cria os indíces de acordo com o intervalo das datas
        date_range = pd.date_range(start=df_level['date'].iloc[0], end=df_level['date'].iloc[-1])
        # Atribui as datas como indíces do DataFrame
        df_level.index = pd.DatetimeIndex(df_level['date'])
        # Reindexa os indíces inserindo as datas faltantes nos gaps (todas as datas em date_range) e preenchendo esses campos com None
        df_level = df_level.reindex(labels=date_range, method=None)
        
        # A variável de data sem gaps será a que está nos indíces
        df_level = df_level.drop(["date"], axis=1)

        # Preenche os valores com NA criados a partir do método reindex
        for col in df_level.columns:
            # Verifica se não são variáveis como 'newCases' ou 'newDeaths'
            if col.startswith("new") or col.startswith("novo"):
                # Essas variáveis serão preenchidas com o valor 0 para as datas sem notificação
                df_level[col].fillna(value=0, inplace=True)
            else:
                # Campos serão preenchidos com o primeiro valor válido 
                df_level[col].ffill(inplace=True)
        # Reseta os indíces a números sequenciais e cria uma variável 'index' com as datas sem gaps
        df_level = df_level.reset_index()
        # Renomeia a coluna de 'index' para date
        df_level = df_level.rename(columns={'index': 'date'})
        # Adiciona as notificações dessa cidade ao DataFrame
        df_without_gaps = df_without_gaps.append(df_level, ignore_index=True) if not df_without_gaps.empty else df_level

    # Padroniza as datas
    df_without_gaps['date'] = df_without_gaps['date'].astype(str)
    return df_without_gaps

def create_new_cases(df):
    dfs = pd.DataFrame(columns=list(df.columns) + ['novos_casos'])
    for city in df['municipio'].unique():
        tmp = df[df['municipio'] == city].sort_values(by=['date'])
        new_cases = [tmp['total_confirmados'].iloc[0]]
        for i in range(1, tmp.shape[0]):
            new_cases.append(tmp['total_confirmados'].iloc[i] - tmp['total_confirmados'].iloc[i - 1])
        tmp['novos_casos'] = new_cases
        dfs = dfs.append(tmp)
    return dfs

df_full = create_new_cases(df_full)

def create_new_deaths(df):
    dfs = pd.DataFrame(columns=list(df.columns) + ['novos_obitos'])
    for city in df['municipio'].unique():
        tmp = df[df['municipio'] == city].sort_values(by=['date'])
        new_cases = [tmp['total_obitos_munres'].iloc[0]]
        for i in range(1, tmp.shape[0]):
            new_cases.append(tmp['total_obitos_munres'].iloc[i] - tmp['total_obitos_munres'].iloc[i - 1])
        tmp['novos_obitos'] = new_cases
        dfs = dfs.append(tmp)
    return dfs

df_full = create_new_deaths(df_full)

def create_mortality_rate(df):
    df['taxa_letalidade'] = (df['total_obitos_munres'] / df['total_confirmados'].where(df['total_confirmados'] != 0, 1) * 100).apply(lambda x: round(x, 2))
    df['taxa_letalidade'].where(df['taxa_letalidade'].notna(), 0)
    return df

df_full = create_mortality_rate(df_full)

def create_recovered(df):
    df['total_recuperados'] = df['total_confirmados'] - df['total_ativos'] - df['total_obitos_munres']
    return df

df_full = create_recovered(df_full)

d_cols = ['date', 'municipio', 'porcentagem', 'coef_incidencia_100k_hab', 'taxa_letalidade']
for col in df_full.columns:
    if col not in d_cols:
        df_full[col] = df_full[col].astype(int)


print("Base de dados completa com informações do último boletim:", df_full.shape)

os.system("cp -p cases-covid19-bahia.csv cases-covid19-bahia.csv.bkp")
df_full.to_csv('cases-covid19-bahia.csv', index=False)

os.system("rm -rf " + base.replace(".txt", "_tabs_ativos_obitosmunres_obitosmunocor.csv"))

