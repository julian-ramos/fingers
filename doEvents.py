
import pygame
from pygame import mouse
from pygame.locals import *
import pickle
import time
from bisect import bisect_left
import numpy as np
import sys
import os
from subprocess import Popen

import constants as vals
from calibFileManager import *
from funcs import peakdetect, smooth

def eventHandling(eventsObject):
    for event in eventsObject:
        if event.type==KEYDOWN:
            '''
            'r': record mode
            'c': calibration mode
            'l': load data mode
            'h': enter next screen(calibration)
            'q': quit
            
            't': test type open/close
            'p': test mouse open/close
            'd': dragging & double click enable/disable
            'm': switch between mouse and keyboard
            'e': do input calibration(optional)
            'k': use index knuckle to help correct index tip

            Not used: 'up arrow': change sensitivity of fingers
            Not used: 'down arrow': change sensitivity of fingers
            Not used: 'left arrow': change sensitivity of fingers
            Not used: 'right arrow': change sensitivity of fingers

            '''
            # Note: [not testing] or [testing but press Ctrl now]
            if not vals.testTypeFlag or (pygame.key.get_mods() & pygame.KMOD_CTRL):
                if event.key==pygame.K_r: #start recording
                    vals.rec_flg=1

                    vals.inputCalibration=0

                    # vals.calibration=False
                    # vals.testStartTime = time.time()  
                elif event.key==pygame.K_c: #start vals.calibration
                    vals.calibration=1
                    vals.calibState = vals.START_CALIB
                # Acts strange now
                # elif event.key==pygame.K_s: #pauses the recording
                #     vals.rec_flg=False 
                elif event.key==pygame.K_q: #quits entirely
                    print "q pressed"
                    vals.quit_FLG=1
                    if vals.testTypeFlag:
                        ttf  = open(vals.testTypeFile.format(vals.userName), 'w')
                        print >> ttf, 'time, dista0, distClick0, inRange, inBox, tIX, tIY, kIX, kIY, tTX, tTY, kTX, kTY, mouse_flg, mouseState, clickX, clickY'
                        for string in vals.testTypeData:
                            print >> ttf, string
                        ttf.close()
                #Load calibration data from file : 'l', load
                elif event.key == pygame.K_l:
                    vals.calibLoadFlag = True
                # Start testing the device while typing
                elif event.key == pygame.K_t:# and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    vals.testTypeFlag = not vals.testTypeFlag
                    if vals.testTypeFlag:
                        vals.testStartTime = time.time()
                        try:
                            unf = open(vals.userNameFile, 'r')
                            vals.userName = unf.readline().strip()
                            unf.close()
                            Popen(["gedit", vals.typeContentFile.format(vals.userName), \
                                '--geometry=+1080+20'], stdin = open(os.devnull, 'r'))
                        except:
                            pass
                    print 'testTypeFlag changed to {}.'.format(str(vals.testTypeFlag)) 
                # Start testing the pointing function
                elif event.key == pygame.K_p:
                    vals.testPointFlag = not vals.testPointFlag
                    print 'testPointFlag changed to {}'.format(str(vals.testPointFlag))
                # Enable/Disable dragging function
                elif event.key == pygame.K_d:
                    vals.dragFlag = not vals.dragFlag
                    print 'dragFlag changed to {}'.format(str(vals.dragFlag))
                #Forced mouse mode
                elif event.key==pygame.K_m:
                    if vals.mouse_flg==1:
                        vals.mouse_flg=0
                    else:
                        vals.mouse_flg=1
                # Use index knuckle to help index tip
                elif event.key == pygame.K_k:
                    vals.knuckleFlag = not vals.knuckleFlag
                    print 'knuckleFlag changed to {}'.format(str(vals.knuckleFlag))
                    
