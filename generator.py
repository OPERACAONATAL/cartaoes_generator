"""
    Pontos para serem melhorados:
    * Descobrir como salvar o QRcode em um tipo de buffer que o OpenCV leia
    * Descobrir como salvar a imagem gerada pelo OpenCV em buffer para que o PIL leia/ou
      descobrir como salvar em pdf pelo próprio OpenCV
    * Verificar as questões de resolução de cartões para as páginas de impressão
    * Gerar o background por essse programa e não o implementado em Node.js -- não é prioridade
    * Migrar tudo para Ruby
"""
import pyqrcode
import cv2
import pandas as pd
import copy as cp
from tqdm import tqdm
from PIL import Image
import os
import math
import re
import unidecode
from PyPDF2 import PdfFileMerger

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

a4_width = 595
a4_heigth = 842

df = pd.read_csv('./src/data/data.csv')
length = df.shape[0]


def removeAccent(src):
    # Verifica também se é "nan" senão retorna em branco
    if isinstance(src, float) and math.isnan(src):
        return ''
    else:
        # Por algum motivo em alguns casos em específico há geração de '?' nas strings, por isso o replace
        return unidecode.unidecode(str(src)).replace('?', '')

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
    middle = int(len(institution)/2)*6

    cv2.putText(new_background, institution, (550-middle, 130), font, scale, color, thickness=thick)
    cv2.putText(new_background, removeAccent(data['Nome do Assistido']), (400, 230), font, scale, color, thickness=thick)
    cv2.putText(new_background, removeAccent(data['Sexo']), (380, 260), font, scale, color, thickness=thick)
    cv2.putText(new_background, removeAccent(data['Idade']), (795, 260), font, scale, color, thickness=thick)
    cv2.putText(new_background, f"ID:{id}", (25, 280), font, 1.5, color, thickness=thick)

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

def insertDummy(id):
    qr = pyqrcode.create(f"OPN-{id}")
    qr.png(f"./dist/img/qrcode/id-{id}.png", scale=10)

    qrcode = cv2.imread(f"./dist/img/qrcode/id-{id}.png")
    qrcode = qrcode[crop: qrcode.shape[0], crop: qrcode.shape[1]]

    new_background = cp.deepcopy(background)
    new_background[y_offset:qrcode.shape[0] + y_offset, x_offset:qrcode.shape[1] + x_offset] = qrcode
    
    cv2.putText(new_background, f"ID:{id}", (25, 280), font, 1.5, color, thickness=thick)

    cv2.imwrite(f"./dist/img/card/OPN-{i}.png", new_background)

def exportToPDF(number, fileNames):
    images = [Image.open(f"./dist/img/card/{x}") for x in fileNames]

    width, heigth = images[0].size
    # Duas colunas e três linhas
    page_width = 2 * width
    page_heigth = 3 * heigth

    #width_border_proportion = 1
    #heigth_border_proportion = page_heigth/page_width

    # mais 20 nas dimensões porque é uma borda que a impressora não imprime em A4
    border = 30

    #width_border = math.ceil(width_border_proportion * border)
    #heigth_border = math.ceil(heigth_border_proportion * border)
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
    page_img.save(f"./dist/img/page/page-{number}.png", 'PNG', quality=100, dpi=(300, 300))
    
# https://stackoverflow.com/a/5967539/7092954
def natural_keys(text):
    return int(re.split('(\d+)', text)[1])

print('\n[1/6] Gerando background:\n')
#os.system('node background.js')

print('\n\n[2/6] Criando cartões:\n')
#for i in tqdm(range(0, length)):
#    insertData(i, df.ix[i])

print('\n[3/6] Criando cartões adicionais em branco:\n')
# Mitiue pediu para gerar dez cartões a mais
#for i in tqdm(range(length, length+10)):
#    insertDummy(i)

# Precisa ser altamente melhorado isso daqui, mas infelizmente as bibliotecas de pdf que encontrei não facilitam muito
# o serviço
# Ao mesmo tempo a complexidade dessa parte do código é 200% desnecessaria
print('\n[4/6] Exportando em páginas:\n')
imgPath = './dist/img/card/'
images = [x for x in os.listdir(imgPath) if x.endswith('.png')]
# Eu sei que é feio, mas é necessário com o tempo curto
images = [x.split('.')[0] for x in images]
images = sorted(images, key=natural_keys)
# Corrigindo agora
images = [f"{x}.png" for x in images]
counter = 0
# O step no range é de seis porque é o número de cartões por página
for i in tqdm(range(6, len(images), 6)):
    exportToPDF(counter, images[i-6:i])
    counter += 1

print('\n[5/6] Salvando as páginas em pdf:\n')
#os.system('ruby pagesToPDF.rb')
print('\n\n[6/6] Linkando em um único pdf:\n')

merger = PdfFileMerger()
pdfs = [x for x in os.listdir('./dist/pdf/') if x.endswith('.pdf')]
pdfs = sorted(pdfs, key=natural_keys)

#for pdf in tqdm(pdfs):
#    merger.append(open(f"./dist/pdf/{pdf}", 'rb'))

#with open('result.pdf', 'wb') as fout:
#    merger.write(fout)

print('\nPrograma finalizado\n')
