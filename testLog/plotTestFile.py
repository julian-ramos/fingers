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
            fileName = os.path.basename(fileObj.name).split('.')[0]
            fileExt = os.path.splitext(fileObj.name)[1]
            if fileExt != '.csv':
                continue

            # Read data
            data = np.genfromtxt(fileObj.name, dtype = float, delimiter = ',', names = True)

            # time, dista0, distClick0, inrange, inBox
            # tIX, tIY, kIX, kIY, tTX, tTY, kTX, kTY, smoothX, smoothY
            # mouse_flg, mouseState, clickX, clickY

            color = ['y.-', 'b.-', 'c.-', 'k.-', 'g.-', 'r.-', 'm.-','yx-','bx-','cx-','kx-']

            # Plot all data
            keys = ['dista0', 'distClick0', 'inRange', 'inBox', 'tIX', 'tIY', 'kIX', 'kIY', \
            'tTX', 'tTY', 'kTX', 'kTY', 'smoothX', 'smoothY', 'mouse_flg', 'mouseState', 'clickX', 'clickY']
            # for i in range(len(keys)):
            #     figure(fi)
            #     fi += 1
            #     plot(data['time'], data[keys[i]], color[i % len(color)])
            #     title('{}-{}'.format(str(fileName), str(keys[i])))

            # Plot selected data
            selData = data[:]
            keyX = ['distClick0', 'tIX', 'kIX', 'tTX', 'kTX', 'smoothX', 'mouse_flg', 'mouseState', 'clickX']
            figure(fi)
            fi += 1
            for i in range(len(keyX)):
                if keyX[i] == 'mouseState' or keyX[i] == 'mouse_flg':
                    ms = np.array(selData[keyX[i]]) * 500
                    plot(selData['time'], ms, color[i % len(color)], label = keyX[i])
                else:
                    plot(selData['time'], selData[keyX[i]], color[i % len(color)], label = keyX[i])
            title('{}-{}'.format(str(fileName), 'X'))
            legend(loc = 'lower right')

            # keyY = ['distClick0', 'tIY', 'kIY', 'tTY', 'kTY', 'smoothY', 'mouseState', 'clickY']
            keyY = ['distClick0', 'tIY', 'smoothY', 'tIX', 'smoothX', 'mouse_flg', 'mouseState']
            figure(fi)
            fi += 1
            for i in range(len(keyY)):
                if keyY[i] == 'mouseState' or keyY[i] == 'mouse_flg':
                    ms = np.array(selData[keyY[i]]) * 500
                    plot(selData['time'], ms, color[i % len(color)], label = keyY[i])
                else:
                    plot(selData['time'], selData[keyY[i]], color[i % len(color)], label = keyY[i])
            
            # Plot diff
            # ledDiffMean = (np.diff(selData['tIY']) + np.diff(selData['kIY']) + np.diff(selData['tTY']) + np.diff(selData['kTY'])) / 4 * 100
            # ledDiffMean = np.sqrt((np.diff(selData['tIY']) ** 2 + np.diff(selData['tIX']) ** 2)) * 100
            ledDiffMean = np.sqrt((np.diff(selData['smoothY']) ** 2 + np.diff(selData['smoothX']) ** 2))


            diffTime = selData['time'][1:]
            plot(diffTime, ledDiffMean, 'g-', label = 'diff^2')

            tmp = np.sum(ledDiffMean[0:5])
            diffBuff  = np.zeros(len(ledDiffMean) - 4)
            diffBuff[0] = tmp / 5
            for i in range(5, len(ledDiffMean)):
                tmp = tmp - ledDiffMean[i-5] + ledDiffMean[i]
                diffBuff[i - 4] = tmp / 5
            buffTime = selData['time'][5:]
            # plot(buffTime, diffBuff, 'b-', label = 'diff buff * 100')

            diffThumbIndex = np.abs((np.diff(selData['tTY']) + np.diff(selData['kTY']) - np.diff(selData['tIY']) - np.diff(selData['kIY'])) / 4 * 100)
            # plot(diffTime, diffThumbIndex, 'r-', label = '(thumbDiff - indexDiff) * 100')

            # plot the speed
            figure(fi)
            fi += 1
            key = ['mouseState', 'speed', 'buffSize']
            for i in range(len(key)):
                plot(selData['time'], selData[key[i]], color[i % len(color)], label = key[i])
            
            # size: a + b * speed
            # P1(minSpeed, maxBuff), P2(maxSpeed, minBuff)
            maxSpeed = 25
            minSpeed = 0.1
            maxBuff = 35
            minBuff = 10
            paramB = float(minBuff - maxBuff) / (maxSpeed - minSpeed)
            paramA = maxBuff - paramB * minSpeed
            
            size = paramA + paramB * np.array(selData['speed'])
            size = [int(x) for x in size]
            sizeLimit = [min(max(x, minBuff), maxBuff) for x in size]
            plot(selData['time'], sizeLimit, color[3], label = 'size = {} + {} * speed'.format(str(paramA), str(paramB)))

            title('{}-{}'.format(str(fileName), 'Y'))
            legend(loc = 'upper right')

            show()

run()