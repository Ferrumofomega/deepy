#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging, os
logging.basicConfig(level=logging.INFO)

from deepy import *
from core import DrawModel

from PIL import Image

def scale_norm(arr):
    arr = arr - arr.min()
    scale = (arr.max() - arr.min())
    return arr / scale

def img_grid(arr, global_scale=True):
    N, height, width = arr.shape

    rows = int(np.sqrt(N))
    cols = int(np.sqrt(N))

    if rows*cols < N:
        cols = cols + 1

    if rows*cols < N:
        rows = rows + 1

    total_height = rows * height
    total_width  = cols * width

    if global_scale:
        arr = scale_norm(arr)

    I = np.zeros((total_height, total_width))

    for i in xrange(N):
        r = i // cols
        c = i % cols

        if global_scale:
            this = arr[i]
        else:
            this = scale_norm(arr[i])

        offset_y, offset_x = r*height, c*width
        I[offset_y:(offset_y+height), offset_x:(offset_x+width)] = this

    I = (255*I).astype(np.uint8)
    return Image.fromarray(I)

ANIMATION_SAMPLES = 16*16

plot_path = os.path.join(os.path.dirname(__file__), "plots")

if __name__ == '__main__':
    from argparse import ArgumentParser
    ap = ArgumentParser()
    ap.add_argument("model", help="pre-trained model path")
    ap.add_argument("--task", default="mnist")
    args = ap.parse_args()

    model, img_size, attention_times = None, None, None
    if args.task == "mnist":
        img_size = 28
        attention_times = 64
    else:
        raise NotImplementedError("task should be 'mnist' or 'sketch'")

    model = DrawModel(image_width=img_size, image_height=img_size, attention_times=attention_times)
    model.load_params(args.model)

    sample_function = theano.function([], outputs=model.sample(ANIMATION_SAMPLES), allow_input_downcast=True)
    samples = sample_function()

    samples = samples.reshape( (attention_times, ANIMATION_SAMPLES, img_size, img_size) )

    for i in xrange(attention_times):
        img = img_grid(samples[i,:,:,:])
        img.save(plot_path + os.sep + "%s-%03d.png" % (args.task, i))

    # Compose all images to animation
    os.system("convert -delay 5 -loop 0 %s/%s-*.png %s/%s-animation.gif" % (plot_path, args.task, plot_path, args.task))








