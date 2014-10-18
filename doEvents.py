
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

def startRecordTestData():
    vals.testStartTime = time.time()
    vals.testTypeData = []
    try:
        unf = open(vals.userNameFile, 'r')
        vals.userName = unf.readline().strip()
        unf.close()
    except:
        print 'Failed to read userName from file: ' + str(vals.userNameFile)
    print 'start recording test data'

def saveTestData():
    saveFileName = vals.testTypeFile.format(vals.userName)
    sf  = open(saveFileName, 'w')
    print >> sf, 'time, dista0, distClick0, inRange, inBox, tIX, tIY, kIX, kIY, tTX, tTY, kTX, kTY, smoothX, smoothY, mouse_flg, mouseState, clickX, clickY, speed, buffSize'
    for string in vals.testTypeData:
        print >> sf, string
    sf.close()
    print 'Write test data to ' + str(saveFileName)
    

'''
'r': record mode
'c': calibration mode
'l': load data mode
'h': enter next screen(calibration)
'q': quit

't': typing test start/end 
'p': pointing test start/end
'd': dragging & double click enable/disable
'm': switch between mouse and keyboard
'e': do input calibration(optional)
'k': use index knuckle to help correct index tip

Shift + 'w'/'up arrow': change sensitivity of fingers
Shift + 's'/'down arrow': change sensitivity of fingers
Shift + 'a'/'left arrow': change sensitivity of fingers
Shift + 'd'/'right arrow': change sensitivity of fingers

Shift + 'f': new feature testing
Shift + 'r': testing relative version

'z': Will zoom, in other words sensitivity will decrease

'''

def eventHandling(eventsObject):
    for event in eventsObject:
        if event.type == KEYUP:
            if event.key == pygame.K_SPACE:
                vals.newClick_flg = 0
                vals.releaseButton = 0
                
        if event.type == KEYDOWN:
            #newGestures   
            if vals.newGestures:
                # Press shift and space to switch modes
                if (pygame.key.get_mods() & pygame.KMOD_SHIFT):
                    if (event.key == pygame.K_SPACE):
                        vals.mouse_flg = not vals.mouse_flg
                #Press space only, no Shift
                if vals.mouse_flg:
                    if not (pygame.key.get_mods() & pygame.KMOD_SHIFT):
                        if event.key == pygame.K_SPACE:
                            vals.newClick_flg = 1
                # Press shift and space to switch modes
                if (pygame.key.get_mods() & pygame.KMOD_SHIFT):
                    if (event.key == pygame.K_SPACE):
                        vals.mouse_flg = not vals.mouse_flg
                #Press space only, no Shift
                if vals.mouse_flg:
                    if not (pygame.key.get_mods() & pygame.KMOD_SHIFT):
                        if event.key == pygame.K_SPACE:
                            vals.newClick_flg = 1
            
            # Note: [not testing] or [testing but press Ctrl now]
            if not vals.testTypeFlag or (pygame.key.get_mods() & pygame.KMOD_CTRL):
                if not (pygame.key.get_mods() & pygame.KMOD_SHIFT):
                    if event.key==pygame.K_r: #start recording
                        vals.rec_flg=1

                        vals.inputCalibration=0

                        vals.planeDepthData = []

                        height = 300
                        width = height * float(vals.width) / vals.height
                        vals.relativeSpeed = [float(vals.width) / width / 0.3, float(vals.height) / height / 0.3]

                        # vals.calibration=False
                        # vals.testStartTime = time.time()  
                    elif event.key==pygame.K_c: #start vals.calibration
                        vals.calibration=1
                        vals.calibState = vals.START_CALIB
                        #vals.calibState = vals.READY_DEPTH_CALIB
                        vals.newGestures = 1
                    # Acts strange now
                    # elif event.key==pygame.K_s: #pauses the recording
                    #     vals.rec_flg=False 
                    elif event.key==pygame.K_q: #quits entirely
                        print "q pressed"
                        vals.quit_FLG=1
                        if vals.testTypeFlag or vals.testPointFlag:
                            # Quit without turn off the type/point flag
                            saveTestData()
                    #Load calibration data from file : 'l', load
                    elif event.key == pygame.K_l:
                        vals.calibLoadFlag = True
                        #vals.newGestures = 1
                    # Start testing the device while typing
                    elif event.key == pygame.K_t:# and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        vals.testTypeFlag = not vals.testTypeFlag
                        if vals.testTypeFlag:
                            if not vals.testPointFlag:
                                # Start testing and timing
                                startRecordTestData()
                            try:
                                # Open gedit on the right side of the screen
                                Popen(["gedit", vals.typeContentFile.format(vals.userName), \
                                    '--geometry=+1080+20'], stdin = open(os.devnull, 'r'))
                            except:
                                pass
                        else:
                            # Turn off. Save if necessary.
                            if not vals.testPointFlag:
                                saveTestData()
                        print 'testTypeFlag changed to {}.'.format(str(vals.testTypeFlag)) 
                    # Start testing the pointing function
                    elif event.key == pygame.K_p:
                        vals.testPointFlag = not vals.testPointFlag
                        if vals.testPointFlag:
                            if not vals.testTypeFlag:
                                # Start testing and timing
                                startRecordTestData()
                        else:
                            # Turn off. Save if necessary.
                            if not vals.testTypeFlag:
                                saveTestData()
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
                    elif event.key == pygame.K_z:
                        vals.zoom_flg = not vals.zoom_flg



