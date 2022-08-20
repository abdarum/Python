# https://github.com/LeoHsiao1/pyexiv2

import pyexiv2
imagename = r"IMG_20220204_180644.jpg"

img = pyexiv2.Image(imagename)
data = img.read_exif()
data = img.read_iptc()
data = img.read_xmp()
if data.get('Xmp.fstop.favorite', '0') == '1': 
    print('fav')
img.close()