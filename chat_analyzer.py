import pandas as pd
import unidecode
import re


def analyze_chat(chat_record):

    formatted_chat = leer_chat(chat_record)

    df = pd.DataFrame(formatted_chat)
    df.columns = ['mensaje']

    # usar para debugging
    df.to_csv('to_analyze.csv', index=False)
                
    df['fecha']=df['mensaje'].str.extract('(\d\d/\d\d/\d\d)', expand=True)
    df['hora']=df['mensaje'].str.extract('(\d\d:\d\d:\d\d)', expand=True)
    df['broker']=df['mensaje'].str.extract('\]([^\]:]+?):', expand=True)
    print(df.shape)

    df['mensaje_limpio'] = df['mensaje'].str.extract(':\s(.*)', expand=True)
    df.drop_duplicates('mensaje_limpio', inplace=True)
    print(df.shape)
    
    # df['ofrecimientos']=df['mensaje_limpio'].str.extract('(ofre\w+)', expand=True, flags=re.IGNORECASE)
    df['ofrecimientos']=df['mensaje_limpio'].str.extract(crear_regex('lista_ofrecer.txt', '\w+|'), expand=True, flags=re.IGNORECASE)
    # df['requerimientos']=df['mensaje_limpio'].str.extract('(requier\w+|necesi\w+|busc\w+|solicit\w+)', expand=True, flags=re.IGNORECASE)
    df['requerimientos']=df['mensaje_limpio'].str.extract(crear_regex('lista_requerir.txt', '\w+|'), expand=True, flags=re.IGNORECASE)
    
    # reordenar
    del df['mensaje']
    df = df[['fecha', 'hora', 'broker', 'ofrecimientos', 'requerimientos', 'mensaje_limpio']]
    
    df.to_csv('output.csv',index=False)

def leer_chat(chat_record):
    chat = []
    with open(chat_record, "r", encoding="utf8") as file:
        for idx, ln in enumerate(file):
            corr_line = unidecode.unidecode(ln).replace('\n',' ')
            if corr_line.startswith("[") and not corr_line.startswith("[?]"):
                chat.append(corr_line)
            else:
                chat[len(chat)-1]+=corr_line
    return chat

#TODO: adaptar espacios en listas de palabras
def crear_regex(list_file, separador):
    words=[]
    with open(list_file, "r") as file:        
        for idx, ln in enumerate(file):
            words.append(ln.replace('\n',''))

    new_list = [x+separador for x in words]
    
    # para intercalar
    # new_string = separador.join(words)
    # no lo uso porque necesito el ultimo \w

    return '(' + ''.join(new_list)[:-1] + ')' # eliminar ultimo OR

            
if __name__ == "__main__":
    analyze_chat('_chat.txt')