#Julian doesn't want me to allow users to change values.
# Note: I decided to uncomment these, but add a shift key to make it safe.
# This is just for the testing. 
                #Change sensitivity of fingers
                elif (pygame.key.get_mods() & pygame.KMOD_SHIFT):
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                       vals.windowY += 50            
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                       vals.windowY -= 50
                    elif event.key==pygame.K_RIGHT or event.key == pygame.K_d:
                       vals.windowX += 50
                    elif event.key==pygame.K_LEFT or event.key == pygame.K_a:
                       vals.windowX -= 50
                    print 'window size: X-{}, Y-{}'.format(str(vals.windowX), str(vals.windowY))
#                     vals.relativeSpeed = [float(vals.width) / vals.windowX, float(vals.height) / vals.windowY]
                    print 'relative speed: X-{}, Y-{}'.format(vals.relativeSpeed[0], vals.relativeSpeed[1])
                    if event.key == pygame.K_f:
                        # Turn on/off the adjustable buffer size
                        vals.featureFlag = not vals.featureFlag
                        print 'featureFlag changed to {}'.format(str(vals.featureFlag))
                        if vals.featureFlag:
                            vals.speedBuff.erase()
                            vals.constBuff[0].erase()
                            vals.constBuff[1].erase()
                        else:
                            vals.buff[0].setBuffSize(vals.defaultBuffSize)
                            vals.buff[1].setBuffSize(vals.defaultBuffSize)

                    elif event.key == pygame.K_r:
                        # Turn on/off the relative version
                        vals.relativeFlag = not vals.relativeFlag
                        if vals.relativeFlag:
                            print 'Change to [Relative Mode]'
                            vals.planeDepthData = []

                            vals.buff[0].setBuffSize(vals.relativeBuffSize)
                            vals.buff[1].setBuffSize(vals.relativeBuffSize)

                            height = 300
                            width = height * float(vals.width) / vals.height
                            vals.relativeSpeed = [float(vals.width) / width / 0.3, float(vals.height) / height / 0.3]
                            
                            # vals.relativeSpeed = [float(vals.width) / vals.windowX, float(vals.height) / vals.windowY]
                            # print 'Log the depth data'
                        else:
                            print 'Change to [Absolute Mode]'
                            vals.buff[0].setBuffSize(vals.defaultBuffSize)
                            vals.buff[1].setBuffSize(vals.defaultBuffSize)
                        # Only write to files here when dubugging
                        # Normaly, we write to files when DEPTH_CALIB -> END_CALIB
                        # elif vals.planeDepthData != []:
                        #     ddf  = open('testLog/depthData.csv', 'w')
                        #     print >> ddf, 'tipThumb, knuThumb, tipIndex, knuIndex, rawX, rawY'
                        #     for data in vals.planeDepthData:
                        #         print >> ddf, data
                        #     ddf.close()
                        #     print 'Write depth data to file.'

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
                        vals.boxLimit=int(sumBoxLimit)-5
                        vals.boxLimitBottom=int(sumBoxLimit)+4

                        # Generate depth file to test or debug
                        sbdf  = open('testLog/switchBoxData.csv', 'w')
                        print >> sbdf, 'tipThumb, knuThumb, tipIndex, knuIndex, rawX, rawY'
                        for data in vals.switchBoxData:
                            print >> sbdf, data
                        sbdf.close()
                        print 'Write depth data to file.'

                        # # Get parameters for the plane: Ax + By + Cz + D = 0, E = sqrt(A**2 + B**2 + C**2), s = std
                        # [A, B, C, D, E, s] = getPlaneParam(vals.switchBoxData)
                        # vals.switchBoxParam = [A, B, C, D, E, s, s]

                        vals.calibState = vals.READY_CLICK_CALIB

                    elif vals.calibState == vals.READY_CLICK_CALIB:
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

                        if True:
                        # if vals.relativeFlag:
                            # Jump to depth calibration if relative
                            vals.calibState = vals.READY_DEPTH_CALIB
                            vals.planeDepthData = []
                        else:
                            #store them to file.
                            calibWriter = CalibFileManager(vals.calibFile)
                            calibWriter.write(vals.mouseModeValue, vals.clickValue, vals.mouseActTimeThre, vals.boxLimit, vals.boxLimitBottom)
                            vals.calibState = vals.END_CALIB

                    elif vals.calibState == vals.READY_DEPTH_CALIB:
                        vals.calibState = vals.DEPTH_CALIB

                    elif vals.calibState == vals.DEPTH_CALIB:
                        # Generate depth file to test or debug
                        ddf  = open('testLog/depthData.csv', 'w')
                        print >> ddf, 'tipThumb, knuThumb, tipIndex, knuIndex, rawX, rawY'
                        for data in vals.planeDepthData:
                            print >> ddf, data
                        ddf.close()
                        print 'Write depth data to file.'

                        # Get parameters for the plane: Ax + By + Cz + D = 0, E = sqrt(A**2 + B**2 + C**2), s
                        vals.planeParam = getPlaneParam(vals.planeDepthData)
                        vals.planeParam[-1] = 3 * vals.planeParam[-1]

                        # Get switch box parameters with the keyboard plane and switch points
                        distance = np.zeros(len(vals.switchBoxData))
                        # Load the data and get X, Y and Z
                        switchBoxStrArray = [x.split(',') for x in vals.switchBoxData]
                        switchBoxStr = zip(*switchBoxStrArray)
                        x, y, z = [float(x) for x in switchBoxStr[4]], [float(x) for x in switchBoxStr[5]], [float(x) for x in switchBoxStr[2]]
                        for i in range(len(x)):
                            distance[i] = getPlaneDistance(vals.planeParam, x[i], y[i], z[i])
                        print 'distance: max:{}, min:{}, mean:{}, std:{}'.format(distance.max(), distance.min(), \
                            distance.mean(), distance.std())
                        boxMean = distance.mean()
                        boxStd = distance.std()
                        vals.switchBoxParam = [20, max(boxMean - 3*boxStd, vals.planeParam[-1]+2)]

                        #store them to file.
                        calibWriter = CalibFileManager(vals.calibFile)
                        calibWriter.write(vals.mouseModeValue, vals.clickValue, vals.mouseActTimeThre, vals.boxLimit, \
                            vals.boxLimitBottom, vals.planeParam, vals.switchBoxParam)
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
                        planeParam = calibReader.read('planeParam').strip('[]').split(',')
                        vals.planeParam = [float(x) for x in planeParam]
                        switchBoxParam = calibReader.read('switchBoxParam').strip('[]').split(',')
                        vals.switchBoxParam = [float(x) for x in switchBoxParam]

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

