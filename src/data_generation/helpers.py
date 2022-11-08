import os
import time
import yaml
import json

class Aircraft:
    """Object for storing positional information for Aircrafts"""
    
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

def make_yaml_file(outdir):
    """Create yaml file for YOLO formatting"""

    data = {
        "train": f"{outdir}/train/images",
        "val": f"{outdir}/valid/images",
        "names": {0: "aircraft"}
    }
    with open(f'{outdir}data.yaml', 'w+') as out:
        yaml.dump(data, out, default_flow_style=False, sort_keys=False)

def prepare_files(args):
    """Prepare file layout for YOLO formatting"""

    outdir = args.outdir + "data_" + str(time.time()) + "/"
    args.outdir = outdir
    os.makedirs(outdir)
    os.makedirs(outdir + "train/images/")
    os.makedirs(outdir + "valid/images/")
    os.makedirs(outdir + "train/labels/")
    os.makedirs(outdir + "valid/labels/")

    make_yaml_file(outdir)

    # set metadata
    json_object = json.dumps(vars(args), indent=4)
    with open(outdir + "metadata.json", "w") as outfile:
        outfile.write(json_object)

    csv_file = outdir + 'state_data.csv'
    with open(csv_file, 'w+') as fd:
        fd.write("filename,e0,n0,u0,h0,p0,r0,vang,hang,z,e1,n1,u1,h1,intr_x,intr_y\n")
    return outdir

'''
# Window setup helpers
def trace_window(x, y, height, width):
    """Trace XPlane window with mouse for demo purposes"""

    move_time = 1
    pyautogui.moveTo(x,y + 1,move_time)
    pyautogui.moveTo(x,height,move_time)
    pyautogui.moveTo(width,height,move_time)
    pyautogui.moveTo(width,y + 1,move_time)
    pyautogui.moveTo(x,y + 1,move_time)

def get_window_dims(client):
    """Allow user to specify params for window location"""

    width = client.getDREF("sim/graphics/view/window_width")[0]
    height = client.getDREF("sim/graphics/view/window_height")[0]
    trace_window(0,0,height, width)
    while input("Is this the window you want captured? (Y/N): ") == "N":
        tl_x = int(input("New top left x: "))
        tl_y = int(input("New top left y: "))
        trace_window(tl_x, tl_y, height, width)
    return tl_x, tl_y'''