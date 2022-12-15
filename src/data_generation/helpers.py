import os
import time
import yaml
import json
import data_generation.constants as c
import sys

class Aircraft:
    """Object for storing positional information for Aircraft"""
    
    def __init__(self, ac_num, east, north, up, heading, pitch=-998, roll=-998):
        self.id = ac_num
        self.e = east
        self.n = north
        self.u = up
        self.h = heading
        self.p = pitch
        self.r = roll
    
    def __str__(self):
        out = "Craft: %.2f, East: %.2f, North: %.2f, Up: %.2f, Heading: %.2f, Pitch: %.2f, Roll: %.2f" % (self.id, self.e, self.n, self.u, self.h, self.p, self.r)
        return out

def make_yaml_file(outdir, name):
    """Create yaml file for YOLO formatting"""

    data = {
        "train": os.path.join(outdir, "train", "images"),
        "val": os.path.join(outdir, "valid", "images"),
        "names": {0: "aircraft"}
    }
    with open(os.path.join(outdir, f"{name}.yaml"), 'w+') as out:
        yaml.dump(data, out, default_flow_style=False, sort_keys=False)

def prepare_files(args):
    """Prepare file layout for YOLO formatting"""

    stamp = time.time()

    if args.datasetname is None:
        outdir = os.path.join(c.PATH, "data_" + str(stamp), "")
    else: 
        outdir = os.path.join(c.PATH, args.datasetname + "/")

    if args.append and args.datasetname is None:
        raise ValueError(f"If you want to append to an existing dataset, the name of the dataset must be specified with the --name flag.")

    if not args.append and os.path.exists(outdir):
        raise RuntimeError(f"There is already a data folder with the name {args.datasetname}.")

    args.outdir = outdir
     
    if not args.append:
        os.makedirs(outdir)
        os.makedirs(os.path.join(outdir, "train", "images", ""))
        os.makedirs(os.path.join(outdir, "valid", "images", ""))
        os.makedirs(os.path.join(outdir, "train", "labels", ""))
        os.makedirs(os.path.join(outdir, "valid", "labels", ""))

        csv_file = os.path.join(outdir, 'state_data.csv')

        with open(csv_file, 'w+') as fd:
            fd.write("filename,e0,n0,u0,h0,p0,r0,vang,hang,z,e1,n1,u1,h1,p1,r1,intr_x,intr_y,loc,ac,clouds,local_time_sec\n")

    make_yaml_file(outdir, args.datasetname)

    # set metadata
    total_images = args.num_train + args.num_valid
    if os.path.exists(os.path.join(outdir, "metadata.json")):
        with open(os.path.join(outdir, "metadata.json"), "r") as metafile:
            prev_data = json.load(metafile)
        curr_range = str(prev_data['total_images']) + "." + str(prev_data['total_images'] + total_images - 1)
        curr_range = float(curr_range)
        prev_data[curr_range] = vars(args)
        metadata = prev_data        
        metadata['total_images'] = metadata['total_images'] + total_images
    else: 
        curr_range = str(0) + "." + str(total_images - 1)
        metadata = {float(curr_range): vars(args), 'total_images': total_images}

    json_object = json.dumps(metadata, indent=4)
    with open(os.path.join(outdir, "metadata.json"), "w") as outfile:
        outfile.write(json_object)

    return outdir, metadata['total_images']