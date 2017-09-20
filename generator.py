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

background = cv2.imread('./dist/img/background.png')
color = 0
font = cv2.FONT_HERSHEY_TRIPLEX
scale = 1
offset = 0
thick = 2

df = pd.read_csv('./src/data/data.csv')
length = df.shape[0]

def insertData(id, data):
    # Sei que isso é feio, mas não sei como salvar o qr em um buffer pro opencv ler
    qr = pyqrcode.create(f"OPN-{id}")
    qr.png(f"./dist/img/qrcode/id-{id}.png", scale=10)
    
    qrcode = cv2.imread(f"./dist/img/qrcode/id-{id}.png")
    
    new_background = cp.deepcopy(background)
    new_background[0:offset + qrcode.shape[0], 0:offset + qrcode.shape[1]] = qrcode

    # Adiciona as informações no cartão
    cv2.putText(new_background, f"{data['Nome da Instituição']}", (440, 140), font, 2, color, thickness=4)

    cv2.putText(new_background, f"Nome: {data['Nome do Assistido']}", (280, 220), font, scale, color, thickness=thick)
    cv2.putText(new_background, f"Sexo: {data['Sexo']}", (280, 260), font, scale, color, thickness=thick)
    cv2.putText(new_background, f"ID: {id}", (670, 260), font, scale, color, thickness=thick)
    cv2.putText(new_background, f"Idade: {data['Idade']}", (950, 260), font, scale, color, thickness=thick)

    cv2.putText(new_background, f"Calca: {data['Nº Calça']}", (30, 365), font, scale, color, thickness=thick)
    cv2.putText(new_background, f"Camista: {data['Nº Camiseta']}", (30, 395), font, scale, color, thickness=thick)
    cv2.putText(new_background, f"Sapato: {data['Nº Calçado']}", (30, 425), font, scale, color, thickness=thick)

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
