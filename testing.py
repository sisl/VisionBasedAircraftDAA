import mss


with mss.mss(display=":0.0") as sct:
    for filename in sct.save():
        print(filename)