const Jimp = require('jimp');
const fs = require('fs');

const default_cb = (err, res) => {
    if (err)
        throw (err);
}

/*  resoluções de uma folha a4  */
const a4_width_screen = 595, a4_heigth_screen = 842, a4_width_printer = 2480, a4_heigth_printer = 3508;
const font_title = Jimp.FONT_SANS_64_BLACK;
const font_regular = Jimp.FONT_SANS_32_BLACK;
const font_size = 32;
const logo_size = 280;
/*  proporções de um cartão para que caibam seis na impressão de uma folha  */
const height = Math.floor(a4_heigth_printer / 3);
const width = Math.floor(a4_width_printer / 2), first_col = 30, second_col = (width / 3) + 50, third_col = (2 * (width / 3)) + 120;
const first_row = 200,
    second_row = first_row + font_size,
    third_row = 330,
    fourth_row = third_row + font_size,
    fifth_row = fourth_row + font_size,
    sixth_row = fifth_row + font_size,
    seventh_row = 500,
    eighth_row = seventh_row + font_size,
    nineth_row = eighth_row + font_size,
    tenth_row = nineth_row + font_size,
    eleventh_row = 670,
    twelfth_row = eleventh_row + font_size,
    thirteenth_row = twelfth_row + font_size,
    fourteenth_row = thirteenth_row + font_size,
    fifteenth_row = fourteenth_row + font_size,
    sixteenth_row = 920,
    seventeenth_row = sixteenth_row + font_size,
    eighteenth_row = seventeenth_row + font_size;
const line = new Jimp(width, 1, 0x000000FF, default_cb);
const column = new Jimp(1, height, 0x000000FF, default_cb);

/*  Gera a imagem de fundo padrão que será utilizada para todos os cartões  */
const background = new Promise((resolve, reject) => {
    new Jimp(width, height, 0xFFFFFFFF, (err, res) => {
        /*  Adiciona o logo */
        return Jimp.read('./src/img/logo.png').then(logo => {
            logo.resize(height, height).opacity(0.2);
            return res.composite(logo, 30, 0);
            /*  Adiciona o cabeçalho    */
        }).then(image => {
            return Jimp.loadFont(font_title).then(font => {
                return image.print(font, 430, 20, 'SACOLINHAS');
            }).catch(err => {
                throw (err);
            });
            /*  Adiciona as linhas e colunas    */
        }).then(image => {
            return image.composite(line, 0, 290)
                .composite(line, 0, sixth_row + font_size + 5)
                .composite(line, 0, tenth_row + font_size + 5)
                .composite(line, 0, fifteenth_row + 100)
                .composite(line, 0, 0)
                .composite(line, 0, height - 1)
                .composite(column, 0, 0)
                .composite(column, width - 1, 0);
            /*  Adiciona o texto em regular */
        }).then(image => {
            return Jimp.loadFont(font_regular).then(font => {
                return image.print(font, 290, first_row, 'Nome:')
                    .print(font, 290, second_row, 'Sexo:')
                    .print(font, 700, second_row, 'Idade:')
                    .print(font, first_col, third_row, 'Calça:')
                    .print(font, first_col, fourth_row, 'Camiseta:')
                    .print(font, first_col, fifth_row, 'Sapato:')
                    .print(font, second_col, third_row, 'Cueca/calcinha')
                    .print(font, second_col, fourth_row, 'Meias')
                    .print(font, second_col, fifth_row, 'Guloseima')
                    .print(font, third_col, third_row, 'Xampu')
                    .print(font, third_col, fourth_row, 'Sabonete')
                    .print(font, third_col, fifth_row, 'Escova de dente')
                    .print(font, third_col, sixth_row, 'Creme dental')
                    .print(font, first_col, seventh_row, 'Locais: CAEP UFSCAR ou CAASO - USP nos dias 25, 26, 27, 30 e 31/10')
                    .print(font, first_col, eighth_row, 'Horários: 12h às 14h e das 18h às 19h30')
                    .print(font, first_col, nineth_row, 'Responsável do projeto: ')
                    .print(font, first_col, tenth_row, 'Telefone: ')
                    .print(font, first_col, eleventh_row, '1. Todos os itens devem ser novos;')
                    .print(font, first_col, twelfth_row, '2. Devolva este cartão no local e datas estipulados; ')
                    .print(font, first_col, thirteenth_row, '3. Não é necessário embalar para presente;')
                    .print(font, first_col, fourteenth_row, '4. Caso seja colocado uma quantidade maior de algum item, ele poderá ser')
                    .print(font, 65, fifteenth_row, 'realocado para outras sacolinhas')
                    .print(font, 235, fifteenth_row+1.5*font_size, 'A Operação Natal agradece a sua participação :)')
            })
            /*  Adiciona o texto em negrito */
        }).then(image => {
            return Jimp.loadFont(font_regular).then(font => {
                return image.print(font, 400, 290, 'Itens a serem inseridos:')
                    .print(font, 460, sixth_row + font_size + 5, 'Entregas:')
                    .print(font, 450, tenth_row + font_size + 5, 'Observações: ');
            }).catch(err => {
                throw (err);
            });
        }).then(resolve).catch(reject);
    });
});

background.then(result => {
    result.write('./dist/img/background.png')
});