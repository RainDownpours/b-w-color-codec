# -*- coding: utf-8 -*-
"""
Created on Sat Jan  8 21:03:34 2022

@author: rainn
"""

import numpy as np
from PIL import Image

# from https://stackoverflow.com/questions/34913005/color-space-mapping-ycbcr-to-rgb
def rgb2ycbcr(im):
    xform = np.array([[.299, .587, .114], [-.1687, -.3313, .5], [.5, -.4187, -.0813]])
    ycbcr = im.dot(xform.T)
    ycbcr[:,:,[1,2]] += 128
    return np.uint8(ycbcr)

file = input("Enter the path to the image: ")
img = np.asarray(Image.open(file))
img_yuv = rgb2ycbcr(img) 
y_bit = input("Enter the number of bits for Y' (default is 4): ")
y_bit = 4 if y_bit == "" else int(y_bit) # from https://stackoverflow.com/questions/13710631/is-there-shorthand-for-returning-a-default-value-if-none-in-python
cbcr_bit = 8 - y_bit

# Scale the range to fit bit ratio
y = np.uint8(img_yuv[:,:,0]*(((2**y_bit)-1)/255))
cb = np.uint8(img_yuv[:,:,1]*(((2**cbcr_bit)-1)/255))
cr = np.uint8(img_yuv[:,:,2]*(((2**cbcr_bit)-1)/255))

# Interlace Cb and Cr
c = np.stack((cb[:,::2],cr[:,1::2]), axis=-1).reshape(y.shape)

# Allocate Y' to MSB and Cb/Cr in LSB
composite = (y << cbcr_bit) + c
out = Image.fromarray(composite)
out.save(file[:-4]+"_b-w.png", "PNG")

print("Finished converting to black and white.")
# Finished writing at Sun Jan  9 3:42:45 2022