from scipy.spatial.distance import euclidean 
import constants as vals
import funcs as fun
import time
import numpy as np
import doDepth
from mainFingers import finger2Mouse
from doEvents import getPlaneDistance

def checkSwitchBox(x, y, z):
    " Check if the finger is in valid height(inside swithch box)"
    distance = getPlaneDistance(vals.planeParam, x, y, z)
    upper, lower = vals.switchBoxParam

    if distance >= lower and distance <= upper:
        vals.inSwitchBox = True
    else:
        vals.inSwitchBox = False


def clientMouseActivities(pygame, rpt, m, k):
    if vals.newClick_flg:
        m.click(vals.traceX, vals.traceY)
        vals.newClick_flg = 0
        print "CLICKED!"


def mouseActivities(pygame, rpt, tipIndex,tipThumb,kIndex,kThumb,m,k):
#3D Distance from the tipIndex to tipThumb
    dist3D=euclidean(rpt[tipIndex],rpt[tipThumb])
    vals.dist3D=dist3D   
    
#Distance for switching modes
    dista=fun.distanceVec(\
    [rpt[tipIndex][0]],\
    [rpt[tipIndex][1]],\
    [rpt[tipThumb][0]],\
    [rpt[tipThumb][1]])

    vals.tipDistance=dista[0]

#Distance for clicking - thumb tip to index knuckle
    distClick=fun.distanceVec(\
    [rpt[kIndex][0]],\
    [rpt[kIndex][1]],\
    [rpt[tipThumb][0]],\
    [rpt[tipThumb][1]])

    vals.clickDistance=distClick[0]


