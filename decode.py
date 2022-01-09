# -*- coding: utf-8 -*-
"""
Created on Sat Jan  8 21:39:07 2022

@author: rainn
"""

import numpy as np
from PIL import Image

# from https://stackoverflow.com/questions/34913005/color-space-mapping-ycbcr-to-rgb
def ycbcr2rgb(im):
    xform = np.array([[1, 0, 1.402], [1, -0.34414, -.71414], [1, 1.772, 0]])
    rgb = im.astype(float)
    rgb[:,:,[1,2]] -= 128
    rgb = rgb.dot(xform.T)
    np.putmask(rgb, rgb > 255, 255)
    np.putmask(rgb, rgb < 0, 0)
    return np.uint8(rgb)
# from https://stackoverflow.com/questions/16388110/double-the-length-of-a-python-numpy-array-with-interpolated-new-values
def ntrpl8(Y):
    N = len(Y)
    X = np.arange(0, 2*N, 2)
    X_new = np.arange(2*N)       # Where you want to interpolate
    Y_new = np.interp(X_new, X, Y) 
    return(Y_new)

"""
Codes below this line, code attribution, array interpolation and import image
are written after Sun Jan  9 3:43:40 2022.
"""
file = input("Enter the path to the image: ")
imgfile = Image.open(file).convert('L')
img = np.asarray(imgfile)
y_bit = input("Enter the number of bits for Y' (default is 4): ")
y_bit = 4 if y_bit == "" else int(y_bit) # from https://stackoverflow.com/questions/13710631/is-there-shorthand-for-returning-a-default-value-if-none-in-python
cbcr_bit = 8 - y_bit

# Seperate Cb and Cr
y = img >> cbcr_bit
cb_half = img[:,::2] & (255 >> y_bit)
cr_half = img[:,1::2] & (255 >> y_bit)

# Interpolate the missing pixels
cb = np.uint8(ntrpl8(cb_half.flatten()).reshape(y.shape))
cr = np.uint8(ntrpl8(cr_half.flatten()).reshape(y.shape))

# Scale the range to fit 255
y255 = np.uint8(y*(255/((2**y_bit)-1)))
cb255 = np.uint8(cb*(255/((2**cbcr_bit)-1)))
cr255 = np.uint8(cr*(255/((2**cbcr_bit)-1)))

img_rgb = ycbcr2rgb(np.dstack((y255,cb255,cr255)))
out = Image.fromarray(img_rgb)
out.save(file[:-4]+"_color.png", "PNG")

print("Finished converting to color.")
# Finished writing at Sun Jan  9 5:50:37 2022
# Came back to fix a bug at Sun Jan  9 12:51:46 2022 - 12:57:18