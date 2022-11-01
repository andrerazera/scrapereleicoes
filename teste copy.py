import requests
import json
import pandas as pd
from datetime import datetime
from time import sleep

n=0

iteracoes = 10 #numero de pesquisas no dia botar 150
sleep_entre_jobs = 3 # sleep no final, no dia botar 60

print("o programa vai rodar por "+    
    str(round((iteracoes*sleep_entre_jobs/60),2))+
    " Horas.")

while n < iteracoes:

    timestamp = datetime.now().strftime('%d_%m_%Y-%Hh%Mm%Ss')   

    try:
        df_eleicao_old = df_eleicao.copy()
    except:
        df_eleicao_old = pd.DataFrame(columns=['Candidato', 'Nº de Votos', 'Porcentagem', 'timestamp'])


    data = requests.get(
        'https://resultados.tse.jus.br/oficial/ele2022/544/dados-simplificados/br/br-c0001-e000544-r.json')

    json_data = json.loads(data.content)

    candidato = []
    partido = []
    votos = []
    porcentagem = []

    for informacoes in json_data['cand']:
        
        if informacoes['seq'] in ['1', '2']:
            candidato.append(informacoes['nm'])
            votos.append(informacoes['vap'])
            porcentagem.append(informacoes['pvap'])
            
    df_eleicao = pd.DataFrame(list(zip(candidato, votos, porcentagem)), columns = [
        'Candidato', 'Nº de Votos', 'Porcentagem'
    ])

    df_eleicao['Nº de Votos'] = df_eleicao['Nº de Votos'].astype(int)
    df_eleicao['Porcentagem'] = df_eleicao['Porcentagem'].str.replace(",",".").astype(float)

    df_eleicao['timestamp'] = datetime.now().strftime('%d_%m_%Y-%Hh%Mm%Ss')

    df_eleicao_export = df_eleicao.join(df_eleicao_old,how='left',rsuffix='_old').drop('Candidato_old', axis=1)

    df_eleicao_export['Nº de Votos_diff'] = df_eleicao_export['Nº de Votos'] - df_eleicao_export['Nº de Votos_old']
    df_eleicao_export['Porcentagem_diff'] = df_eleicao_export['Porcentagem'] - df_eleicao_export['Porcentagem_old']



    try:
        df_eleicao_export['Nº de Votos_diff_%'] = df_eleicao_export['Nº de Votos_diff'].apply(lambda x: x / df_eleicao_export['Nº de Votos_diff'].sum())
    except ZeroDivisionError:
        df_eleicao_export['Nº de Votos_diff_%'] = 0



    file = 'base.xlsx'

    from openpyxl import load_workbook
    from openpyxl.utils.dataframe import dataframe_to_rows

        #Load existing sheet as it is
    book = load_workbook(file)
        #Rename fist empty sheet
    sheet = book['Planilha1']
    # sheet.title = 'base Eleicao'

        #Load dataframe into new sheet
    for row in dataframe_to_rows(df_eleicao_export, index=False, header=True):
        sheet.append(row)

    print('rodagem as '+timestamp+' rodagem n'+str(n))
    n+=1

    book.save(file)
    sleep(sleep_entre_jobs)


