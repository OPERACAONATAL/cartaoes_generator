"""
    Pontos para serem melhorados:
    * Descobrir como salvar o QRcode em um tipo de buffer que o OpenCV leia
    * Descobrir como salvar a imagem gerada pelo OpenCV em buffer para que o PIL leia/ou
      descobrir como salvar em pdf pelo próprio OpenCV
    * Verificar as questões de resolução de cartões para as páginas de impressão
    * Gerar o background por essse programa e não o implementado em Node.js -- não é prioridade
"""
import pyqrcode
import cv2
import pandas as pd
import copy as cp
from tqdm import tqdm
from PIL import Image
from fpdf import FPDF
import os
import math
import re
import unidecode

background = cv2.imread('./dist/img/background.png')
color = 0
font = cv2.FONT_HERSHEY_TRIPLEX
scale = 1
x_offset = 5
y_offset = 5
thick = 2
crop = 20
elders = ['Cantinho Fraterno ', 'Helena Dornfeld']
# Feio mas 'funciona'
text = ['MESES', 'ANOS', 'ANO', 'MÊS']
exceptions = ['Cantinho Fraterno ', 'CEMEI Papa João Paulo II', 'ONG Formiga Verde', 'Salesianos']

pdf = FPDF(unit="mm", format='A4')

a4_width = 595
a4_heigth = 842

df = pd.read_csv('./src/data/data.csv')
length = df.shape[0]
#length = 15

def removeAccent(src):
    # Por algum motivo em alguns casos em específico há geração de '?' nas strings, por isso o strip
    return unidecode.unidecode(str(src)).strip('?')

def insertData(id, data):
    # Sei que isso é feio, mas não sei como salvar o qr em um buffer pro opencv ler
    qr = pyqrcode.create(f"OPN-{id}")
    qr.png(f"./dist/img/qrcode/id-{id}.png", scale=10)
    
    qrcode = cv2.imread(f"./dist/img/qrcode/id-{id}.png")
    
    # Corte as bordas em branco do qrcode
    qrcode = qrcode[crop: qrcode.shape[0], crop: qrcode.shape[1]]

    new_background = cp.deepcopy(background)
    new_background[y_offset:qrcode.shape[0] + y_offset, x_offset:qrcode.shape[1] + x_offset] = qrcode

    # Adiciona as informações no cartão
    institution = removeAccent(data['Nome da Instituição'])
    # 'Oito' é um constante encontrada empiricamente para converter em uma escala o tamanho da letra
    middle = int(len(institution)/2)*8
    cv2.putText(new_background, removeAccent(data['Nome do Assistido']), (400, 230), font, scale, color, thickness=thick)
    cv2.putText(new_background, removeAccent(data['Sexo']), (380, 260), font, scale, color, thickness=thick)
    cv2.putText(new_background, f"ID:{id}", (25, 280), font, 1.5, color, thickness=thick)
    cv2.putText(new_background, removeAccent(data['Idade']), (795, 260), font, scale, color, thickness=thick)

    cv2.putText(new_background, removeAccent(data['Nº Calça']), (130, 360), font, scale, color, thickness=thick)
    cv2.putText(new_background, removeAccent(data['Nº Camiseta']), (180, 390), font, scale, color, thickness=thick)
    cv2.putText(new_background, removeAccent(data['Nº Calçado']), (150, 425), font, scale, color, thickness=thick)

    # Como a ARCORDE não terá brinquedo nem lvro por questão do time das sacolinhas terem pedido para não colocarmos -- 
    # porque haverá um trabalho diferente com eles -- foi decidido que haverá nada no espaço no certão. E em que 
    # verificar porque NaN é um tipo de float e ao mesmo tempo é o dado atribuido ao campos sem valores em uma csv
    if data['Nome da Instituição'] == 'A.C.O.R.D.E.' or (isinstance(data['Idade'], float) and math.isnan(data['Idade'])):
        pass
    elif data['Nome da Instituição'] in elders:
         cv2.putText(new_background, "Fralda geriatrica", (30, 450), font, scale, color, thickness=thick)
    # Se tiver texto na idade, significa que tem "meses"-- ou seja, bebês
    elif any(x in data['Idade'] for x in text) or int(data['Idade']) < 11:
        cv2.putText(new_background, "Brinquedo", (30, 455), font, scale, color, thickness=thick)
    # Caso que sobrou: pessoas que não são da ACORDE, nem idosas e tem mais de 12 anos.
    else:
        cv2.putText(new_background, "Livro", (30, 455), font, scale, color, thickness=thick)
    # Salva a imagem do cartão
    cv2.imwrite(f"./dist/img/card/OPN-{i}.png", new_background)

def exportToPDF(start, fileNames):
    images = [Image.open(f"./dist/img/card/{x}") for x in fileNames]

    width, heigth = images[0].size
    # Duas colunas e três linhas
    page_width = 2 * width
    page_heigth = 3 * heigth

    page_img = Image.new('RGB', (page_width, page_heigth), (255, 255, 255))
    x_offset = 0
    y_offset = 0

    for j in range(0, len(images), 2):
        k = j
        for _ in range(0, 2):
            # Don't do this at home
            if(k < len(images)):
                page_img.paste(images[k], (x_offset, y_offset))
                x_offset += width
                k += 1
        x_offset = 0
        y_offset += heigth

    # Verificar como transformar em um buffer
    page_img = page_img.resize((a4_width, a4_heigth), Image.ANTIALIAS)
    page_img.save('./dist/img/page.png', 'PNG', quality=100)
    pdf.add_page()
    pdf.image('./dist/img/page.png', x=2, y=2)

def atoi(text):
    return int(text)

# https://stackoverflow.com/a/5967539/7092954
def natural_keys(text):
    return atoi(re.split('(\d+)', text)[1])

print("\nCriando cartões:\n")
for i in tqdm(range(0, length)):
# Como algumas instituições não entregaram seus dados a tempo, por ora não geraremos cartões delas -- mas é importante que seu id se mantenha
    if not df.ix[i]['Nome da Instituição'] in exceptions:
         insertData(i, df.ix[i])

# Precisa ser altamente melhorado isso daqui, mas infelizmente as bibliotecas de pdf que encontrei não facilitam muito o serviço
# Ao mesmo tempo a complexidade dessa parte do código é 200% desnecessaria
print("\nExportando para pdf:\n")
imgPath = './dist/img/card/'
images = [x for x in os.listdir(imgPath) if x.endswith('.png')]
# Eu sei que é feio, mas é necessário com o tempo curto
images = [x.split('.')[0] for x in images]
images = sorted(images, key=natural_keys)
# Corrigindo agora
images = [f"{x}.png" for x in images]
# O step no range é de seis porque é o número de cartões por página
for i in tqdm(range(6, len(images), 6)):
    exportToPDF(i, images[i-6:i])
pdf.output('cartoes.pdf', "F")
print('\n')
