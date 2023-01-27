'''import torch
import numpy as np
from yolov5.models.yolo import Model
from yolov5.models.common import *
from yolov5.utils.torch_utils import fuse_conv_and_bn

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import ImageGrid
import matplotlib.patches as patches'''

import sys
sys.path.append('..')
import mss
from ultralytics import YOLO
import numpy as np

'''
def get_bb(model, im, save):
    bbs = []
    df = model(im).pandas().xyxy[0]
    if not df.empty:
        for i in range(len(df)):
            xmin = np.rint(df['xmin'][i])
            xmax = np.rint(df['xmax'][i])
            ymin = np.rint(df['ymin'][i])
            ymax = np.rint(df['ymax'][i])

            xp = xmin
            yp = ymin
            w = xmax - xmin
            h = ymax - ymin
            bbs.append([xp, yp, w, h])
    else:
        xp, yp, w, h = 0, 0, 0, 0

    if save > -1:
        f, ax = plt.subplots()
        f.set_figwidth(14)
        f.set_figheight(14)

        ax.imshow(im)

        if not df.empty:
            conf = np.round(df['confidence'][0], decimals=2)

            rect = patches.Rectangle((xp, yp),
                                     w, h, linewidth=1, edgecolor='r', facecolor='none')
            ax.add_patch(rect)
            ax.text(xp + (w / 2), yp - 10, "Conf: " + str(conf), horizontalalignment='center',
                    verticalalignment='center', color='r')

        plt.xlim(0, 1920)
        plt.ylim(1056, 0)
        plt.axis('off')

        filename = 'imgs/' + str(save) + '.png'
        plt.savefig(filename, bbox_inches='tight', pad_inches=0)
        plt.close(f)

    return not df.empty, bbs

def load_model(ckpt_file):
    ckpt = torch.load(ckpt_file)

    # Create model architecture
    model = Model(ckpt['model'].yaml)

    # Load the weights
    model.load_state_dict(ckpt['model'].state_dict())

    # Fuse and autoshape
    print("Fusing...")
    for m in model.modules():
        if isinstance(m, (Conv, DWConv)) and hasattr(m, 'bn'):
            m.conv = fuse_conv_and_bn(m.conv, m.bn)  # update conv
            delattr(m, 'bn')  # remove batchnorm
            m.forward = m.forward_fuse  # update forward

    model = AutoShape(model)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    return model

def run_live_predictor(model_path):
    model = load_model(model_path)
    screen_shot = mss.mss()
    ss = np.array(screen_shot.grab(screen_shot.monitors[0]))[:, :, :]
    get_bb(model, ss, "test")'''

def run_live_predictor2(model_path):
    model = YOLO(model_path)
    screen_shot = mss.mss()
    ss = np.array(screen_shot.grab(screen_shot.monitors[0]))[:, :, :3]
    print(ss.shape)
    results = model.predict(source=ss, save=True, save_txt=True)

if __name__ == '__main__':
    model_path = "../../runs/detect/train/weights/best.pt"
    run_live_predictor2(model_path)