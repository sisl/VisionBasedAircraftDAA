import sys
sys.path.append('../')

import data_generation.constants as consts
import torch
import argparse
import torchvision as tv
import os
import pandas as pd
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from ultralytics import YOLO

def output_to_file(msg, reset=False):
    '''Prints evaluation to output file'''

    permission = 'a'
    if reset: permission = 'w'
    with open(f"{args.outfile_name}.txt", permission) as outfile:
        outfile.write(msg)

def get_ious(y_pred_xyxy, y_true_xyxy):
    '''Calculates intersection over union between predicted and true states'''

    ious = []
    for i in range(len(y_pred_xyxy)):
        if y_pred_xyxy[i] is None:
            ious.append(None)
            continue
        iou = tv.ops.box_iou(y_pred_xyxy[i], y_true_xyxy[i])
        ious.append(iou)
    return ious

def get_prec_and_recall(ious):
    '''Calculates precision and recall based on intersection over union'''

    tps = 0  # TP: IOU > 0
    fps = 0  # FP: IOU = 0
    fns = 0  # FN: no box detected

    for i in ious:
        if i is None:
            fns += 1
            continue

        for j in range(len(i)):
            if i[j] > 0:
                tps += 1
            else:
                fps += 1

    precision = 'NA' if tps + fps == 0 else tps / (tps + fps)
    recall = 'NA' if tps + fns == 0 else tps / (tps + fns)
    output_to_file(f"{precision}\t{recall}\t")

def get_map(ious):
    '''Calculates mean average precision (mAP)'''

    thresholds = np.arange(0.0,0.95,step=0.05)
    precisions = np.empty_like(thresholds)
    recalls = np.empty_like(thresholds)

    for idx, t in enumerate(thresholds):
        tps, fps, fns = 0, 0, 0

        for i in ious:
            if i is None:
                fns += 1
                continue
            for j in range(len(i)):
                if i[j] > t:
                    tps += 1
                else:
                    fps += 1
        precisions[idx] = 0 if tps + fps == 0 else tps / (tps + fps)
        recalls[idx] = 0 if tps + fns == 0 else tps / (tps + fns)

    recalls2 = np.append(recalls, 1)
    precisions2 = np.append(precisions, 0)
    recalls2 = np.insert(recalls2, 0, 0)
    precisions2 = np.insert(precisions2, 0, 0)
    
    AP = np.sum((recalls2[1:] - recalls2[:-1]) * precisions2[1:])
    output_to_file(f"{AP}\t")


def get_data(subdir):
    '''Retrieves data for use in evaluating the model
    
    Parameters:
    -----------
    subdir : str
        subdirectory ('val' or 'train') from which data is being drawn
    
    Returns:
    --------
    file_list
        list of image file names in the dataset
    y_pred_xyxy
        list of tensors representing predicted bounding boxes for intruder in xyxy format
    y_true_xyxy
        list of tensors representing bounding actual bounding boxes in xyxy format
    '''
    model = YOLO(args.path_to_model)

    source_list = os.listdir(os.path.join(args.path_to_datadir, "images", subdir))
    image_list = []
    file_list = []
    y_true_xyxy = []
    y_pred_xyxy = []

    count = 0
    total_count = 0
    extras = 0
    n = len(source_list)

    for idx, im_f in enumerate(source_list):
        im_path = os.path.join(args.path_to_datadir, "images", subdir, im_f)
        if os.path.isfile(im_path):
            if im_path == os.path.join(args.path_to_datadir, "images", subdir, '.DS_Store'): 
                extras += 1
                continue
            file_list.append(int(im_f.replace('.jpg', '')))

            image_list.append(Image.open(im_path))
            with open(os.path.join(args.path_to_datadir, "labels", subdir, im_f.replace('.jpg', '.txt')), "r") as labelfile:
                data_txt = labelfile.readline().split(" ")
            data = [float(d) for d in data_txt][1:]
            data = torch.FloatTensor([data])
            data = tv.ops.box_convert(data, 'cxcywh', 'xyxy')

            y_true_xyxy.append(data)

            count += 1
            total_count += 1
            results = model.predict(source=Image.open(im_path), save=args.save, save_txt=args.save)
            if results[0].boxes.shape[0] == 0:
                y_pred_xyxy.append(None)
            else:
                y_pred_xyxy.append(results[0].boxes.xyxyn)
            print ("IMAGE ", idx)
            if count == 100:
                print (f"Processed {total_count} images")
                count = 0

    return file_list, y_pred_xyxy, y_true_xyxy


def filter_data(category, criteria):
    '''Retrieves indexes of dataset images within the specified dataset that abide by criteria'''

    df = pd.read_csv(os.path.join(args.path_to_datadir, "state_data.csv"))
    idxs = [df.iloc[i]['filename']
            for i in range(len(df)) if criteria(df.iloc[i][category])]
    return idxs

def process_filter(filt, files, y_pred, y_true, subset):
    '''Filters data and calculates evaluation metrics on that data subset'''

    filtered_files = [i for i in range(len(files)) if files[i] in filt]
    if subset == 'valid': 
        output_to_file(f'Valid\t{len(filtered_files)}\t')
    else:
        output_to_file(f'Train\t{len(filtered_files)}\t')
    #output_to_tsv(f'{subset}\t{len(filtered_files)}\t')


    y_pred_temp = [y_pred[i]
                   for i in range(len(y_pred)) if i in filtered_files]
    y_true_temp = [y_true[i]
                   for i in range(len(y_true)) if i in filtered_files]
    ious = get_ious(y_pred_temp, y_true_temp)
    get_map(ious)
    get_prec_and_recall(ious)

