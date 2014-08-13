# Plot and analyze the data during test type/point
# Zhen Li, Aug.13th, 2014

from pylab import *
import numpy as np
import Tkinter, Tkconstants, tkFileDialog
import os

def run():
    " Main procedure "

    tkObj = Tkinter.Tk()
    tkObj.file_opt = options = {}
    options['defaultextension'] = '.csv'

    openFiles = tkFileDialog.askopenfiles('r')
    fi = 0
    if openFiles:
        for fileObj in openFiles:
            fileName, fileExt = os.path.splitext(fileObj.name)
            if fileExt != '.csv':
                continue

            # Read data
            data = np.genfromtxt(fileObj.name, dtype = float, delimiter = ',', names = True)

            # time, dista0, distClick0, inrange, inBox
            # tIX, tIY, kIX, kIY, tTX, tTY, kTX, kTY
            # mouse_flg, mouseState, clickX, clickY

            color = ['y.-', 'b.-', 'c.-', 'k.-', 'g.-', 'r.-', 'm.-']
            keys = ['dista0', 'distClick0', 'inRange', 'inBox', 'tIX', 'tIY', 'kIX', 'kIY', \
            'tTX', 'tTY', 'kTX', 'kTY', 'mouseState', 'clickX', 'clickY']

            for i in range(len(keys)):
                figure(fi + i)
                plot(data['time'], data[keys[i]], color[i % len(color)])
                title('{}-{}'.format(str(fileName), str(keys[i])))

            show()

            fi += 1

run()