def getPlane(x, y, z):
    matXY = np.array([x, y, np.ones(len(x))], np.float64)
    matXY = matXY.T
    vecZ = z
    ret = np.linalg.lstsq(matXY, vecZ)
    return ret

def getPlaneParam(depthData):
    "Calculate the keyboard plane parameters from the depth calibration"
    # boxSizeInc = 1.5

    # Load the data and get X, Y and Z
    depthDataStrArray = [x.split(',') for x in depthData]
    dataStr = zip(*depthDataStrArray)
    x, y, z = [float(x) for x in dataStr[4]], [float(x) for x in dataStr[5]], [float(x) for x in dataStr[2]]

    # Get the plane parameter
    # Linear function: z = a * x + b * y + c
    ret = getPlane(x, y, z)
    print 'Residual: {}, {}'.format(ret[1], ret[1] / len(x))
    a, b, c = ret[0]

    # z = ax + by + c => Ax + By + Cz + D = 0, E = sqrt(A^2 + B^2 + C^2)
    # A = a, B = b, C = -1, D = c, E = sqrt(a**2 + b**2 + 1)
    A, B, C, D, E = a, b, -1, c, np.sqrt(a**2 + b**2 + 1)

    # From distance(planeZ, rawZ), positive means the point is 'under' the plane, negative means the point is 'above' the plane.
    # So the max(positive) is the top of the 3D box of keyboard.
    deviation = np.zeros(len(x))
    for j in range(len(x)):
        distance = np.abs((A*x[j] + B*y[j] + C*z[j] + D) / E)
        zj = a*x[j] + b*y[j] + c
        if zj < z[j]:
            # this point is above the plane
            distance = -distance
        if distance > 5:
            print 'Discard: ' + str(distance)
            distance = 0
        deviation[j] = distance

    # For this problem, we need the max, to get all training points in the box.
    maxDev, minDev, stdDev = max(deviation), min(deviation), np.std(deviation)
    print 'max:{}, min:{}, std:{}'.format(maxDev, minDev, stdDev)

    return [A, B, C, D, E, stdDev]
    # keyboardTop = 3 * stdDev
    # keyboardTop = maxDev + boxSizeInc
            
    # return [A, B, C, D, E, keyboardTop]

def getPlaneDistance(planeParam, x, y, z):
    " Calculate the distance to the plane. Positive if under the plane, negative if above the plane "

    # z = ax + by + c <=> Ax + By + Cz + D = 0, E = sqrt(A^2 + B^2 + C^2)
    A, B, C, D, E = planeParam[:5]
    a, b, c = -A/C, -B/C, -D/C

    distance = np.abs((A*x + B*y + C*z + D) / E)
    zi = a*x + b*y + c
    if zi < z:
        # this point is above the plane
        distance = -distance

    return distance
