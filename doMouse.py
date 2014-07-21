from scipy.spatial.distance import euclidean 
import constants as vals
import funcs as fun
import time
import numpy as np
import doDepth

def mouseActivities(rpt, tipIndex,tipThumb,kIndex,kThumb,m,k):
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


    if doDepth.checkAllInBox():
    #Switching Modes
        #When distance tips goes below mouseModevalue, start measuring time.
        if 10<=dista[0]<=newMouseModeValue and vals.inrange==1 and vals.mouseModeSwitchTime==0:     
            vals.mouseModeSwitchTime=time.time()  

        hold5ms = (vals.timeHold<=(time.time()-vals.mouseModeSwitchTime)*1000) 
        tipInRange= (10<=dista[0]<=newMouseModeValue)
        mouseCondition= hold5ms and tipInRange and vals.inrange==1
        #if distance is below for a certain time and all other conditions are met, then switch
        if mouseCondition and vals.mouse_flg==0 and not vals.mouseSwitched_flg:
            print('Mouse mode activated')
            vals.mouse_flg=1
            vals.mouseModeSwitchTime=0
            vals.mouseSwitched_flg=1
        if mouseCondition and vals.mouse_flg==1 and not vals.mouseSwitched_flg:
            print('Mouse mode deactivated')
            vals.mouse_flg=0
            vals.contDist=0
            vals.mouseSwitched_flg=1
        #after switching, the fingers need to part in order to reset constants.
        if (vals.mouseSwitched_flg and dista[0]>newMouseModeValue):
            vals.mouseSwitched_flg=0
            vals.mouseModeSwitchTime=0

#Adjusting MaxBuff with respect to thumbtip and index knuckle
    #if vals.mouse_flg:
    #    a=40*newClickValue
    #    vals.maxBuff=a/distClick[0]
    #    if vals.maxBuff<20:
    #        vals.maxBuff=20
    #    elif vals.maxBuff>40:
    #        vals.maxBuff=40
    
    # Clicking and Dragging
    if vals.mouseState == vals.MOUSE_NORMAL:
        # print 'NORMAL'
        #print distClick[0], vals.inrange, vals.mouse_flg
        if distClick[0] <= newClickValue and vals.inrange and vals.mouse_flg:
            # Get possible point of click or drag
            vals.clickX, vals.clickY = vals.buff[0].mean(), vals.buff[1].mean()
            vals.dragX, vals.dragY = vals.buff[0].mean(), vals.buff[1].mean()

            vals.stime = time.time()
            vals.mouseState = vals.MOUSE_CLICK_READY
            #vals.mouseActBuff = [[], []]
            print 'NORMAL -> READY'
            print 'distClick[0]: ' + str(distClick[0])

    elif vals.mouseState == vals.MOUSE_CLICK_READY:
        # print 'READY'
        currTime = (time.time() - vals.stime) * float(1000)
        if distClick[0] > newClickValue and vals.mouse_flg and  currTime <= vals.mouseActTimeThre:
            # Click
            vals.mouseState = vals.MOUSE_CLICK
            m.click(vals.clickX, vals.clickY)
            print('Click')
            print 'distClick[0]: ' + str(distClick[0])

        elif distClick[0] <= newClickValue and vals.mouse_flg and currTime > vals.mouseActTimeThre:
            # Drag
            vals.mouseState = vals.MOUSE_DRAG
            m.press(vals.dragX, vals.dragY)
            print('Drag')
            print 'distClick[0]: ' + str(distClick[0])

    elif vals.mouseState == vals.MOUSE_CLICK:
        # print 'CLICK'
        vals.mouseState = vals.MOUSE_NORMAL

    elif vals.mouseState == vals.MOUSE_DRAG:
        # print 'DRAG'
        if distClick[0] > newClickValue * 1.2 and vals.mouse_flg:
            vals.mouseState = vals.MOUSE_NORMAL
            m.release(vals.buff[0].mean(),vals.buff[1].mean())
            print("Release")
            print 'distClick[0]: ' + str(distClick[0])


