from PyPDF2 import PdfFileMerger
import os
import re

def atoi(text):
    return int(text)

# https://stackoverflow.com/a/5967539/7092954
def natural_keys(text):
    return atoi(re.split('(\d+)', text)[1])

merger = PdfFileMerger()
pdfs = [x for x in os.listdir('./dist/pdf/') if x.endswith('.pdf')]
pdfs = sorted(pdfs, key=natural_keys)

for pdf in pdfs:
    merger.append(open(f"./dist/pdf/{pdf}", 'rb'))

with open('result.pdf', 'wb') as fout:
    merger.write(fout)