#Julian doesn't want me to allow users to change values.
                #Change sensitivity of fingers
                #elif event.key==pygame.K_UP:
                #    vals.windowY+=10            
                #elif event.key==pygame.K_DOWN:
                #    vals.windowY-=10
                #elif event.key==pygame.K_RIGHT:
                #    vals.windowX+=10
                #elif event.key==pygame.K_LEFT:
                #    vals.windowX-=10

                '''
                if vals.rec_flg: #if recording, can change the lag time
                    if event.key==pygame.K_z:
                        vals.lagValue+=100
                    elif event.key==pygame.K_x:
                        vals.lagValue-=100
                '''
            # if vals.testTypeFlag and not(pygame.key.get_mods() & pygame.KMOD_CTRL)
                    
        # Mouse events for vals.calibration mode
            if vals.calibration:
                # Transition if press 'H'
                if event.key == pygame.K_h:
                    if vals.calibState == vals.START_CALIB:
                        vals.calibState = vals.MOUSE_MODE_CALIB

                    elif vals.calibState == vals.MOUSE_MODE_CALIB:
                        while min(vals.mouseModeCalibList) < 50:
                            vals.mouseModeCalibList.remove(min(vals.mouseModeCalibList))
                        vals.mouseModeValue = int(1.2 * min(vals.mouseModeCalibList))
                        vals.clickCalibSTime = time.time()
                        while min(vals.boxBoundCalibList)<15:
                            vals.boxBoundCalibList.remove(min(vals.boxBoundCalibList))
                        sumBoxLimit=0
                        for i in xrange(len(vals.boxBoundCalibList)):
                            sumBoxLimit+=vals.boxBoundCalibList[i]
                        sumBoxLimit=sumBoxLimit/len(vals.boxBoundCalibList)
                        vals.boxLimit=int(sumBoxLimit)-3
                        vals.boxLimitBottom=int(sumBoxLimit)+3

                        vals.calibState = vals.CLICK_CALIB

                    elif vals.calibState == vals.CLICK_CALIB:
                        # Generate clickCalibFile to test or debug
                        ccf = open('testLog/clickCalibFile.txt', 'w')
                        for i in range(len(vals.clickingCalibList[0])):
                            print >> ccf, '{},{}'.format(vals.clickingCalibList[0][i],\
                            vals.clickingCalibList[1][i])
                        ccf.close()
                        # print vals.clickingCalibList
                                
                        vals.clickValue, vals.mouseActTimeThre = getDistAndTime(\
                            vals.clickingCalibList[0], vals.clickingCalibList[1], 2, 4)
                        vals.mouseActTimeThre = min(vals.mouseActTimeMax, vals.mouseActTimeThre)
                        vals.mouseActTimeThre = max(vals.mouseActTimeMin, vals.mouseActTimeThre)

                        print 'clickValue:{}, mouseActTimeThre:{}'.format(\
                            str(vals.clickValue), str(vals.mouseActTimeThre))

                        # Old code to get clickValue
                        '''
                        # clickingCalibList: (time, value)
                        while min(vals.clickingCalibList[1]) < 30:
                            vals.clickingCalibList[1].remove(min(vals.clickingCalibList[1]))
                        vals.clickValue=int(1.2 * min(vals.clickingCalibList[1]))
                        '''

                        #store them to file.
                        calibWriter = CalibFileManager(vals.calibFile)
                        calibWriter.write(vals.mouseModeValue, vals.clickValue, vals.mouseActTimeThre, vals.boxLimit, vals.boxLimitBottom)
                        vals.calibState = vals.END_CALIB

            # Read calibration data from file, vals.calibLoadFlag mode
            if vals.calibLoadFlag:
                if not vals.calibReadFinished:
                    calibReader = CalibFileManager(vals.calibFile)
                    try:
                        vals.mouseModeValue = float(calibReader.read('mouseModeValue'))
                        vals.clickValue = float(calibReader.read('clickValue'))
                        vals.mouseActTimeThre = float(calibReader.read('mouseActTimeThre'))
                        vals.boxLimit = float(calibReader.read('boxLimit'))
                        vals.boxLimitBottom = float(calibReader.read('boxLimitBottom'))

                    except:
                        # Go back and press again
                        print 'Error: Calibration data file not found.'
                        vals.calibLoadFlag = False
                        print sys.exc_info()[0]
                        return

                    vals.calibState = vals.END_CALIB
                    vals.calibReadFinished = True

            # Note: I canceled the design of type area,  because it is too complicated without a lib. 
            # I cannot find a way to add widgets from libs such as pgu without 
            # changing the frame of the project. By Zhen.

            # Show the character user types in
            # if vals.testTypeFlag and vals.typeGUI != None:
            #     vals.typeGUI.update([event])
            #     print str(pygame.key.name(event.key))

            #after calibration isdone and start the input area.
            #also it is resettable.
            if vals.calibState == vals.END_CALIB and event.key == K_e:
                vals.inputCalibration=1






        if event.type==QUIT:
            vals.quit_FLG=1

        if vals.testTypeFlag:
            if vals.textGUI != None:
                vals.textGUI.update(event)           

