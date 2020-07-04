#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests, os, datetime, re


# In[2]:


today = datetime.datetime.now().strftime("%Y-%m-%d")
today


# In[3]:


url = 'http://www.saude.ba.gov.br/temasdesaude/coronavirus/notas-tecnicas-e-boletins-epidemiologicos-covid-19/'
path = "./boletins_sesab/"


# In[4]:


r = requests.get(url)
r.close()


# In[5]:


boletins_page = r.text.split("Boletim Epidemiológico – COVID-19")
boletim_mais_recente = boletins_page[0].split("href=\"")[-1].split("\"")[0]
boletins_sesab = sorted([boletim_mais_recente] + [x.split("href=\"")[1].split("\"")[0] for x in boletins_page[1:]], reverse=True)
boletins_sesab


# In[6]:


if not os.path.exists(path):
    os.mkdir(path)
    os.mkdir(path + "raw/")
elif not os.path.exists(path + "raw/"):
    os.mkdir(path + "raw/")


# In[7]:


re.search("_[A-z]*\d{8,}.pdf", "_A20.pdf")


# In[8]:


ant_name = ""
for i, boletim in enumerate(boletins_sesab):
    if "BOLETIM_ELETRONICO_BAHIAN" in boletim:
        r = re.findall("\d+\_\d.*", boletim)
        if len(r) != 0:
            print("ALERT | Tratando boletim:", boletim)
            r = r[-1]
            s = r.replace("_", "")
            boletim = boletim.replace(r, s)
            print("\tBoletim tratado:", boletim)
        b_name = re.sub("__[A-Z]+", "__", boletim.split("/")[-1])
        b_name = re.sub("\-\d.pdf", ".pdf", b_name)
        if not re.search("_[A-z]*\d{8,}.pdf", b_name):
            data_ant = ant_name.split("_")[-1].replace(".pdf", "")
            print(b_name, data_ant)
            date_atual = (datetime.datetime.strptime(data_ant, "%d%m%Y") - datetime.timedelta(1)).strftime("%d%m%Y")
            print("ALERT | Adicionando data [{}] ao arquivo: {}".format(date_atual, b_name))
            b_name = b_name.replace(".pdf", "__" + date_atual + ".pdf")
            print("\tArquivo com a data:", b_name)
            
        print("[Info] - Baixando: {}".format(boletim))
        ant_name = b_name
        os.system("curl -C - " + boletim + " -o " + path + "raw/" + b_name)
#     else:
#         print("[Alert!] Ignorado link: {}".format(boletim))


# ## Código R para extrair as informações do PDF mais atual

# In[9]:


os.system("/usr/bin/Rscript ./extrat_text_pdf.r")

