import pandas as pd
import unidecode
import re
import os
import datetime
import sys


def analyze_mult_chats(input_folder, output_folder):
    chat_df = pd.DataFrame()
    for chat_record in os.listdir(input_folder):
        if chat_record.endswith('.txt'):
            print('Leyendo ' + chat_record)

            formatted_chat = leer_chat(input_folder + '/' + chat_record)

            chat_df_single = create_chat_df(formatted_chat, chat_record[:-4])

            chat_df = chat_df.append(chat_df_single)
            
            
    # chat_df.to_csv('to_analyze.csv', index=False)

    processed_chat, keyword_lists = chat_keywords(chat_df)

    # formato DF

    print('Ordenando resultados...')
    
    processed_chat['fecha'] = pd.to_datetime(processed_chat['fecha'], format='%d/%m/%y')
    processed_chat = processed_chat.sort_values(['fecha', 'hora'], ascending=False)

    del processed_chat['mensaje']

    # Ordenar
    first_columns = ['conversacion', 'fecha', 'hora', 'broker']
    column_names = first_columns + keyword_lists + ['mensaje_limpio']
    processed_chat = processed_chat[column_names]

    today = datetime.datetime.today().strftime('%d-%m-%Y')

    print('Guardando...')
    
    file_name = output_folder + '/' +'reporte_'+ today +'.csv'
    processed_chat.to_csv(file_name, index=False, sep='|', date_format='%d-%m-%Y')
    
    add_sep_header(file_name)


def analyze_chat(chat_record, output_folder):
    formatted_chat = leer_chat(chat_record)

    chat_df = create_chat_df(formatted_chat, None)

    processed_chat, keyword_lists = chat_keywords(chat_df)

    # formato DF
    print('Ordenando resultados...')
    processed_chat['fecha'] = pd.to_datetime(processed_chat['fecha'], format='%d/%m/%y')
    processed_chat = processed_chat.sort_values(['fecha', 'hora'], ascending=False)

    del processed_chat['mensaje']

    first_columns = ['fecha', 'hora', 'broker']
    
    column_names = first_columns + keyword_lists + ['mensaje_limpio']
    
    processed_chat = processed_chat[column_names]

    today = datetime.datetime.today().strftime('%d-%m-%Y')

    print('Guardando...')
    file_name = output_folder + '/' +'reporte_'+ chat_record[:-4] + '_' + today +'.csv'
    processed_chat.to_csv(file_name,index=False, sep='|', date_format='%d-%m-%Y')
    
    add_sep_header(file_name)

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


def create_chat_df(chat_list, chat_id):
    df = pd.DataFrame(chat_list)
    df.columns = ['mensaje']

    if chat_id is not None:
        df['conversacion'] = chat_id

    # usar para debugging
    # df.to_csv('to_analyze.csv', index=False)

    return df


def chat_keywords(df):
    # input: pandas DataFrame
                
    df['fecha']=df['mensaje'].str.extract('(\d\d/\d\d/\d\d)', expand=True)
    df['hora']=df['mensaje'].str.extract('(\d\d:\d\d:\d\d)', expand=True)
    df['broker']=df['mensaje'].str.extract('\]([^\]:]+?):', expand=True)
    # print(df.shape)

    print('Eliminando duplicados...')
    df['mensaje_limpio'] = df['mensaje'].str.extract(':\s(.*)', expand=True)
    df.drop_duplicates('mensaje_limpio', inplace=True)
    # print(df.shape)
    
    conjunto_lista_keyword = []
    
    print('Buscando palabras clave...')
    for lista_keyword in os.listdir('./listas'):
        if lista_keyword.endswith('.txt'):
            conjunto_lista_keyword.append(lista_keyword[:-4])
            df[lista_keyword[:-4]]=df['mensaje_limpio'].str.extract(crear_regex('./listas/'+lista_keyword, '|'), expand=True, flags=re.IGNORECASE)
    
    return (df,conjunto_lista_keyword)


def crear_regex(list_file, separador):
    words=[]
    with open(list_file, "r") as file:        
        for idx, ln in enumerate(file):
            to_append = ln.lstrip()
            to_append = to_append.rstrip()
            to_append = to_append.replace('\n','')
            to_append = to_append.replace(' ', '\s')
            words.append(to_append)

    new_list = [x+separador for x in words]
    
    # para intercalar
    # new_string = separador.join(words)
    # no lo uso porque necesito el ultimo \w

    my_regex = '(' + ''.join(new_list)[:-1] + ')' # eliminar ultimo OR

    # print(my_regex)

    return my_regex

def add_sep_header(file):
    with open(file, "r+") as f: s = f.read(); f.seek(0); f.write("sep=|\n" + s)

            
if __name__ == "__main__":
    # analyze_chat('_chat.txt')
    # analyze_mult_chats('../fuente', '../reportes')
    analyze_mult_chats(sys.argv[1], sys.argv[2])
    print('Reporte terminado')
