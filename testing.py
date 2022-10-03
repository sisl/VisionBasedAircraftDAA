import mss

import cv2

import win32gui 
import numpy as np

h = win32gui.FindWindow(None, "X-System") 
if not h: 
    print("Window not found!") 
else: 
    left, top, right, bottom = win32gui.GetWindowRect(h) 
    width, height = (right - left), (bottom - top) 
    print(f'{left=}\n{right=}\n{top=}\n{width=}')


with mss.mss(display=":0.0") as sct:
    monitor = {"top": top, "left": left, "width": width, "height": height}
    output = "sct-{top}x{left}_{width}x{height}.png".format(**monitor)

    # Grab the data
    sct_img = sct.grab(monitor)

    # Save to the picture file
    mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
    print(output)