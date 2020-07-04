def hide_input_cells_notebook_html(read_path, write_path):
    import re
    f = open(read_path, encoding='utf8')
    arq = f.readlines()
    f.close()

    insere = True
    c_open = 0
    c_close = 0
    f = open(write_path, encoding='utf8', mode='w')
    for x in arq:
        if x == "\n" or ((not "<div class=\"input\">" in x and not " output_stderr" in x) and insere):
            if "<title>" in x:
                x = "<title>Analysis of COVID-19 data from Bacia do Jacuípe</title>"
            f.write(re.sub("Out\[\d+\]\:", "", x))
        elif insere:
            insere = False
            c_open = 0
            c_close = 0
            if " output_stderr" in x:
                c_open = 1
        elif '<div' in x and insere == False:
            c_open += 1
        elif '</div' in x and insere == False:
            c_close += 1
        if c_open != 0 and c_open == c_close and insere == False:
            insere = True
    f.close()

hide_input_cells_notebook_html("03_analysis.html", "report_boletim_baciadojacuipe.html")
print("Notebook 03_analysis.ipynb salvo como HTML em report_boletim_baciadojacuipe.html")