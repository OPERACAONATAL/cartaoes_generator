/**
 * Só  lembrar  que  as  informações  fixas como logo e dados de texto devem ser
 * retiradas  após  o  layout definitivo. Isso permitirá que o programa processe
 * menos dados.
 */
'use strict';

const qr = require('qr-image');
const Jimp = require('jimp');
const fs = require('fs');
const pdfmake = require('pdfmake');
const pdfkit = require('pdfkit');
const csvdata = require('csvdata');
const ProgressBar = require('ascii-progress');
const async = require('async');

const default_cb = (err, res) => {
    if(err)
        throw(err);
}

/*  resoluções de uma folha a4  */
const a4_width_screen = 595, a4_heigth_screen = 842, a4_width_printer = 2480, a4_heigth_printer = 3508;
const font_title = Jimp.FONT_SANS_64_BLACK;
const font_regular = Jimp.FONT_SANS_32_BLACK;
const font_size = 32;
const logo_size = 280;
/*  proporções de um cartão para que caibam seis na impressão de uma folha  */
const height = Math.floor(a4_heigth_printer/3);
const width = Math.floor(a4_width_printer/2), first_col=30, second_col=(width/3)+50, third_col=(2*(width/3))+120;
const first_row = 200,
      second_row = first_row+font_size,
      third_row = 330,
      fourth_row = third_row+font_size,
      fifth_row = fourth_row+font_size,
      sixth_row = fifth_row+font_size,
      seventh_row = 500,
      eighth_row = seventh_row+font_size,
      nineth_row = eighth_row+font_size,
      tenth_row = nineth_row+font_size,
      eleventh_row = 670,
      twelfth_row = eleventh_row+font_size,
      thirteenth_row = twelfth_row+font_size,
      fourteenth_row = thirteenth_row+font_size,
      fifteenth_row = fourteenth_row+font_size,
      sixteenth_row = 920,
      seventeenth_row = sixteenth_row+font_size,
      eighteenth_row = seventeenth_row+font_size;

/*  Adiciona os dados no cartão */
const injectDataIntoCard = (background, data, index) => new Promise((resolve, reject) => {
    /*  Adiciona o QR Code gerado no cartão */
    Jimp.read(Buffer(qr.imageSync(`OPN-${index}`, { type: 'png' }))).then(qr_buffer => {
        /*  Como o QR Code vem com uma borda que atrapalha a primeira linha do
            cartão, ela deve ser removida primeiramente */
        qr_buffer.crop(12, 12, 120, 120).resize(logo_size, logo_size);
        return background.composite(qr_buffer, 5, 5);
        /*  Adiciona o nome da instituição  */
    }).then(image => {
        return Jimp.loadFont(font_title).then(font => {
            return image.print(font, 520, 70, data['Nome da Instituição']);
        }).catch(err => {
            throw (err);
        });
        /*  Adiciona as informações sobre o beneficiado */
    }).then(image => {
        return Jimp.loadFont(font_regular).then(font => {
            return image.print(font, 300, first_row, `Nome: ${data['Nome do Assistido']}`)
                .print(font, 300, second_row, `Sexo: ${data['Sexo']}`)
                .print(font, third_col, first_row, `ID: ${index}`)
                .print(font, third_col, second_row, `Idade: ${data['Idade']} anos`)
                .print(font, first_col, third_row, `Calça: ${data['Nº Calça']}`)
                .print(font, first_col, fourth_row, `Camiseta: ${data['Nº Camiseta']}`)
                .print(font, first_col, fifth_row, `Sapato: ${data['Nº Calçado']}`);
        }).catch(err => {
            throw (err);
        });
    }).then(card => {
        card.write(`./dist/img/OPN-${index}.png`, (err, resp) => {
            if(err)
                reject(err);
            else {
                resolve(resp);
                console.log('wrote');
            }
        });
    }).catch(console.log);
});

/*  carrega os dados dos beneficiados   */
csvdata.load('./src/data/data.csv').then(data => {
    Jimp.read('./dist/img/background.png', (err, background) => {
        const limit = 50;
        const bar = new ProgressBar({
            schema: ' [:bar] \n:current/:total \n:percent \n:elapseds :etas',
            // total: data.length
            total: limit
        });
        const result = data.slice(0, 50);

        if(result) {
            async.forEach(result, injectDataIntoCard, bar.tick());
        }
        injectDataIntoCard(background.clone(), element, index));
        bar.tick();
    });
});

/*  Salva os cartões em um arquivo pdf  */
/*
card.getBuffer(Jimp.MIME_PNG, (err, res) => {
    const page_specs = {
        size: [a4_width_printer, a4_heigth_printer]
    };
    const doc = new pdfkit(page_specs);

    doc.pipe(fs.createWriteStream('./dist/pdf/card.pdf'));
    doc.image(res, 0, 0);
    doc.image(res, width, 0);
    doc.image(res, 0, height);
    doc.image(res, width, height);
    doc.image(res, 0, 2 * height);
    doc.image(res, width, 2 * height);
    doc.end();
});
*/
