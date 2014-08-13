import pygame
from pygame.locals import *
import time
import numpy as np

import constants as vals
import doDepth
import funcs as fun
from funcs import Reader


def drawAllRecording(screen, rpt, rpt2, tipThumb,tipThumb2, kThumb,kThumb2, tipIndex,tipIndex2,kIndex,kIndex2,averageX,averageY,averageX2,averageY2,myfont, calibFont,depthFont):
#     screen.fill(vals.black)
    if not vals.testTypeFlag:
    # Normal Recording Mode
        mouseLabel=myfont.render("Mouse:"+" "+str(vals.mouseModeValue) ,1,(255,255,255))
        screen.blit(mouseLabel,(0,80))
        clickLabel=myfont.render("Click:"+" "+str(vals.clickValue) ,1,(255,255,255))
        screen.blit(clickLabel,(0,95))        

        Calib1=calibFont.render("tipThumb:"+str(int(vals.depthBuff[0].mean())),1,vals.white)
        screen.blit(Calib1,(0,115))

        Calib2=calibFont.render("kThumb:"+str(int(vals.depthBuff[1].mean())),1,vals.white)
        screen.blit(Calib2,(0,135))

        Calib3=calibFont.render("tipIndex:"+str(int(vals.depthBuff[2].mean())),1,vals.white)
        screen.blit(Calib3,(0,155))
        
        Calib4=calibFont.render("kIndex:"+str(int(vals.depthBuff[3].mean())),1,vals.white)
        screen.blit(Calib4,(0,175))

        tipDistance=calibFont.render("Switch-Distance:"+str(int(vals.tipDistance)),1,vals.white)
        screen.blit(tipDistance,(0,205))

        clickDistance=calibFont.render("Click-Distance:"+str(int(vals.clickDistance)),1,vals.white)
        screen.blit(clickDistance,(0,235))
        
        distance3D=calibFont.render("3D-Distance:"+str(int(vals.dist3D)),1,vals.white)
        screen.blit(distance3D,(0,255))

        box3D=calibFont.render(str(int(vals.boxLimit)),1,vals.white)
        screen.blit(box3D,(0,285))

