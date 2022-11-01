import requests
import json
import pandas as pd
from datetime import datetime
from time import sleep

# arquivo tipo estado
# obs campos
# https://www.tse.jus.br/++theme++justica_eleitoral/pdfjs/web/viewer.html?file=https://www.tse.jus.br/eleicoes/eleicoes-2022/arquivos/interessados/ea15-arquivo-de-acompanhamento-uf-1653934878111/@@download/file/TSE-EA15-Arquivo-de-acompanhamento-UF.pdf

# obter estados
estados = pd.read_excel("estados.xlsx")
estados.SiglaEstado = estados.SiglaEstado.str.lower()



# iteracoes codigo
n=0

iteracoes = 1 #numero de pesquisas no dia botar 150
sleep_entre_jobs = 1 # sleep no final, no dia botar 60

print("o programa vai rodar por "+    
    str(round((iteracoes*sleep_entre_jobs/60),2))+
    " Horas.")

df2 = pd.DataFrame()

while n < iteracoes:

    # gerar df de todos os estados
    for estado in estados.SiglaEstado:

            data = requests.get(
                    'https://resultados.tse.jus.br/oficial/ele2022/545/dados/'+estado+'/'+estado+'-c0001-e000545-v.json'
            )

            json_data = json.loads(data.content)

            lista = []

            for dic in json_data['abr'][0]['cand']:
                    if dic['seq'] in ['1','2']:
                            lista.append(dic)

            timestamp = datetime.now().strftime('%d_%m_%Y-%Hh%Mm%Ss')   

            df = pd.DataFrame(lista)
            df['timestamp'] = timestamp
            df['votos_apurados'] = json_data['abr'][0]['pea']
            df['UF'] = json_data['abr'][0]['cdabr']

            # concatenar ao df princial
            df2 = pd.concat([df2,df])
            
            # Salvar Json em txt
            arquivo = open('BaseJsonUF.txt','a')
            arquivo.write("Arquivo gerado as "+ timestamp + "\n")
            arquivo.write(str(json_data) + "\n")
        #     print("Operação concluída no arquivo " + arquivo.name)
            arquivo.close()

         
    df2.to_csv("baseuf/baseuf_"+timestamp+" "+"Estados"+".csv", sep=";")

    print('rodagem de ESTADOS as '+timestamp+' rodagem n'+str(n))
    n+=1

    sleep(sleep_entre_jobs)

