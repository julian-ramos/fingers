

import constants as vals
import funcs as fun


def findingDepth(rpt, rpt2, tipThumb,tipThumb2, kThumb,kThumb2, tipIndex,tipIndex2,kIndex,kIndex2):
    focal=1380 #pixels, I found this online
    disparityTipThumb=fun.distanceVec([rpt[tipThumb][0]],[rpt[tipThumb][1]],\
                                [rpt2[tipThumb2][0]],[rpt2[tipThumb2][1]])[0]

    disparityKThumb=fun.distanceVec([rpt[kThumb][0]],[rpt[kThumb][1]],\
                                [rpt2[kThumb2][0]],[rpt2[kThumb2][1]])[0]

    disparityTipIndex=fun.distanceVec([rpt[tipIndex][0]],[rpt[tipIndex][1]],\
                                [rpt2[tipIndex2][0]],[rpt2[tipIndex2][1]])[0]

    disparityKIndex=fun.distanceVec([rpt[kIndex][0]],[rpt[kIndex][1]],\
                                [rpt2[kIndex2][0]], [rpt2[kIndex2][1]])[0]

    disparityList=[disparityTipThumb,disparityKThumb,disparityTipIndex,disparityKIndex]

    depthList=[]
    for i in xrange(len(disparityList)):    
        if disparityList[i]<1:
            depth=0
        else:
            depth=1.0*focal/disparityList[i]*3.5 #cm, the b value
        vals.depthBuff[i].put(depth)

#Some notes about depth measurement

# Z = f * b/d

#where f is the focal length, b is the baseline, or distance between the cameras, and d the disparity between corresponding points. 
#1cm=37.79527559055 pixels
#35cm=1322.834645669pixels
#6cm= 226.7716535433pixels

#35cm=f*6cm/disparity
#f=35cm/6cm*disparity    


 #lower >fingers >upper 

def checkAllInBox():
    for i in xrange(4):
        if vals.depthBuff[i].mean()<vals.boxLimit or vals.depthBuff[i].mean()>vals.boxLimitBottom:#if a single one is out of box, false
            return False;
    return True;

def checkIndexInBox(): 
    return vals.depthBuff[2].mean()>= vals.boxLimit
    #return vals.depthBuff[2].mean()<vals.boxLimit or vals.depthBuff[2].mean()>vals.boxLimitBottom

def checkAllAboveBox():
    for i in xrange(4):
        if vals.depthBuff[i].mean()>=vals.boxLimit: #if a single one is in box, false
            return False;
    return True;    

def meanDepth():
    averageDepth=0
    for i in xrange(4):
        averageDepth+=vals.depthBuff[i].mean()
    averageDepth=averageDepth/4
    return averageDepth

        """
        The following is code so that nothing will function if the depth of 
        each LED is below 25. I chose 25 as the magic number as around that 
        depth, the LEDs tend to go crazy because the Wiimotes cannot track them
        accurately. I haven't tested this value for other setups but mine.
        """
        
def checkAllAboveTwentyFive(): 
    for i in xrange(4):
        if vals.depthBuff[i].mean()<=25: #if a single one is <25, false
            return False;
    return True;  