#Circles to check on mode switching
        if doDepth.checkAllInBox(): # Used to log data
            pygame.draw.circle(screen, vals.green, (10,325),10)
        else:
            pygame.draw.circle(screen, vals.red, (10,325),10)

        inBox=calibFont.render("in 3dBox",1,vals.white)
        screen.blit(inBox,(20,325))

        if (vals.inrange==1):
            pygame.draw.circle(screen, vals.green, (10,345),10)
        else:
            pygame.draw.circle(screen, vals.red, (10,345),10)
        
        inBox=calibFont.render("inrange",1,vals.white)
        screen.blit(inBox,(20,345))

        if (not vals.mouseSwitched_flg): # Used to log data
            pygame.draw.circle(screen, vals.green, (10,365),10)
        else:
            pygame.draw.circle(screen, vals.red, (10,365),10)
        
        inBox=calibFont.render("open tips",1,vals.white)
        screen.blit(inBox,(20,365))

    #main circles
        pygame.draw.circle(screen, vals.red, (rpt[tipIndex][0]/3,rpt[tipIndex][1]/3),10)
        pygame.draw.circle(screen, vals.blue, (rpt[kIndex][0]/3,rpt[kIndex][1]/3),10)
        pygame.draw.circle(screen, vals.green, (rpt[tipThumb][0]/3,rpt[tipThumb][1]/3),10)
        pygame.draw.circle(screen, vals.white, (rpt[kThumb][0]/3,rpt[kThumb][1]/3),10)

        pygame.draw.circle(screen, vals.gray, (averageX/3,averageY/3),13)
        pygame.draw.circle(screen, vals.gray, (averageX2/3,averageY2/3),13)

        pygame.draw.circle(screen, vals.red, (rpt2[tipIndex2][0]/3,rpt2[tipIndex2][1]/3),10)
        pygame.draw.circle(screen, vals.blue, (rpt2[kIndex2][0]/3,rpt2[kIndex2][1]/3),10)
        pygame.draw.circle(screen, vals.green, (rpt2[tipThumb2][0]/3,rpt2[tipThumb2][1]/3),10)
        pygame.draw.circle(screen, vals.white, (rpt2[kThumb2][0]/3,rpt2[kThumb2][1]/3),10)

    #GUI for depth
        # pygame.draw.rect(screen, vals.gray, (500,0,1500,1500))
        depthGUILeft = int(vals.width * 0.35)
        depthGUITop = int(vals.height * 0.05)
        depthGUIWidth = int(vals.width * 0.45) - depthGUILeft
        depthGUIHeight = int(vals.height * 0.95) - depthGUITop
        pygame.draw.rect(screen, vals.gray, (depthGUILeft, depthGUITop, depthGUIWidth, depthGUIHeight))
        
        # 0left--1startPos--2green--3white--4red--5blue--6endPos--7label--8right
        objXPos = np.linspace(depthGUILeft, depthGUILeft + depthGUIWidth, 9)
        objXPos = [int(x) for x in objXPos]
        #Creating the lines
        for i in xrange(11):
            offsetY = 75
            startPos = (objXPos[1], offsetY + i*30)      # was 550
            endPos = (objXPos[6], offsetY + i*30)      # was 650 
            pygame.draw.line(screen, vals.black, startPos, endPos)
            depthLabel = depthFont.render( str(5*i), 1, vals.black)
            screen.blit(depthLabel, (objXPos[7], offsetY + i*30))
        #Depth circles. Was 560, 580, 600, 620
        pygame.draw.circle(screen, vals.green, (objXPos[2], int(75 + vals.depthBuff[0].mean()*6)), 10) #tipThumb
        pygame.draw.circle(screen, vals.white, (objXPos[3], int(75 + vals.depthBuff[1].mean()*6)), 10) #kThumb
        pygame.draw.circle(screen, vals.red, (objXPos[4], int(75 + vals.depthBuff[2].mean()*6)), 10) #tipindex
        pygame.draw.circle(screen, vals.blue, (objXPos[5], int(75 + vals.depthBuff[3].mean()*6)), 10)#kIndex

    #The gesture bounds
        pygame.draw.line(screen,vals.red, (vals.gestureLeftThreshHold/3,0),(vals.gestureLeftThreshHold/3,800))
        pygame.draw.line(screen,vals.blue, (0,vals.gestureDownThreshHold/3),(10000,vals.gestureDownThreshHold/3))
        pygame.draw.line(screen,vals.yellow, (0,vals.gestureUpThreshHold/3),(10000,vals.gestureUpThreshHold/3))
    #Mouses mode drawing
        if vals.mouse_flg:
            MouseKeyboard=myfont.render( "Mouse mode",1,(255,255,255))
        else:
            MouseKeyboard=myfont.render( "Keyboard mode",1,(255,255,255))
        screen.blit(MouseKeyboard,(0,50))

        #input rectangle
        pygame.draw.line(screen,vals.white, (vals.inputX1/3,vals.inputY1/3), (vals.inputX2/3,vals.inputY1/3))
        pygame.draw.line(screen,vals.white, (vals.inputX2/3,vals.inputY1/3), (vals.inputX2/3,vals.inputY2/3))
        pygame.draw.line(screen,vals.white, (vals.inputX2/3,vals.inputY2/3), (vals.inputX1/3,vals.inputY2/3))
        pygame.draw.line(screen,vals.white, (vals.inputX1/3,vals.inputY2/3), (vals.inputX1/3,vals.inputY1/3))
        
    else:
    # Testing Recording Mode: Show article text.
    # I canceled the text input area.

        testFont = 'textFiles/MonospaceTypewriter.ttf'
        # Text GUI on the left: show the text
        
        if vals.textContent == '':
        # Read from file        
            try:
                tcf = open(vals.textContentFile, 'r')
                vals.textContent = tcf.read()
                tcf.close()

                print vals.textContent
            except:
                print 'Error: Invalid type content file.'

        
        textGUILeft = int(vals.width * 0.05)
        textGUITop = int(vals.height * 0.05)
        textGUIWidth = int(vals.width * 0.45) - textGUILeft
        textGUIHeight = int(vals.height * 0.95) - textGUITop
        pygame.draw.rect(screen, vals.white, (textGUILeft, textGUITop, textGUIWidth, textGUIHeight))

        if vals.textGUI == None:
            textFontSize = 20
            textBorder = 10

            vals.textGUI = Reader(unicode(vals.textContent.expandtabs(4), 'utf8'), (textGUILeft + textBorder, textGUITop + textBorder), \
                textGUIWidth - 2 * textBorder, textFontSize, height = textGUIHeight - 2 * textBorder, \
                font = testFont, fgcolor = (0, 0, 0), hlcolor = (255,10,150,100), split = True)

        vals.textGUI.show()

        '''
        # Type GUI on the right: input area        

        typeGUILeft = int(vals.width * 0.55)
        typeGUITop = int(vals.height * 0.05)
        typeGUIWidth = int(vals.width * 0.95) - typeGUILeft
        typeGUIHeight = int(vals.height * 0.95) - typeGUITop
        pygame.draw.rect(screen, vals.white, (typeGUILeft, typeGUITop, typeGUIWidth, typeGUIHeight))

        if vals.typeGUI == None:
            typeFontSize = 15
            typeBorder = 10

            typeFont = pygame.font.Font(testFont, typeFontSize)
            vals.typeGUI = Input(x = typeGUILeft + typeBorder, y = typeGUITop + typeBorder, \
                font = typeFont, color = (255, 255, 255))

        vals.typeGUI.draw(screen)
        pygame.display.flip()
        '''

