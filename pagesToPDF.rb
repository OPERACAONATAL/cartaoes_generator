require 'rmagick'

pages = Dir.entries('./dist/img/page/')
# https://stackoverflow.com/a/22468447/7092954
pages = pages.sort_by { |x| x[/\d+/].to_i }
# retirando '.' e '..' dos arquivos lidos
pages = pages[2..-1]

print("Pages size: ", pages.length, "\n")
print("Before\n")
pages = pages[130..-1]
pages.map{ |e| Magick::ImageList.new("./dist/img/page/#{e}").write("./dist/pdf/#{e.sub! '.png', ''}.pdf") }
print("After\n")