'''
# Old logic of click and drag.
# Problem: always click before drag.
    
    if distClick[0]<newClickValue and vals.inrange and vals.mouse_flg and not vals.click_flg:
        vals.click_flg=1
        vals.stime=time.time()
        try:
            m.click(vals.buff[0].mean(),vals.buff[1].mean())
            vals.dragX, vals.dragY=vals.buff[0].mean(),vals.buff[1].mean()
        except:
            pass
        print('Click')
        print distClick[0]
        clickDistFile = open('clickDistFile.txt', 'a')
        print >> clickDistFile, 'Click'
        clickDistFile.close()
        # vals.mouseClickBuff = [[], []]
        # clickPntFile = open('clickPntFile.txt', 'a')
        # print >> clickPntFile, 'Click:['
        # clickPntFile.close()
    if (vals.click_flg and (time.time()-vals.stime)*1000>=vals.lagValue and not vals.drag_flg): #so its been 1/2 second, 
        if (distClick[0]>=newClickValue): #if finger is up, then delete flag. Else 
            vals.click_flg=0
            vals.drag_flg=0
            print("reset")
            print distClick[0]
            clickDistFile = open('clickDistFile.txt', 'a')
            print >> clickDistFile, 'EndClick'
            clickDistFile.close()
            # clickPntFile = open('clickPntFile.txt', 'a')
            # print >> clickPntFile, '] Click End'
            # print >> clickPntFile, 'mean:{}, {}, var:{}, {}'.format(np.mean(vals.mouseClickBuff[0]), np.mean(vals.mouseClickBuff[1]),\
            #     np.var(vals.mouseClickBuff[0]), np.var(vals.mouseClickBuff[1]))
            # clickPntFile.close()
        elif ((vals.dragX-vals.buff[0].mean()>5) or (vals.dragY-vals.buff[1].mean()>5)): #Drag situation
            m.press(vals.dragX,vals.dragY)
            vals.drag_flg=1
            print ("dragging")
            print distClick[0]
            # clickDistFile = open('clickDistFile.txt', 'a')
            # print >> clickDistFile, 'Drag'
            # clickDistFile.close()
            # clickPntFile = open('clickPntFile.txt', 'a')
            # print >> clickPntFile, 'Drag:['
            # clickPntFile.close()
    if vals.drag_flg and distClick[0]>=int(1.2*newClickValue): #released the drag
        vals.drag_flg=0
        m.release(vals.buff[0].mean(),vals.buff[1].mean())
        vals.dragX,vals.dragY=0,0
        print("release drag")
        print distClick[0]
        # clickDistFile = open('clickDistFile.txt', 'a')
        # print >> clickDistFile, 'EndDrag'
        # clickDistFile.close()
        # clickPntFile = open('clickPntFile.txt', 'a')
        # print >> clickPntFile, '] Drag End'
        # print >> clickPntFile, 'mean:{}, {}, var:{}, {}'.format(np.mean(vals.mouseClickBuff[0]), np.mean(vals.mouseClickBuff[1]),\
        #         np.var(vals.mouseClickBuff[0]), np.var(vals.mouseClickBuff[1]))
        # clickPntFile.close()
    if vals.mouse_flg:
        if vals.click_flg or vals.drag_flg:
            clickDistFile = open('clickDistFile.txt', 'a')
            print >> clickDistFile, '{},{}'.format(str(distClick[0]), str(time.time()-vals.stime))
            clickDistFile.close()
            # currX, currY = vals.buff[0].data[-1], vals.buff[1].data[-1]
            # vals.mouseClickBuff[0].append(currX)
            # vals.mouseClickBuff[1].append(currY)
            # clickPntFile = open('clickPntFile.txt', 'a')
            # print >> clickPntFile, 'mean:{},{} ### curr:{}, {} ### time:{}'.format(\
            #     vals.buff[0].mean(), vals.buff[1].mean(), currX, currY, (time.time()-vals.stime))
            # clickPntFile.close()

'''



"""
##################implement click with finger movement Still testing#################################
    if vals.inrange and vals.mouse_flg and not vals.click_flg and not vals.yeah_flg: #raise flg and store current values
        vals.ASDFTTD=vals.depthBuff[0].mean()
        vals.ASDFTKD=vals.depthBuff[1].mean()
        vals.ASDFITD=vals.depthBuff[2].mean()
        vals.ASDFIKD=vals.depthBuff[3].mean()
        vals.yeah_flg=1
        print "yeah"

#         if vals.mouse_flg:        
#             print vals.depthBuff[0].mean(), ASDFTTD

    if vals.inrange and vals.mouse_flg and not vals.click_flg and vals.yeah_flg and (vals.depthBuff[0].mean()-vals.ASDFTTD<-3):
        vals.ASDFTTD=vals.depthBuff[0].mean()
        print "oh yeah"

    if vals.oh_yeah_flg and not vals.click_flg and (vals.depthBuff[0].mean()-vals.ASDFTTD>3):
        vals.click_flg=1
        vals.yeah_flg=0
        vals.oh_yeah_flg=0
        vals.stime=time.time()
        m.click(vals.buff[0].mean(),vals.buff[1].mean())
        vals.dragX, vals.dragY=vals.buff[0].mean(),vals.buff[1].mean()
        print('Click with finger')
"""