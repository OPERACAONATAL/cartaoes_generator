require 'rmagick'

jpg = Magick::ImageList.new('./dist/img/page/page-6.png')
jpg.write('test.pdf')