def create_report():
    '''Outputs full evaluation report of model performance in different environment situations'''

    output_to_file("TEST SET EVALUATION\n", reset=True)
    output_to_file(f"Model: {args.path_to_model}\n")
    output_to_file(f"Dataset: {args.path_to_datadir}\n\n")
    output_to_file(f"Filter\tSubset\tSamples\tmAP\tPrecision\tRecall\n")
    output_to_file(f"---------------------------------------------------\n")
    output_to_file("OVERALL\t")
    
    #subdirs = ['valid', 'train'] if args.train_and_val else ['valid']
    files_val, y_pred_val, y_true_val = get_data('valid')
    if args.train_and_val: files_train, y_pred_train, y_true_train = get_data('train')

    # Filters
    ranges = {'close (0-150m)': lambda r: r < 150, 'medium (150-500m)': lambda r: r >=
              150 and r < 500, 'far (>500m)': lambda r: r >= 500}
    crafts = ['Cessna Skyhawk', 'Boeing 737-800', "King Air C90"]
    rel_alt = {'below (vang<0deg)': lambda a: a < 0,
               'above (vang>0deg)': lambda a: a >= 0}
    regions = consts.REGION_OPTIONS
    hours = {'morning (0800-1000)': (8, 10), 'midday (1000-1300)': (10, 13), 'early afternoon (1300-1500)': (13, 15), 'late afternoon (1500-1700)': (15, 17)}

    # print metrics for full validation set and train if specified
    output_to_file(f"Valid\t{len(y_pred_val)}\t")
    ious = get_ious(y_pred_val, y_true_val)
    get_map(ious)
    get_prec_and_recall(ious)
    output_to_file(f"\n")
    if args.train_and_val:
        output_to_file(f"OVERALL\tTrain\t{len(y_pred_train)}\t")
        ious = get_ious(y_pred_train, y_true_train)
        get_prec_and_recall(ious)
        output_to_file(f"\n")
    output_to_file(f"\n")

    for c in range(6):
        output_to_file(f"clouds={c}\t")
        cloud_filter = filter_data("clouds", lambda x: x == c)
        process_filter(cloud_filter, files_val, y_pred_val, y_true_val, 'valid')
        if args.train_and_val: 
            output_to_file(f"\nclouds={c}\t")
            process_filter(cloud_filter, files_train, y_pred_train, y_true_train, 'train')
        output_to_file(f"\n")

    output_to_file(f"\n")
    for r in ranges:
        filt = filter_data("z", ranges[r])
        output_to_file(f"distance={r}\t")
        process_filter(filt, files_val, y_pred_val, y_true_val, 'valid')
        if args.train_and_val: 
            output_to_file(f"\ndistance={r}\t")
            process_filter(filt, files_train, y_pred_train, y_true_train, 'train')
        output_to_file(f"\n")
            
    output_to_file(f"\n")
    for a in rel_alt:
        filt = filter_data("vang", rel_alt[a])
        output_to_file(f"vang={a}\t")
        process_filter(filt, files_val, y_pred_val, y_true_val, 'valid')
        if args.train_and_val:
            output_to_file(f"\nvang={a}\t")
            process_filter(filt, files_train, y_pred_train, y_true_train, 'train')
        output_to_file(f"\n")

    output_to_file(f"\n")
    for ac in crafts:
        filt = filter_data("ac", lambda x: x.strip() == ac)
        output_to_file(f"aircraft={ac}\t")
        process_filter(filt, files_val, y_pred_val, y_true_val, 'valid')
        if args.train_and_val: 
            output_to_file(f"\naircraft={ac}\t")
            process_filter(filt, files_train, y_pred_train, y_true_train, 'train')
        output_to_file(f"\n")

    output_to_file(f"\n")
    for r in regions:
        filt = filter_data("loc", lambda x: x.strip() == r)
        output_to_file(f"location={r}\t")
        process_filter(filt, files_val, y_pred_val, y_true_val, 'valid')
        if args.train_and_val: 
            output_to_file(f"\nlocation={r}\t")
            process_filter(filt, files_train, y_pred_train, y_true_train, 'train')
        output_to_file(f"\n")

    output_to_file(f"\n")
    for h in hours:
        filt = filter_data("local_time_sec", lambda x: x /
                           3600 >= hours[h][0] and x / 3600 < hours[h][1])
        output_to_file(f"hours={h}\t")
        process_filter(filt, files_val, y_pred_val, y_true_val, 'valid')
        if args.train_and_val: 
            output_to_file(f"\nhours={h}\t")
            process_filter(filt, files_train, y_pred_train, y_true_train, 'train')

        output_to_file(f"\n")
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--datadir", dest="path_to_datadir",
                        default="../../datasets/sample_small", help="Relative path to the directory for the dataset with which you want to evaluate the model.")
    parser.add_argument("-m", "--model", dest="path_to_model",
                        default="../../models/baseline.pt", help="Relative path to the file for the model (e.g. model.pt) you want to evaluate.")
    parser.add_argument("-t", "--train", dest="train_and_val",
                        action=argparse.BooleanOptionalAction, default=False, help="Flag for specifying that the evaluation should be done on both the training and validation data.")
    parser.add_argument("-o", "--outfile",
                        dest="outfile_name", default="results", help="Name of output file for evaluation results, without a filetype suffix. If a file with this name already exists, it will be overwritten.")
    parser.add_argument("-s", "--save", dest="save",
                        action=argparse.BooleanOptionalAction, default=False, help="Flag for specifying that the images with overlayed bounding boxes should be saved. Images and labels will be saved within the 'runs/detect' directory in 'model'.")

    global args
    args = parser.parse_args()

    create_report()