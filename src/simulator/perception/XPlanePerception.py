import sys
sys.path.append('..')

from evaluation import output_enc_result, evalSingleAlertFrequency, evalSingleNMAC
from perception.xp_constants import REGION_OPTIONS, TIME_OPTIONS
import pymap3d as pm
import shutil
import os
import cv2
from PIL import Image
import mss
from ultralytics import YOLO
import numpy as np
from data_generation.helpers import Aircraft
from xpc3 import *
import time


def set_position(client, aircraft, loc):
    """Sets position of aircraft in X-Plane

    Parameters
    ----------
    client : SocketKind.SOCK_DGRAM
        XPlaneConnect socket
    aircraft : Aircraft
        object containing details about craft's position
    """
    ref = REGION_OPTIONS[loc]
    p = pm.enu2geodetic(aircraft.e, aircraft.n, aircraft.u,
                        ref[0], ref[1], ref[2])  # east, north, up
    client.sendPOSI([*p, 0, 0, aircraft.h], aircraft.id)


class XPlanePerception:
    '''Uses aircraft detection model to detect the intruder'''

    def __init__(self, args):
        self.client = None
        self.args = args
        self.model_path = args.model_path
        self.model = YOLO(self.model_path)
        self.setup_xplane()
        self.image_count = 0
        self.image_dir = 'perception/images/'
        self.setup_environ()
        self.latest_exact_time = 0

    def __del__(self):
        self.client.close()
        del self.model

    def setup_environ(self):
        client = self.client

        # setting cloud layers
        client.sendDREF("sim/weather/cloud_type[1]", 0)
        client.sendDREF("sim/weather/cloud_type[2]", 0)
        # lowest clouds at about 15000ft
        client.sendDREF("sim/weather/cloud_base_msl_m[0]", 4572)
        # upper end of clouds at about 17000ft
        client.sendDREF("sim/weather/cloud_tops_msl_m[0]", 5182)
        client.sendDREF("sim/weather/cloud_type[0]", self.args.weather)

    def set_time(self):
        # set time
        window = self.args.time_window
        times = {'morning': (8.0, 10.0), 'midday': (10.0, 13.0), 'earlyafternoon': (
            13.0, 15.0), 'lateafternoon': (15.0, 17.0)}
        local_time = np.random.uniform(
            times[window][0] * 3600, times[window][1] * 3600)
        zulu_time = local_time + (TIME_OPTIONS[self.args.location] * 3600)
        self.client.sendDREF("sim/time/zulu_time_sec", zulu_time)
        self.client.sendDREF("sim/time/local_date_days", 0)
        self.latest_exact_time = local_time

    def setup_xplane(self):
        '''Establishes connection with X-Plane to prepare for detection'''

        client = XPlaneConnect()
        client.socket.settimeout(None)

        client.sendDREF("sim/weather/cloud_type[0]", 0)
        client.pauseSim(True)
        client.sendDREF("sim/operation/override/override_joystick", 1)
        client.sendVIEW(85)

        self.client = client
        set_position(client, Aircraft(
            0, 0, 0, 0, 0, pitch=0, roll=0), self.args.location)
        set_position(client, Aircraft(1, 0, 100, 0, 0,
                     pitch=0, roll=0), self.args.location)

    def mult_matrix_vec(self, m, v):
        """4x4 matrix transform of an XYZW coordinate - this matches OpenGL matrix conventions"""

        m = np.reshape(m, (4, 4)).T
        return np.matmul(m, v)

    def get_bb_coords(self, ss):
        """Calculates coordinates of intruder bounding box
        Returns
        -------
        int
            x position of intruder on screen from upper left 0,0
        int
            y position of intruder on screen from upper left 0,0
        """

        screen_h, screen_w, _ = ss.shape

        # retrieve x,y,z position of intruder
        acf_wrl = np.array([
            self.client.getDREF("sim/multiplayer/position/plane1_x")[0],
            self.client.getDREF("sim/multiplayer/position/plane1_y")[0],
            self.client.getDREF("sim/multiplayer/position/plane1_z")[0],
            1.0
        ])

        mv = self.client.getDREF("sim/graphics/view/world_matrix")
        proj = self.client.getDREF("sim/graphics/view/projection_matrix_3d")

        acf_eye = self.mult_matrix_vec(mv, acf_wrl)
        acf_ndc = self.mult_matrix_vec(proj, acf_eye)

        acf_ndc[3] = 1.0 / acf_ndc[3]
        acf_ndc[0] *= acf_ndc[3]
        acf_ndc[1] *= acf_ndc[3]
        acf_ndc[2] *= acf_ndc[3]

        final_x = screen_w * (acf_ndc[0] * 0.5 + 0.5)
        final_y = screen_h * (acf_ndc[1] * 0.5 + 0.5)

        return final_x, screen_h - final_y

    def perceiveIntruderState(self, s_own, s_int, enc_idx):
        '''Positions aircraft in X-Plane and then takes a screenshot and passes it through the model to detect intruder'''

        # ENCOUNTER STATE [x, y, z, v, dh, theta]
        [x0, y0, z0, _, _, theta0] = s_own[0:6]
        [x1, y1, z1, _, _, theta1] = s_int[0:6]

        # using xyxy prediction from the model:
        # x, y: estimated from theta and prediction of how far the planes are apart
        # z: ownship z value

        # set plane positions and take screenshot
        set_position(self.client, Aircraft(
            0, x0, y0, z0, theta0), self.args.location)
        set_position(self.client, Aircraft(
            1, x1, y1, z1, theta1), self.args.location)
        time.sleep(0.1)
        screen_shot = mss.mss()
        ss = np.array(screen_shot.grab(screen_shot.monitors[1]))[:, :, :3]
        true_state = self.get_bb_coords(ss)

        predictions = self.model(ss, stream=True, verbose=False)
        for prediction in predictions:
            boxes = prediction.boxes.xyxy
            for box in boxes:
                [x1, y1, x2, y2] = box.tolist()
                if x1 <= true_state[0] <= x2 and y1 <= true_state[1] <= y2:
                    self.image_count += 1
                    return s_int

        '''if enc_idx is not None:
            cv2.imwrite(f"{self.image_dir}{self.image_count}.jpg", ss)'''

        del predictions
        self.image_count += 1
        return None

    def evalEnc(self, enc, enc_num, args):
        output_enc_result(
            f'{args.encs_dir},{self.model_path},{enc_num},{args.weather},{args.location},{args.craft},{args.time_window},{self.latest_exact_time},', args.fname)
        evalSingleAlertFrequency(enc, args.fname)
        evalSingleNMAC(enc, args.fname)

    # extremely sketchy
    def make_gif(self, name="../gifs/encounter.gif"):
        '''Creates gif of one encounter'''

        sorted_source_list = [str(i) + '.jpg' for i in range(50)]
        image_list = []

        for im_f in sorted_source_list:
            im_path = os.path.join(self.image_dir, im_f)
            if os.path.isfile(im_path):
                image_list.append(Image.open(im_path))
                os.remove(im_path)

        predict_path = os.path.join("runs", "detect", "predict")

        # clear any old files
        if os.path.exists(predict_path):
            shutil.rmtree(predict_path)

        predictions = self.model.predict(
            source=image_list, save=True, save_txt=True)
        sorted_source_list = [os.path.join(
            predict_path, "image" + str(i) + '.jpg') for i in range(50)]
        frames = [Image.open(image)
                  for image in sorted_source_list if os.path.exists(image)]
        frame_one = frames[0]
        frame_one.save(name, format="GIF", append_images=frames,
                       save_all=True, duration=1000, loop=3)
        shutil.rmtree(predict_path)