def drawAllCalibration(screen, rpt, tipIndex, tipThumb,kThumb,kIndex,rpt2,tipIndex2, tipThumb2,kThumb2,kIndex2,averageX,averageY,myfont,calibFont,depthFont):
    mouseModeDistance=fun.distanceVec(\
        [rpt[tipIndex][0]],\
        [rpt[tipIndex][1]],\
        [rpt[tipThumb][0]],\
        [rpt[tipThumb][1]])

    clickingDistance=fun.distanceVec(\
        [rpt[kIndex][0]],\
        [rpt[kIndex][1]],\
        [rpt[tipThumb][0]],\
        [rpt[tipThumb][1]])


    screen.fill(vals.black)
    #Drawing the Circles
    pygame.draw.circle(screen, vals.yellow, (rpt[tipIndex][0]/3,rpt[tipIndex][1]/3),10)
    pygame.draw.circle(screen, vals.red, (rpt[kIndex][0]/3,rpt[kIndex][1]/3),10)
    pygame.draw.circle(screen, vals.green, (rpt[tipThumb][0]/3,rpt[tipThumb][1]/3),10)
    pygame.draw.circle(screen, vals.blue, (rpt[kThumb][0]/3,rpt[kThumb][1]/3),10)
    pygame.draw.circle(screen, vals.white, (averageX/3,averageY/3),10)

    #Drawing the instructions
    pygame.draw.rect(screen, vals.gray, (0,5,600,60))
    if vals.calibState == vals.START_CALIB:
        Calib1=calibFont.render("Press H to start",1,vals.black)
        screen.blit(Calib1,(0,15))

    elif vals.calibState == vals.MOUSE_MODE_CALIB:
        Calib1=calibFont.render("Tap tip of thumb and tip of index",1,vals.black)
        screen.blit(Calib1,(0,15))
        Calib2=calibFont.render("Press H to complete",1,vals.black)
        screen.blit(Calib2,(0,35))
        pygame.draw.line(screen,vals.white,(rpt[tipThumb][0]/3,rpt[tipThumb][1]/3),(rpt[tipIndex][0]/3,rpt[tipIndex][1]/3),5 )
        vals.mouseModeCalibList.append(mouseModeDistance[0])     
        doDepth.findingDepth(rpt, rpt2, tipThumb,tipThumb2, kThumb,kThumb2, tipIndex,tipIndex2,kIndex,kIndex2)
        vals.boxBoundCalibList.append(doDepth.meanDepth())        

    elif vals.calibState == vals.CLICK_CALIB:
        Calib1=calibFont.render("Tap tip of thumb and knuckle of index for {} times".format(\
            str(vals.clickNum)), 1, vals.black)
        screen.blit(Calib1,(0,15))
        Calib2=calibFont.render("Press H to complete",1,vals.black)
        screen.blit(Calib2,(0,35))
        pygame.draw.line(screen,vals.white,(rpt[tipThumb][0]/3,rpt[tipThumb][1]/3),(rpt[kIndex][0]/3,rpt[kIndex][1]/3),5 )
        vals.clickingCalibList[0].append(time.time() - vals.clickCalibSTime)
        vals.clickingCalibList[1].append(clickingDistance[0]) 

                      
    elif vals.calibState == vals.END_CALIB:
        calibrationDone=1
        Calib1=calibFont.render("Calibration Completed",1,vals.black)
        screen.blit(Calib1,(0,15))
        Calib2=calibFont.render("Press r to start recording",1,vals.black)
        screen.blit(Calib2,(0,35))