#Modifying vals.mouseModeValue with respect to distance between knuckles
   # currentKnuckleValue=fun.distanceVec(\
   # [rpt[kIndex][0]],\
   # [rpt[kIndex][1]],\
   # [rpt[kThumb][0]],\
   # [rpt[kThumb][1]])[0]

   # knuckleRatio=float(currentKnuckleValue/vals.knuckleValue)
   # if knuckleRatio>1:
   #     newMouseModeValue=int(knuckleRatio*vals.mouseModeValue)
   #     newClickValue=int(knuckleRatio*vals.clickValue)
   # else:
    newMouseModeValue=vals.mouseModeValue
    newClickValue=vals.clickValue

    smoothTipIndex = np.mean(fun.smooth(vals.depthBuff[2].data, window_len = vals.depthBuff[2].size()))
    checkSwitchBox(rpt[tipIndex][0], rpt[tipIndex][1], smoothTipIndex)
    # inBox = doDepth.checkAllInBox() # Used to log data
    if vals.inSwitchBox:
    #Switching Modes
        #When distance tips goes below mouseModevalue, start measuring time.
        if 10<=dista[0]<=newMouseModeValue and vals.inrange==1 and vals.mouseModeSwitchTime==0:     
            vals.mouseModeSwitchTime=time.time()  

        hold5ms = (vals.timeHold<=(time.time()-vals.mouseModeSwitchTime)*1000) 
        tipInRange= (10<=dista[0]<=newMouseModeValue)
        mouseCondition= hold5ms and tipInRange# and vals.inrange==1
        #if distance is below for a certain time and all other conditions are met, then switch
        if mouseCondition and vals.mouse_flg==0 and not vals.mouseSwitched_flg:
            print('Mouse mode activated')
            vals.traceX, vals.traceY = m.position()

            vals.mouse_flg=1
            vals.mouseModeSwitchTime=0
            vals.mouseSwitched_flg=1

            try:
                vals.switchSound.play()
            except:
                pass
            # file = 'switch.mp3'
            
            # try:
            #     vals.a.play()
            # except:
            #     vals.a.load(file)
            #     vals.a.play()


        if mouseCondition and vals.mouse_flg==1 and not vals.mouseSwitched_flg:
            print('Mouse mode deactivated')
            vals.mouse_flg=0
            vals.contDist=0
            vals.mouseSwitched_flg=1

            try:
                vals.switchSound.play()
            except:
                pass

            # file = 'switch.mp3'
            # try:
            #     vals.a.play()
            # except:
            #     vals.a.load(file)
            #     vals.a.play()

        #after switching, the fingers need to part in order to reset constants.
        if (vals.mouseSwitched_flg and dista[0]>newMouseModeValue):
            vals.mouseSwitched_flg=0
            vals.mouseModeSwitchTime=0





    '''
    #Adjusting MaxBuff with respect to thumbtip and index knuckle
    # It doesn't work. Currently this method uses a larger buffer when clicking,
    # in order to avoid mistakes when getting the clickX and clickY.
    # But this method will only work when we put the cursor still on the target.
    # If we move and press 'click', it will be worse, because of its larger buffer contains
    # more wrong information.

    # Method 1: Sin
    # if vals.mouse_flg and vals.debugFlag:
    #     currBuff = vals.minBuff
    #     if distClick[0] < 0.8 * newClickValue:
    #         currBuff = vals.maxBuff            
    #     elif distClick[0] > 1.2 * newClickValue:
    #         currBuff = vals.minBuff
    #     else:
    #         currBuff = (vals.maxBuff + vals.minBuff)/2 - (vals.maxBuff - vals.minBuff)/2 * \
    #         np.sin((distClick[0] - newClickValue) * 2 * np.pi / 0.8 / newClickValue)
    #     vals.buff[0].setCurrBuff(currBuff)
    #     vals.buff[1].setCurrBuff(currBuff)

    #    a=40*newClickValue
    #    vals.maxBuff=a/distClick[0]
    #    if vals.maxBuff<20:
    #        vals.maxBuff=20
    #    elif vals.maxBuff>40:
    #        vals.maxBuff=40
    '''
    
    # Clicking and Dragging
    if vals.mouseState == vals.MOUSE_NORMAL:
        # print 'NORMAL'
        #print distClick[0], vals.inrange, vals.mouse_flg
        if distClick[0] <= newClickValue and vals.inrange and vals.mouse_flg:
            # Get possible point of click or drag
            vals.clickX, vals.clickY = vals.traceX, vals.traceY
            # vals.clickX = np.mean(fun.smooth(vals.buff[0].data, window_len=len(vals.buff[0].data)))
            # vals.clickY = np.mean(fun.smooth(vals.buff[1].data, window_len=len(vals.buff[1].data)))
            vals.dragX, vals.dragY = vals.clickX, vals.clickY

            vals.stime = time.time()
            vals.mouseState = vals.MOUSE_READY
            #vals.mouseActBuff = [[], []]
            print 'READY'
            print 'distClick[0]: ' + str(distClick[0])

    elif vals.mouseState == vals.MOUSE_READY:
        # print 'READY'
        currTime = (time.time() - vals.stime) * float(1000)
        # Note: We don't need to add time threshold here to do READY -> CLICK.
        # Because the point is discrete, it may jump from the READY rectangle to NORMAL without
        # triggering CLICK or DRAG signal. That is, its distClick < clickValue and time < timeThre for
        # the last point, but distClick > clickValue and time > timeThre for the current point.
        # In this case, we assume that is a CLICK. Noted by Zhen Li, Aug 5th, 2014.
        if distClick[0] > newClickValue and vals.mouse_flg and vals.inrange:# and currTime <= vals.mouseActTimeThre:
            # Click
            vals.mouseState = vals.MOUSE_CLICK
            # if not vals.testTypeFlag:
            #     m.click(vals.clickX, vals.clickY)

            # Detect double click:
            clickTime = (time.time() - vals.lastClickTime) * float(1000)
            if clickTime > vals.doubleClickTimeThre or not vals.dragFlag:
                # Click
                if not vals.testTypeFlag:
                    m.click(vals.clickX, vals.clickY)
                    vals.lastClickX, vals.lastClickY = vals.clickX, vals.clickY
                    print('Click')

                    try:
                        vals.clickSound.play()
                    except:
                        pass

                    # file = 'click.mp3'    
                    # try:
                    #     vals.b.play()
                    # except:
                    #     vals.b.load(file)
                    #     vals.b.play()

            else:
                # Double Click
                if not vals.testTypeFlag:
                    m.click(vals.lastClickX, vals.lastClickY)
                    print('Double Click')

                    try:
                        vals.clickSound.play()
                    except:
                        pass

                    # file = 'click.mp3'    
                    # try:
                    #     vals.b.play()
                    # except:
                    #     vals.b.load(file)
                    #     vals.b.play()

            vals.lastClickTime = time.time()
            # print('Click')
            print 'distClick[0]: ' + str(distClick[0])

        elif distClick[0] <= newClickValue and vals.mouse_flg and vals.inrange and currTime > vals.mouseActTimeThre:
            # Drag if enabled
            if not vals.testTypeFlag:
                if vals.dragFlag:
                    m.press(vals.dragX, vals.dragY)
                else:
                    m.click(vals.clickX, vals.clickY)
                    try:
                        vals.clickSound.play()
                    except:
                        pass
            vals.mouseState = vals.MOUSE_DRAG
            print('Drag')
            print 'distClick[0]: ' + str(distClick[0])

    elif vals.mouseState == vals.MOUSE_CLICK:
        # print 'CLICK'
        # vals.mouseState = vals.MOUSE_NORMAL
        vals.mouseState = vals.MOUSE_WAIT

    elif vals.mouseState == vals.MOUSE_WAIT:
        if distClick[0] > 1.5 * newClickValue and vals.mouse_flg and vals.inrange:
            vals.mouseState = vals.MOUSE_NORMAL

    elif vals.mouseState == vals.MOUSE_DRAG:
        # print 'DRAG'
        if distClick[0] > newClickValue and vals.mouse_flg:
            # Release if enabled
            if vals.dragFlag and not vals.testTypeFlag:
                m.release(vals.buff[0].mean(),vals.buff[1].mean())
            vals.mouseState = vals.MOUSE_NORMAL
            print("Release")
            print 'distClick[0]: ' + str(distClick[0])

    if vals.testTypeFlag or vals.testPointFlag:
        ''' TODO: convert them to actual coordinate on the display.'''
        tIX, tIY = finger2Mouse(rpt[tipIndex][0], rpt[tipIndex][1])
        kIX, kIY = finger2Mouse(rpt[kIndex][0], rpt[kIndex][1])
        tTX, tTY = finger2Mouse(rpt[tipThumb][0], rpt[tipThumb][1])
        kTX, kTY = finger2Mouse(rpt[kThumb][0], rpt[kThumb][1])
        smoothX, smoothY = vals.traceX, vals.traceY
        # smoothX = np.mean(fun.smooth(vals.buff[0].data, window_len=len(vals.buff[0].data)))
        # smoothY = np.mean(fun.smooth(vals.buff[1].data, window_len=len(vals.buff[1].data)))

        # time, dista0, distClick0, inrange, inBox
        # tIX, tIY, kIX, kIY, tTX, tTY, kTX, kTY, smoothX, smoothY
        # mouse_flg, mouseState, clickX, clickY, speed, buffSize
        vals.testTypeData.append('{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}'.format(\
            str(time.time() - vals.testStartTime), str(dista[0]), str(distClick[0]), str(int(vals.inrange)), str(int(vals.inSwitchBox)), \
            str(tIX), str(tIY), str(kIX), str(kIY), str(tTX), str(tTY), str(kTX), str(kTY), str(smoothX), str(smoothY), \
            str(vals.mouse_flg), str(vals.mouseState), str(vals.clickX), str(vals.clickY), str(vals.smoothSpeed), str(vals.buff[0].size())
            ))



