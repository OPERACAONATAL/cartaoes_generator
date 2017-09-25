require 'rmagick'
require 'progress_bar'

pages = Dir.entries('./dist/img/page/')
# https://stackoverflow.com/a/22468447/7092954
pages = pages.sort_by { |x| x[/\d+/].to_i }
# retirando '.' e '..' dos arquivos lidos
pages = pages[2..-1]
bar = ProgressBar.new(pages.length)

for i in (0..pages.length).step(10)
    bar.increment! i
    data = pages[i..i+9]
    data.map{ |e| Magick::ImageList.new("./dist/img/page/#{e}").write("./dist/pdf/#{e.sub! '.png', ''}.pdf") }
    # Rodando o Garbage Collector -- como se utiliza memória pesadamente durante a execução da aplicação, se deve
    # liberá-la de tempos em tempos para que não comece a acentecer swap pesadamente.
    GC.start
end