def drawAllMiniRecording(screen, rpt, rpt2, tipThumb,tipThumb2, kThumb,kThumb2, tipIndex,tipIndex2,kIndex,kIndex2,averageX,averageY,myfont, calibFont,depthFont):
    screen.fill(vals.black)

#main circles
    pygame.draw.circle(screen, vals.red, (rpt[tipIndex][0]/10,rpt[tipIndex][1]/10),2)
    pygame.draw.circle(screen, vals.blue, (rpt[kIndex][0]/10,rpt[kIndex][1]/10),2)
    pygame.draw.circle(screen, vals.green, (rpt[tipThumb][0]/10,rpt[tipThumb][1]/10),2)
    pygame.draw.circle(screen, vals.white, (rpt[kThumb][0]/10,rpt[kThumb][1]/10),2)

    pygame.draw.circle(screen, vals.gray, (averageX/10,averageY/10),4)

    pygame.draw.circle(screen, vals.red, (rpt2[tipIndex2][0]/10,rpt2[tipIndex2][1]/10),2)
    pygame.draw.circle(screen, vals.blue, (rpt2[kIndex2][0]/10,rpt2[kIndex2][1]/10),2)
    pygame.draw.circle(screen, vals.green, (rpt2[tipThumb2][0]/10,rpt2[tipThumb2][1]/10),2)
    pygame.draw.circle(screen, vals.white, (rpt2[kThumb2][0]/10,rpt2[kThumb2][1]/10),2)
#The gesture bounds
    pygame.draw.line(screen,vals.white, (vals.gestureRightThreshHold/10,0),(vals.gestureRightThreshHold/10,800))
    pygame.draw.line(screen,vals.red, (vals.gestureLeftThreshHold/10,0),(vals.gestureLeftThreshHold/10,800))
    pygame.draw.line(screen,vals.blue, (0,vals.gestureDownThreshHold/10),(10000,vals.gestureDownThreshHold/10))
    pygame.draw.line(screen,vals.yellow, (0,vals.gestureUpThreshHold/10),(10000,vals.gestureUpThreshHold/10))
#Mouses mode drawing
    if vals.mouse_flg:
        MouseKeyboard=myfont.render("M",1,(255,255,255))
    else:
        MouseKeyboard=myfont.render( "K",1,(255,255,255))
    screen.blit(MouseKeyboard,(0,0))



def drawAllMiniCalibration(screen, rpt, tipIndex, tipThumb,kThumb,kIndex,averageX,averageY,myfont,calibFont,depthFont):
    mouseModeDistance=fun.distanceVec(\
        [rpt[tipIndex][0]],\
        [rpt[tipIndex][1]],\
        [rpt[tipThumb][0]],\
        [rpt[tipThumb][1]])

    clickingDistance=fun.distanceVec(\
        [rpt[kIndex][0]],\
        [rpt[kIndex][1]],\
        [rpt[tipThumb][0]],\
        [rpt[tipThumb][1]])

    screen.fill(vals.black)
    #Drawing the Circles
    pygame.draw.circle(screen, vals.yellow, (rpt[tipIndex][0]/10,rpt[tipIndex][1]/10),2)
    pygame.draw.circle(screen, vals.red, (rpt[kIndex][0]/10,rpt[kIndex][1]/10),2)
    pygame.draw.circle(screen, vals.green, (rpt[tipThumb][0]/10,rpt[tipThumb][1]/10),2)
    pygame.draw.circle(screen, vals.blue, (rpt[kThumb][0]/10,rpt[kThumb][1]/10),2)
    pygame.draw.circle(screen, vals.white, (averageX/10,averageY/10),3)

    if not (vals.mouseModeCalib or vals.startClickModeCalib or vals.startMouseModeCalib or vals.clickingCalib):
        print "Press H to start"
    if vals.startMouseModeCalib and not vals.mouseModeCalib:
        print "Tap tip of thumb and tip of index"
        print "Press H to complete"
        pygame.draw.line(screen,vals.white,(rpt[tipThumb][0]/10,rpt[tipThumb][1]/10),(rpt[tipIndex][0]/10,rpt[tipIndex][1]/10),2 )
        vals.mouseModeCalibList.append(mouseModeDistance[0])                
    if vals.startClickModeCalib and not vals.clickingCalib:
        print "Tap tip of thumb and knuckle of index"
        print "Press H to complete"
        pygame.draw.line(screen,vals.white,(rpt[tipThumb][0]/10,rpt[tipThumb][1]/10),(rpt[kIndex][0]/10,rpt[kIndex][1]/10),2 )
        vals.clickingCalibList.append(clickingDistance[0])                    
    if vals.mouseModeCalib and vals.clickingCalib:
        print "Calibration Completed"
        print "Press r to start recording"
        calibrationDone=1