def getDistAndTime(X, Y, paramD, paramT):
    "Get mean and std of distance and time(ms) with calib data: meanDist, stdDist, meanTime, stdTime"
    "Then get answer = mean + std * param"
    # plot(X, Y, 'g.')
    windowLen = 16
    smoothY = smooth(Y, windowLen)
    smoothY = smoothY[(windowLen / 2 - 1) : -(windowLen / 2)]
    # plot(X, smoothY, 'c-')

    # Note: The author suggests: '(sample / period) / f' where '4 >= f >= 1.25'
    f = 6
    lookahead = len(X) / vals.clickNum / f

    _max, _min = peakdetect(smoothY, X, lookahead)#, 0.30)
    # print _max
    # print _min
    xm = [p[0] for p in _max]
    ym = [p[1] for p in _max]
    xn = [p[0] for p in _min]
    yn = [p[1] for p in _min]

    # plot(xm, ym, 'rx', markersize = 10)
    # plot(xn, yn, 'kx', markersize = 10)

    yTh = getYTh(ym, yn)
    # print 'yTh: ' + str(yTh)

    newXMax = []
    newYMax = []
    newXMin = []
    newYMin = []

    i, j = 0, 0
    
    lastPoint = 0
    ADD_MAX, \
    ADD_MIN = range(2)

    if xm[i] < xn[j]:
        #max,min,...
        newXMax.append(xm[i])
        newYMax.append(ym[i])
        i = i + 1
        lastPoint = ADD_MAX
    else:
        #min, max,... : add a max point
        newXMax.append(X[0])
        newYMax.append(smoothY[0])
        lastPoint = ADD_MAX

    while i < len(_max) and j < len(_min):
        if lastPoint == ADD_MAX:
            if xm[i] > xn[j]:
                # print 'max, [min], max: ' + str(ym[i-1] - yn[j])
                if (ym[i-1] - yn[j]) > yTh:
                    #...max, [min], max... : Normal
                    # print 'add min:{}, x={}'.format(str(j), xn[j])
                    newXMin.append(xn[j])
                    newYMin.append(yn[j])
                    j = j + 1
                    lastPoint = ADD_MIN

                    #Special judge for wrong [max] before it
                    try:
                        if i >= 1 and newXMax[-1] == X[0] and newXMax[-1] < xm[i-1]:
                            #print newXMax[-1], xm[i-1], i
                            newXMax[-1] = xm[i-1]
                            newYMax[-1] = ym[i-1]
                    except:
                        pass
                else:
                    #Discard the [min]
                    j = j + 1
            else:
                #...max, [max], min...: Discard it
                i = i + 1
        elif lastPoint == ADD_MIN:
            if xm[i] < xn[j]:
                # print 'min, [max], min: ' + str(ym[i] - yn[j -1])
                if (ym[i] - yn[j -1]) > yTh:
                    #...min, [max], min...: Normal
                    # print 'add max:{}, x={}'.format(str(i), xm[i])
                    newXMax.append(xm[i])
                    newYMax.append(ym[i])
                    i = i + 1
                    lastPoint = ADD_MAX
                else:
                    #Discard the [max]
                    i = i + 1
            else:
                #...min, [min], max: Discard it
                # newXMax.append((xn[j] + xn[j-1]) / 2)
                # newYMax.append(ym[0])
                # newXMin.append(xn[j])
                # newYMin.append(yn[j])
                j = j + 1
                # lastPoint = ADD_MIN
    else:
        if i < len(_max) and lastPoint == ADD_MIN:
            #...min, [max].
            newXMax.append(xm[i])
            newYMax.append(ym[i])
            i = i + 1
            lastPoint = ADD_MAX
        elif j < len(_min) and lastPoint == ADD_MAX and (ym[i-1] - yn[j]) > yTh:
            #...max, [min] : Make a max after it
            newXMin.append(xn[j])
            newYMin.append(yn[j])
            newXMax.append(X[-1])
            newYMax.append(smoothY[-1])
            j = j + 1
            lastPoint = ADD_MAX

    # plot(newXMax, newYMax, 'r*', markersize = 10)
    # plot(newXMin, newYMin, 'k*', markersize = 10)
    # print fi

    meanDist = np.mean(newYMin)
    stdDist = np.std(newYMin)
    targetDist = meanDist + stdDist * paramD
    print 'Dist: mean:{}, std:{}'.format(str(meanDist),  str(stdDist))

    clickTimes = getClickTimes(X, smoothY, newXMin, targetDist)
    meanTime = np.mean(clickTimes)
    stdTime = np.std(clickTimes)
    targetTime = meanTime + stdTime * paramT
    print 'Time: mean:{}, std:{}'.format(str(meanTime), str(stdTime))

    return targetDist, targetTime * 1000

def getYTh(ym, yn):
    "Get y threshold of the peak-valley"
    ymMean = (np.sum(ym) - min(ym) - max(ym)) / (len(ym) - 2)
    ynMean =  (np.sum(yn) - min(yn) - max(yn)) / (len(yn) - 2)
    # ret = (np.mean(ym) - np.mean(yn)) * 0.5
    ret = (ymMean - ynMean) * 0.8
    return ret

def  getClickTimes(X, Y, valleyX, targetY):
    "Get the click time with original data, valleyPoints, and targetY"
    if len(X) != len(Y):
        print "Error: The length of  the array must be the same."
        return
    # print valleyX
    # print targetY

    clickTimes = []
    lo = 0
    hi = len(X)

    for i in range(len(valleyX)):
        currXPos = bisect_left(X, valleyX[i], lo, hi)
        # print 'lo:{}, {}, hi:{}, {}, curr:{}, {}'.format(str(lo), str(X[lo]), str(hi-1), str(X[hi-1]),\
        #     str(currXPos), str(X[currXPos]))
        leftX = currXPos
        rightX = currXPos

        while leftX >= lo:
            if Y[leftX] >= targetY:
                break
            else:
                leftX = leftX - 1
        else:
            leftX = lo
        
        while rightX < hi:
            if Y[rightX] >= targetY:
                break
            else:
                rightX = rightX + 1
        else:
            rightX = hi - 1

        # print leftX, rightX, X[leftX], X[rightX], Y[leftX], Y[rightX]
        clickTimes.append(X[rightX] - X[leftX])
        lo = rightX

    return clickTimes
