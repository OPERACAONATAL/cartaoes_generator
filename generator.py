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
from pdfrw import PdfReader, PdfWriter
import os
import math
import re
import unidecode

background = cv2.imread('./dist/img/background.png')
color = 0
font = cv2.FONT_HERSHEY_TRIPLEX
scale = 1
x_offset = 25
y_offset = 5
thick = 2
crop = 30
elders = ['Cantinho Fraterno', 'Helena Dornfeld']

df = pd.read_csv('./src/data/data.csv')
length = df.shape[0]
# length = 15

def removeAccent(src):
    return unidecode.unidecode(str(src))

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
    cv2.putText(new_background, institution, (600-middle, 140), font, scale, color, thickness=thick)

    cv2.putText(new_background, removeAccent(data['Nome do Assistido']), (400, 230), font, scale, color, thickness=thick)
    cv2.putText(new_background, removeAccent(data['Sexo']), (380, 260), font, scale, color, thickness=thick)
    cv2.putText(new_background, f"ID:{id}", (30, 280), font, scale+1, color, thickness=thick)
    cv2.putText(new_background, removeAccent(data['Idade']), (1040, 260), font, scale, color, thickness=thick)

    cv2.putText(new_background, removeAccent(data['Nº Calça']), (130, 360), font, scale, color, thickness=thick)
    cv2.putText(new_background, removeAccent(data['Nº Camiseta']), (180, 390), font, scale, color, thickness=thick)
    cv2.putText(new_background, removeAccent(data['Nº Calçado']), (150, 425), font, scale, color, thickness=thick)

    if data['Nome da Instituição'] in elders:
         cv2.putText(new_background, "Fralda geriatrica", (30, 450), font, scale, color, thickness=thick)
    # Se tiver texto na idade, significa que tem "meses" -- ou seja, bebês
    elif isinstance(data['Idade'], str):
        cv2.putText(new_background, "Brinquedo", (30, 455), font, scale, color, thickness=thick)
    # Tem que verificar porque NaN é um tipo de float e ao mesmo tempo é o dado atribuido ao campos sem valores em uma csv
    elif not math.isnan(data['Idade']) and data['Idade'] < 12:
        cv2.putText(new_background, "Brinquedo", (30, 455), font, scale, color, thickness=thick)
    # Caso não seja idoso, ou criança, mas sim um adolescente -- ou a idade é um atributo vazio
    else:
        cv2.putText(new_background, "Livro", (30, 455), font, scale, color, thickness=thick)

    # Salva a imagem do cartão
    cv2.imwrite(f"./dist/img/card/OPN-{i}.png", new_background)

def exportToPDF(start):
    images = []
    for j in range(i, i + 6):
        if(j < length):
            images.append(Image.open(f"./dist/img/card/OPN-{j}.png"))

    width = images[0].size[0]
    height = images[0].size[1]
    # Duas colunas e três linhas
    page_width = 2 * width
    page_height = 3 * height

    page_img = Image.new('RGB', (page_width, page_height))
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
        y_offset += height

    a4_width = 595
    a4_heigth = 842
    page_img = page_img.resize((a4_width, a4_heigth), Image.ANTIALIAS)
    page_img.save(f"./dist/pdf/page{i}.pdf", "PDF", resolution=100.0)

print("\nCriando cartões:\n")
for i in tqdm(range(0, length)):
    insertData(i, df.ix[i])

# Precisa ser altamente melhorado isso daqui, mas infelizmente as bibliotecas de pdf que encontrei não facilitam muito o serviço
# Ao mesmo tempo a complexidade dessa parte do código é 200% desnecessaria
print("\nExportando para pdf:\n")
# O step no range é de seis porque é o número de cartões por página
for i in tqdm(range(0, length, 6)):
    exportToPDF(i)

# Mais um trecho de código que dói ver
print('\nLinkando os cartões em um único pdf:\n')
fpath = './dist/pdf/'
writer = PdfWriter()
files = [x for x in os.listdir(fpath) if x.endswith('.pdf')]
for fname in tqdm(sorted(files)):
    writer.addpages(PdfReader(os.path.join(fpath, fname)).pages)
writer.write("cartoes.pdf")
print("\n")
