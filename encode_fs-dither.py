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
# from https://scipython.com/blog/floyd-steinberg-dithering/
def get_new_val(old_val, nc):
    """
    Get the "closest" colour to old_val in the range [0,1] per channel divided
    into nc values.
    """
    return np.round(old_val * (nc - 1)) / (nc - 1)
def fs_dither(img, nc):
    """
    Floyd-Steinberg dither the image img into a palette with nc colours per
    channel.
    """
    arr = np.array(img, dtype=float) / 255

    for ir in range(img.shape[0]):
        for ic in range(img.shape[1]):
            # NB need to copy here for RGB arrays otherwise err will be (0,0,0)!
            old_val = arr[ir, ic].copy()
            new_val = get_new_val(old_val, nc)
            arr[ir, ic] = new_val
            err = old_val - new_val
            # In this simple example, we will just ignore the border pixels.
            if ic < img.shape[1] - 1:
                arr[ir, ic+1] += err * 7/16
            if ir < img.shape[0] - 1:
                if ic > 0:
                    arr[ir+1, ic-1] += err * 3/16
                arr[ir+1, ic] += err * 5/16
                if ic < img.shape[1] - 1:
                    arr[ir+1, ic+1] += err / 16

    carr = np.array(arr/np.max(arr, axis=(0,1)) * nc, dtype=np.uint8)
    return np.array(carr)

file = input("Enter the path to the image: ")
imgfile = Image.open(file).convert('RGB')
img = np.asarray(imgfile)
img_yuv = rgb2ycbcr(img) 
y_bit = input("Enter the number of bits for Y' (default is 4): ")
y_bit = 4 if y_bit == "" else int(y_bit) # from https://stackoverflow.com/questions/13710631/is-there-shorthand-for-returning-a-default-value-if-none-in-python
cbcr_bit = 8 - y_bit

dithery = input("Do you want to dither Y'? (Takes a while to compute) [y or n]: ")
ditherc = input("Do you want to dither CbCr? (Takes a while to compute) [y or n]: ")

# Scale the range to fit bit ratio and maybe dither
if dithery == "y":
    print("Dithering Y'...")
    y = fs_dither(img_yuv[:,:,0],(2**y_bit)-1)
    print("Finished dithering Y'.")
else:
    y = np.uint8(img_yuv[:,:,0]*(((2**y_bit)-1)/255))
if ditherc == "y":    
    print("Dithering Cb...")
    cb = fs_dither(img_yuv[:,:,1],(2**cbcr_bit)-1)
    print("Dithering Cr...")
    cr = fs_dither(img_yuv[:,:,2],(2**cbcr_bit)-1)
    print("Finished dithering CbCr.")
else:
    cb = np.uint8(img_yuv[:,:,1]*(((2**cbcr_bit)-1)/255))
    cr = np.uint8(img_yuv[:,:,2]*(((2**cbcr_bit)-1)/255))

# Interlace Cb and Cr
c = np.stack((cb[:,::2],cr[:,1::2]), axis=-1).reshape(y.shape)

# Allocate Y' to MSB and Cb/Cr in LSB
composite = (y << cbcr_bit) + c
out = Image.fromarray(composite)
if dithery or ditherc:
    out.save(file[:-4]+"_b-w_dither.png", "PNG")
else:
    out.save(file[:-4]+"_b-w.png", "PNG")
print("Finished converting to black and white.")
# Finished writing at Sun Jan  9 3:42:45 2022
# Came back to add dither function at Sun Jan  9 13:53:25 2022 - 14:46:06