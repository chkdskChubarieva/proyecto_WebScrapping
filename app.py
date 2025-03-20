# app.py
from flask import Flask, render_template, redirect, url_for, send_file
from bs4 import BeautifulSoup as bs
from datetime import datetime
from time import sleep
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

titulo_list  = []
fecha_list = []
contenido_list = []
precio_list = []
tipo_list = []
subtipo_list = []
departamento_list = []
id_list = []
celular_list = []
interruptor = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/info.html')
def info():
     
    return render_template('info.html')

@app.route('/info/iniciar')
def iniciar():
    global interruptor
    global pausa
    interruptor = True
    pausa = False

    opts = Options()
    opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.86 Safari/537.36")
    opts.add_argument('--start-maximized')
    driver = webdriver.Chrome(
             service=Service(ChromeDriverManager().install()),
            options=opts
            )
    driver.get('https://clasificados.lostiempos.com/inmuebles')

    driver.implicitly_wait(5)
    n_pagina = 1
    try:
        while n_pagina <= 30 and interruptor:
            n_anuncio = 1
            while n_anuncio <= 30 and interruptor:
                if pausa:
                    sleep(1)
                    continue 
                if driver.find_elements("xpath", '//*[@id="panel-bootstrap-region-avisos"]/div/div[3]/div[1]/div/div/div/div[2]/div[%(n_anuncio)d]/div[6]/div[1]/span/a'% {"n_anuncio": n_anuncio}):
                    driver.find_element("xpath", '//*[@id="panel-bootstrap-region-avisos"]/div/div[3]/div[1]/div/div/div/div[2]/div[%(n_anuncio)d]/div[6]/div[1]/span/a'% {"n_anuncio": n_anuncio}).click()
                    html_anuncio = driver.page_source
                    soup_anuncio = bs(html_anuncio, 'html')
                    titulo = soup_anuncio.find('div',{'class':'block-inner clearfix'}).find('h2',{'class':'pane-title block-title'}).text

                    fecha = soup_anuncio.find('div',{'class':'date-submit'}, ).text.split(':')[1].strip()

                    contenido = soup_anuncio.find('div',{'class':'field field-name-body field-type-text-with-summary field-label-hidden view-mode-inmueble'}).find('p').text

                    if driver.find_elements("xpath",'//*[@class="nodo-precio"]'):
                        precio = soup_anuncio.find('div',{'class':'nodo-precio'}).text
                        precio = precio.replace(" ", "")
                        if precio.find('$') != -1:
                            precio = precio.split('s')[1]
                    else:
                        precio = 'null'

                    tipo_inmueble = soup_anuncio.find('div',{'class':'field field-name-field-cat-in-tipo field-type-taxonomy-term-reference field-label-hidden view-mode-inmueble'}).find('span',{'class':'lineage-item lineage-item-level-0'}).text

                    subtipo = soup_anuncio.find('div',{'class':'field field-name-field-inmuebles-transaccion field-type-taxonomy-term-reference field-label-hidden view-mode-inmueble'}).find('span',{'class':'lineage-item lineage-item-level-0'}).text

                    departamento = soup_anuncio.find('div',{'class':'field field-name-field-taxo-ubicacion field-type-taxonomy-term-reference field-label-hidden view-mode-inmueble'}).find('span',{'class':'lineage-item lineage-item-level-0'}).text

                    id = soup_anuncio.find('section',{'class':'field field-name-field-codigo-w2p field-type-text field-label-inline clearfix view-mode-inmueble'}).find('div',{'class':'field-item even'}).text
                    try:
                        celular = soup_anuncio.find('div', {'class': 'field field-name-field-telefono field-type-text field-label-hidden view-mode-inmueble'}).find('div', {'class': 'field-item even'}).text
                    except:
                        celular = 'null'

                    print('Página: %(n_pagina)d \n'% {"n_pagina": n_pagina})
                    print('Anuncio: %(n_anuncio)d \n'% {"n_anuncio": n_anuncio})
                    print(titulo+'\n')
                    print(fecha+'\n')
                    print(contenido+'\n')
                    print(precio+'\n')
                    print(tipo_inmueble+'\n')
                    print(subtipo+'\n')
                    print(departamento+'\n')
                    print(id+'\n')
                    print(celular+'\n')

                    titulo_list.append(titulo)
                    fecha_list.append(fecha)
                    contenido_list.append(contenido)
                    precio_list.append(precio)
                    tipo_list.append(tipo_inmueble)
                    subtipo_list.append(subtipo)
                    departamento_list.append(departamento)
                    id_list.append(id)
                    celular_list.append(celular)

                    n_anuncio = n_anuncio + 1
                    driver.execute_script("window.history.go(-1)") #Volver a la página anterior
                else:
                    n_anuncio = n_anuncio + 1

            n_pagina = n_pagina + 1
            if interruptor:
                driver.find_element("xpath",'//*[@title="Ir a la página %(n_pagina)d"]'% {"n_pagina": n_pagina}).click()

    except (KeyboardInterrupt, NoSuchElementException, AttributeError):
        print("Se ha detenido el proceso Web Scrapping")

    return redirect(url_for('info'))


@app.route('/info/detener')
def detener():
    global interruptor
    interruptor = False
    return redirect(url_for('info'))

@app.route('/info/pausar')
def pausar():
    global pausa
    pausa = True
    return redirect(url_for('info'))

@app.route('/info/continuar')
def continuar():
    global pausa
    pausa = False
    return redirect(url_for('info'))

@app.route('/info/descargar', methods=['GET', 'POST'])
def descargar():
    col_titulo = pd.Series(titulo_list)
    col_fecha = pd.Series(fecha_list)
    col_contenido = pd.Series(contenido_list)
    col_precio = pd.Series(precio_list)
    col_tipo = pd.Series(tipo_list)
    col_subtipo = pd.Series(subtipo_list)
    col_dep = pd.Series(departamento_list)
    col_id = pd.Series(id_list)
    col_cel = pd.Series(celular_list)
    
    data = {'Titulo': col_titulo, 'Fecha': col_fecha, 'Contenido': col_contenido,
        'Precio': col_precio, 'Tipo': col_tipo, 'Subtipo': col_subtipo, 'Departamento': col_dep,
        'ID': col_id, 'Celular': col_cel}
    df_avisos = pd.DataFrame(data)

    fecha_actual = datetime.now().strftime("%d-%m-%Y") 

    nombre_archivo = 'avisos{}.xlsx'.format(fecha_actual)
    df_avisos.to_excel(nombre_archivo, sheet_name= 'datos', index=False)
    
    return send_file(nombre_archivo, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)