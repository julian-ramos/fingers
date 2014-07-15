from scipy.spatial.distance import euclidean 
import constants as vals
import funcs as fun
import time
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



#Switching Modes
    #When distance tips goes below mouseModevalue, start measuring time.
    if 10<=dista[0]<=newMouseModeValue and vals.inrange==1 and vals.mouseModeSwitchTime==0:     
        vals.mouseModeSwitchTime=time.time()  

    #if distance is below for a certain time and all other conditions are met, then switch
    if (vals.timeHold<=(time.time()-vals.mouseModeSwitchTime)*1000) and vals.mouse_flg==0 and \
        vals.drag_flg==0 and 10<=dista[0]<=newMouseModeValue and not vals.mouseSwitched_flg:
        print('Mouse mode activated')
        vals.mouse_flg=1
        vals.mouseModeSwitchTime=0
        vals.mouseSwitched_flg=1
    if (vals.timeHold<=(time.time()-vals.mouseModeSwitchTime)*1000) and vals.mouse_flg==1 and \
                vals.drag_flg==0 and 10<=dista[0]<=newMouseModeValue and not vals.mouseSwitched_flg:
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
#Clicking
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
    if (vals.click_flg and (time.time()-vals.stime)*1000>=vals.lagValue and not vals.drag_flg): #so its been 1/2 second, 
        if (distClick[0]>=newClickValue): #if finger is up, then delete flag. Else 
            vals.click_flg=0
            vals.drag_flg=0
            print("reset")
            print distClick[0]
        elif ((vals.dragX-vals.buff[0].mean()>5) or (vals.dragY-vals.buff[1].mean()>5)): #Drag situation
            m.press(vals.dragX,vals.dragY)
            vals.drag_flg=1
            print ("dragging")
            print distClick[0]
    if vals.drag_flg and distClick[0]>=int(1.2*newClickValue): #released the drag
        vals.drag_flg=0
        m.release(vals.buff[0].mean(),vals.buff[1].mean())
        print distClick[0]
        vals.dragX,vals.dragY=0,0
        print("release drag")