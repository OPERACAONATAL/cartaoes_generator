import pyqrcode
import cv2
import pandas as pd
import copy as cp
from tqdm import tqdm
from PyPDF2 import PdfFileWriter, PdfFileReader

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
    qr = pyqrcode.create('OPN-0')
    qr.png(f"./dist/img/qrcode/id-{id}.png", scale=10)
    
    qrcode = cv2.imread(f"./dist/img/qrcode/id-{id}.png")
    
    new_background = cp.deepcopy(background)
    new_background[0:offset + qrcode.shape[0], 0:offset + qrcode.shape[1]] = qrcode

    # Adiciona as informações no cartão
    cv2.putText(new_background, f"{data['Nome da Instituição']}", (440, 140), font, 2, color, thickness=4)

    cv2.putText(new_background, f"Nome: {data['Nome do Assistido']}", (280, 220), font, scale, color, thickness=thick)
    cv2.putText(new_background, f"Sexo: {data['Sexo']}", (280, 260), font, scale, color, thickness=thick)
    cv2.putText(new_background, f"ID: {id}", (950, 220), font, scale, color, thickness=thick)
    cv2.putText(new_background, f"Idade: {data['Idade']}", (950, 260), font, scale, color, thickness=thick)

    cv2.putText(new_background, f"Calca: {data['Nº Calça']}", (30, 365), font, scale, color, thickness=thick)
    cv2.putText(new_background, f"Camista: {data['Nº Camiseta']}", (30, 395), font, scale, color, thickness=thick)
    cv2.putText(new_background, f"Sapato: {data['Nº Calçado']}", (30, 425), font, scale, color, thickness=thick)

    # Salva a imagem do cartão
    cv2.imwrite(f"./dist/img/card/OPN-{i}.png", new_background)

def saveToPDF(index):
    output = PdfFileWriter()



print("Criando cartões:\n")
for i in tqdm(range(0, length)):
    insertData(i, df.ix[i])

print("Exportando para pdf:\n")
for i in tqdm(range(0, 6)):
    saveToPDF(i)
