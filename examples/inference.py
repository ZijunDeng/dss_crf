#!/usr/bin/python

"""
Adapted from the original C++ example: densecrf/examples/dense_inference.cpp
http://www.philkr.net/home/densecrf Version 2.2
"""

import numpy as np
import cv2
import pydensecrf.densecrf as dcrf
from skimage.segmentation import relabel_sequential
import sys
import Image

if len(sys.argv) != 4:
    print("Usage: python {} IMAGE ANNO OUTPUT".format(sys.argv[0]))
    print("")
    print("IMAGE and ANNO are inputs and OUTPUT is where the result should be written.")
    sys.exit(1)

img = cv2.imread(sys.argv[1], 1)
labels = relabel_sequential(cv2.imread(sys.argv[2], 0))[0].flatten()
output = sys.argv[3]

palette = [0,0,0,
               128,0,0,
               0,128,0,
               128,128,0,
               0,0,128,
               128,0,128,
               0,128,128,
               128,128,128,
               64,0,0,
               192,0,0,
               64,128,0,
               192,128,0,
               64,0,128,
               192,0,128,
               64,128,128,
               192,128,128,
               0,64,0,
               128,64,0,
               0,192,0,
               128,192,0,
               0,64,128,
               128,64,128,
               0,192,128,
               128,192,128,
               64,64,0,
               192,64,0,
               64,192,0,
               192,192,0]

M = 21  # number of labels

# Setup the CRF model
d = dcrf.DenseCRF2D(img.shape[1], img.shape[0], M)

# Certainty that the ground truth is correct
GT_PROB = 0.5

# Simple classifier that is 50% certain that the annotation is correct
u_energy = -np.log(1.0 / M)
n_energy = -np.log((1.0 - GT_PROB) / (M - 1))
p_energy = -np.log(GT_PROB)

U = np.zeros((M, img.shape[0] * img.shape[1]), dtype='float32')
U[:, labels > 0] = n_energy
U[labels, np.arange(U.shape[1])] = p_energy
U[:, labels == 0] = u_energy
d.setUnaryEnergy(U)

d.addPairwiseGaussian(sxy=3, compat=3)
d.addPairwiseBilateral(sxy=80, srgb=13, rgbim=img, compat=10)

# Do the inference
res = np.argmax(d.inference(5), axis=0).astype('uint8')

res = res.reshape(img.shape[:2])
res = Image.fromarray(res, mode='P')
res.putpalette(palette)
res.save(output)