def drawDefault(screen, defaultFont):
    screen.fill(vals.black)

    #Drawing the instructions
    pygame.draw.rect(screen, vals.gray, (5, 5, 500, 90))
    default1 = defaultFont.render('press "l" to load calibration data,', 1, vals.black)
    screen.blit(default1, (10, 15))
    default2 = defaultFont.render('or press "c" to calibrate,', 1, vals.black)
    screen.blit(default2, (10, 35))
    default3 = defaultFont.render('then press "r" to start recording.', 1, vals.black)
    screen.blit(default3, (10, 55))


def drawInputCalibration(screen, rpt, tipIndex, tipThumb,kThumb,kIndex,rpt2,tipIndex2, tipThumb2,kThumb2,kIndex2,averageX,averageY,myfont,calibFont,depthFont):
    mouseModeDistance=fun.distanceVec(\
        [rpt[tipIndex][0]],\
        [rpt[tipIndex][1]],\
        [rpt[tipThumb][0]],\
        [rpt[tipThumb][1]])

    clickingDistance=fun.distanceVec(\
        [rpt[kIndex][0]],\
        [rpt[kIndex][1]],\
        [rpt[tipThumb][0]],\
        [rpt[tipThumb][1]])


    screen.fill(vals.black)
    #Drawing the Circles
    pygame.draw.circle(screen, vals.yellow, (rpt[tipIndex][0]/3,rpt[tipIndex][1]/3),10)
    pygame.draw.circle(screen, vals.red, (rpt[kIndex][0]/3,rpt[kIndex][1]/3),10)
    pygame.draw.circle(screen, vals.green, (rpt[tipThumb][0]/3,rpt[tipThumb][1]/3),10)
    pygame.draw.circle(screen, vals.blue, (rpt[kThumb][0]/3,rpt[kThumb][1]/3),10)
    pygame.draw.circle(screen, vals.white, (averageX/3,averageY/3),10)

    #Drawing the instructions
    pygame.draw.rect(screen, vals.gray, (0,5,600,60))
    if vals.inputCounter == 0:
        Calib1=calibFont.render("Tap thumb tip and index knuckle to set top left point",1,vals.black)
        screen.blit(Calib1,(0,15))

    elif vals.inputCounter==1:
        Calib1=calibFont.render("Tap thumb tip and index knuckle to set bottom right point",1,vals.black)
        screen.blit(Calib1,(0,15))
        #this draws the line
        pygame.draw.line(screen,vals.white,(vals.inputX1/3,vals.inputY1/3),(rpt[tipIndex][0]/3,rpt[tipIndex][1]/3),5 )

    elif vals.inputSet:
        Calib2=calibFont.render("Press r to start recording",1,vals.black)
        screen.blit(Calib2,(0,35))
        pygame.draw.line(screen,vals.white,(vals.inputX1/3,vals.inputY1/3),(vals.inputX2/3,vals.inputY2/3),5)
        pygame.draw.rect(screen, vals.white, (vals.inputX1/3, vals.inputY1/3, (vals.inputX2-vals.inputX1)/3, (vals.inputY2-vals.inputY1)/3))
