#!/usr/bin/env python

"""
An echo server that uses threads to handle multiple clients at a time.
Entering any line of input at the terminal will exit the server.
"""

#General imports
import miniQueue as q
import numpy as np
import copy
import os
from time import sleep
import select
import socket
import sys
import threading
import pygame
from pygame.locals import *
from pymouse import PyMouse
from pykeyboard import PyKeyboard

#Own imports
import constants as vals
import findingPoints
import doMouse
import doGestures
import doEvents
import doDraw
import doDepth
import funcs as fun
import checkingInRange

def finger2Mouse(fX, fY, rectangle = False):
    " Convert the fingers coordinate to mouse coordinate "
    left = vals.leftBound
    upper = vals.upperBound
    if rectangle == False:
        left = 600
        upper = 150


    windowX=vals.windowX
    windowY=vals.windowY

    if vals.zoom_flg:
        zoomConstant=10
        windowX=zoomConstant*windowX
        windowY=zoomConstant*windowY
        print "zoom"

        mX = (fX - vals.fX) * vals.width / windowX                    
        mY = (fY - vals.fY) * vals.height / windowY
        mX=mX+vals.mouseX
        mY=mY+vals.mouseY
        return mX,mY

    mX = (fX - left) * vals.width / windowX                    
    mY = (fY - upper) * vals.height / windowY

    return mX, mY    

def finger2MouseRelative(fXList, fYList, mX0, mY0):
    " Get next mouse point(mX1, mY1) by fX/YList "

    # Restrict the valid area
    if fXList[-1] < vals.fingerStart[0] or fYList[-1] < vals.fingerStart[1]:
        [mX1, mY1] = [mX0, mY0]
        #print('1 %d %d'%(mX1,mY1))
    elif (fXList[-1] - fXList[-2])**2+(fYList[-1] - fYList[-2])**2>=2:
        mX1 = vals.relativeSpeed[0] * (fXList[-1] - fXList[-2]) + mX0
        mY1 = vals.relativeSpeed[1] * (fYList[-1] - fYList[-2]) + mY0

        mX1 = max(min(mX1, vals.width), 0)
        mY1 = max(min(mY1, vals.height), 0)
        
    else:
        [mX1, mY1] = [mX0, mY0]
        #print('2 %d %d'%(mX1,mY1))
        
    return [mX1, mY1]


def isOnKeyboard(x, y, z):
    " Check if the index tip is on the keyboard "

    if x == 0 and y == 0:
        return True

    # z = ax + by + c <=> Ax + By + Cz + D = 0, E = sqrt(A^2 + B^2 + C^2)
    A, B, C, D, E, keyboardTop = vals.planeParam
    a, b, c = -A/C, -B/C, -D/C

    distance = np.abs((A*x + B*y + C*z + D) / E)
    zi = a*x + b*y + c
    if zi < z:
        # this point is above the plane
        distance = -distance

    if distance > keyboardTop:
        ret = False
    else:
        ret = True
    return ret

class mainThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)    

    def run(self):
        global FLG, coords
        FLG=1
        m = PyMouse()
        k = PyKeyboard()
        
        #Intialization of Pygame
        pygameRate=100
        os.environ['SDL_VIDEO_iWINDOW_POS'] = "%d,%d" % (0,0)
        pygame.init()
        clock=pygame.time.Clock()
        myfont=pygame.font.SysFont("monospace",15)
        calibFont=pygame.font.SysFont("monospace",20)
        depthFont=pygame.font.SysFont("monospace",10)
        defaultFont=pygame.font.SysFont("monospace",15)

        pygame.mixer.init()
        
        infoObject = pygame.display.Info()
        vals.width = infoObject.current_w
        vals.height = infoObject.current_h
        # print width, height
        screen=pygame.display.set_mode((int(vals.width*0.5), vals.height))
        global kill
        
        
        #Main loop
        while kill==False:
            
            screen.fill((0,0,0))
            rpt=[[int(i2) for i2 in i]for i in coords[0]]
            rpt2=[[int(i2) for i2 in i]for i in coords[1]]
            
            if not vals.rec_flg and (vals.calibration or vals.calibLoadFlag): #do calibration or load from file
            #Receiving data from the threads
                newList=findingPoints.findDegrees(rpt) #returns in from [(theta1,i1),(theta2,i2)....)]
                tipIndex, tipIndexAngle, kIndex,kIndexAngle=findingPoints.indexData(newList)
                tipThumb,tipThumbAngle,kThumb,kThumbAngle=findingPoints.thumbData(newList)
                averageX,averageY=findingPoints.centerFind(rpt) #the center point
            #Find out the location of the 2nd Wiimote LEDs
                newList2=findingPoints.findDegrees(rpt2) #returns in from [(theta1,i1),(theta2,i2)....)]
                tipIndex2, tipIndexAngle2, kIndex2,kIndexAngle2=findingPoints.indexData(newList2)
                tipThumb2,tipThumbAngle2,kThumb2,kThumbAngle2=findingPoints.thumbData(newList2)
            #GUI section
                #doDraw.drawAllMiniCalibration(miniScreen, rpt, tipIndex, tipThumb,kThumb,kIndex,averageX,averageY,myfont,calibFont,depthFont)
                doDraw.drawAllCalibration(screen, rpt, tipIndex, tipThumb,kThumb,kIndex,rpt2, tipIndex2, tipThumb2,kThumb2,kIndex2, averageX,averageY,myfont,calibFont,depthFont)
            

            if vals.inputCalibration:
            #Receiving data from the threads
                newList=findingPoints.findDegrees(rpt) #returns in from [(theta1,i1),(theta2,i2)....)]
                tipIndex, tipIndexAngle, kIndex,kIndexAngle=findingPoints.indexData(newList)
                tipThumb,tipThumbAngle,kThumb,kThumbAngle=findingPoints.thumbData(newList)
                averageX,averageY=findingPoints.centerFind(rpt) #the center point
            #Find out the location of the 2nd Wiimote LEDs
                newList2=findingPoints.findDegrees(rpt2) #returns in from [(theta1,i1),(theta2,i2)....)]
                tipIndex2, tipIndexAngle2, kIndex2,kIndexAngle2=findingPoints.indexData(newList2)
                tipThumb2,tipThumbAngle2,kThumb2,kThumbAngle2=findingPoints.thumbData(newList2)
            #GUI section
                doDraw.drawInputCalibration(screen, rpt, tipIndex, tipThumb,kThumb,kIndex,rpt2, tipIndex2, tipThumb2,kThumb2,kIndex2, averageX,averageY,myfont,calibFont,depthFont)

                #first "click" get where the rpt index x,y, store it. Second click completes the line, turn into square
                distClick=fun.distanceVec(\
                [rpt[kIndex][0]],\
                [rpt[kIndex][1]],\
                [rpt[tipThumb][0]],\
                [rpt[tipThumb][1]])

                #first click
                if (distClick[0]<vals.clickValue and vals.inputCounter==0):
                    vals.inputX1=rpt[tipIndex][0]
                    vals.inputY1=rpt[tipIndex][1]
                    vals.inputCounter+=1
                    vals.inputClickStopper=1
                    print "awef"
                    print vals.inputX1,vals.inputY1
                if (distClick[0]>=vals.clickValue and vals.inputClickStopper):
                    vals.inputClickStopper=0
                
                #second click
                if (distClick[0]<vals.clickValue and vals.inputCounter==1 and not vals.inputClickStopper):
                    vals.inputX2=rpt[tipIndex][0]
                    vals.inputY2=rpt[tipIndex][1]
                    print "hey"
                    print vals.inputX2,vals.inputY2
                    vals.inputCounter+=1
                    vals.inputSet=1

                if vals.inputSet:
                    #sets the inrange constants
                    if vals.inputX1<=vals.inputX2:
                        vals.leftBound=vals.inputX1
                        vals.rightBound=vals.inputX2
                    else:
                        vals.leftBound=vals.inputX2
                        vals.rightBound=vals.inputX1                        

                    if vals.inputY1<=vals.inputY2:
                        vals.upperBound=vals.inputY1
                        vals.lowerBound=vals.inputY2
                    else:
                        vals.upperBound=vals.inputY2
                        vals.lowerBound=vals.inputY1       

                    vals.windowX = vals.rightBound - vals.leftBound
                    vals.windowY = vals.lowerBound - vals.upperBound                 
                    


            if vals.rec_flg==1: #Recording 
            #Finding out the location of the LEDs, tipThumb, kThumb....
                newList=findingPoints.findDegrees(rpt) #returns in from [(theta1,i1),(theta2,i2)....)]
                tipIndex, tipIndexAngle, kIndex,kIndexAngle=findingPoints.indexData(newList)
                tipThumb,tipThumbAngle,kThumb,kThumbAngle=findingPoints.thumbData(newList)
                averageX,averageY=findingPoints.centerFind(rpt) #the center point
            #Find out the location of the 2nd Wiimote LEDs
                newList2=findingPoints.findDegrees(rpt2) #returns in from [(theta1,i1),(theta2,i2)....)]
                tipIndex2, tipIndexAngle2, kIndex2,kIndexAngle2=findingPoints.indexData(newList2)
                tipThumb2,tipThumbAngle2,kThumb2,kThumbAngle2=findingPoints.thumbData(newList2)
                averageX2,averageY2=findingPoints.centerFind(rpt2) #the center point

            #Check whether LED is in range
                newRpt=copy.deepcopy(rpt)
                vals.rptList.append(newRpt)
                vals.inrange, vals.LED1,vals.LED2,vals.LED3,vals.LED4=checkingInRange.rangeChecker(vals.rptList, vals.LED1, vals.LED2,vals.LED3,vals.LED4)
            
                if (vals.inputX1<=rpt[tipIndex][0]<=vals.inputX2 and vals.inputY1<=rpt[tipIndex][1]<=vals.inputY2) or \
                    (vals.inputX1<=rpt2[tipIndex][0]<=vals.inputX2 and vals.inputY1<=rpt2[tipIndex][1]<=vals.inputY2):
                    vals.inrange=1

            # Check for the other wiimote
                

            #Depth
                doDepth.findingDepth(rpt, rpt2, tipThumb,tipThumb2, kThumb,kThumb2, tipIndex,tipIndex2,kIndex,kIndex2)
            #GUI
                doDraw.drawAllRecording(screen, rpt, rpt2, tipThumb,tipThumb2, kThumb,kThumb2, tipIndex,tipIndex2,kIndex,kIndex2,averageX,averageY,averageX2,averageY2,myfont,calibFont,depthFont)
                #doDraw.drawAllMiniRecording(miniScreen, rpt, rpt2, tipThumb,tipThumb2, kThumb,kThumb2, tipIndex,tipIndex2,kIndex,kIndex2,averageX,averageY,myfont,calibFont,depthFont)

                # Only log the depth data in record mode when testing or debugging
                # if vals.relativeFlag:
                #     if vals.depthBuff[2].size() > 10:
                #         smoothTipIndex = np.mean(fun.smooth(vals.depthBuff[2].data[-10:], window_len = 10))
                #     else:
                #         smoothTipIndex = np.mean(fun.smooth(vals.depthBuff[2].data, window_len = vals.depthBuff[2].size()))
                #     smoothTipIndex = vals.depthBuff[2].back()
                #     # log the depth and index tip raw coordinate
                #     vals.planeDepthData.append('{}, {}, {}, {}, {}, {}'.format(vals.depthBuff[0].back(), vals.depthBuff[1].back(), \
                #         smoothTipIndex, vals.depthBuff[3].back(), rpt[tipIndex][0], rpt[tipIndex][1]))

            #Mouse Events
                doMouse.mouseActivities(pygame,rpt, tipIndex,tipThumb,kIndex,kThumb,m,k)
            #Gestures
                # print doDepth.checkAllAboveBox()
                if doDepth.checkAllAboveBox():
                    doGestures.gestures(averageX,averageY,k,m)

                if vals.mouse_flg==1:
                    #This is to weight the location of the pointer WRT tip & knuckle
                    tipParam = 7
                    knuParam = 3
                    if vals.knuckleFlag:
                        fingerX = (rpt[tipIndex][0] * tipParam + rpt[kIndex][0] * knuParam) / (tipParam + knuParam)
                        fingerY = (rpt[tipIndex][1] * tipParam + rpt[kIndex][1] * knuParam) / (tipParam + knuParam)
                    else:
                        fingerX, fingerY = rpt[tipIndex][0], rpt[tipIndex][1]

                    # Relative:
                    if vals.relativeFlag:
                        smoothTipIndex = np.mean(fun.smooth(vals.depthBuff[2].data, window_len = vals.depthBuff[2].size()))
 
                        keyboardTest = isOnKeyboard(fingerX, fingerY, smoothTipIndex)

                        if vals.onKeyboardFlag and not keyboardTest:
                            # Hands up
                            vals.fingerBuff[0].erase()
                            vals.fingerBuff[1].erase()
                        # else:
                        #     # Hands down
                        #     pass

                        vals.onKeyboardFlag = keyboardTest

                        if vals.onKeyboardFlag:
                            vals.fingerBuff[0].put(fingerX)
                            vals.fingerBuff[1].put(fingerY)

                            # Move the mouse
                            if vals.fingerBuff[0].size() >= 2:
                                mouseX, mouseY = finger2MouseRelative(vals.fingerBuff[0].data, \
                                    vals.fingerBuff[1].data, vals.traceX, vals.traceY)

                                vals.buff[0].put(mouseX)
                                vals.buff[1].put(mouseY)
                             
                                smoothX = np.mean(fun.smooth(vals.buff[0].data, window_len = vals.buff[0].size()))
                                smoothY = np.mean(fun.smooth(vals.buff[1].data, window_len = vals.buff[1].size()))

                                # print fingerX, fingerY, mouseX, mouseY
                                vals.traceX, vals.traceY = smoothX, smoothY

                            m.move(vals.traceX, vals.traceY)                     

                    # Absolute:
                    elif not vals.relativeFlag:
                        if not vals.zoom_flg:
                            vals.fX=rpt[tipIndex][0]
                            vals.fY=rpt[tipIndex][1]

                        if ((vals.inputX2-vals.inputX1)==0) or ((vals.inputY2-vals.inputY1)==0):
                            # Use default option
                            mouseX, mouseY = finger2Mouse(fingerX, fingerY, False)
                            # mouseX=(rpt[tipIndex][0]-600)*vals.width/vals.windowX                    
                            # mouseY=(rpt[tipIndex][1]-150)*vals.height/vals.windowY
                        else:
                            # Use the user prefered window size
                            mouseX, mouseY = finger2Mouse(fingerX, fingerY, True)
            

                        if not vals.zoom_flg:
                            vals.fingerX=fingerX
                            vals.fingerY=fingerY
                            vals.mouseX=mouseX
                            vals.mouseY=mouseY




                        """Currently we have the setting such that if there is a single LED that is out of range then
                        the mouse wont move. The problem with this is that the range of the mouse gets limited, and 
                        some places (such as corners) are difficult/impossible to click. If we eliminate the if statement
                        then this problem won't exist, but then it may start to recognize the knuckle LED as the tip and vice 
                        versa. So this is a give or take until we have a better filtering method."""
            
                        if (vals.inrange and doDepth.checkIndexInBox()) or vals.mouseState == vals.MOUSE_DRAG:
                            vals.buff[0].put(mouseX)
                            vals.buff[1].put(mouseY)
                         
                            smoothX = np.mean(fun.smooth(vals.buff[0].data, window_len = vals.buff[0].size()))
                            smoothY = np.mean(fun.smooth(vals.buff[1].data, window_len = vals.buff[1].size()))

                            if vals.featureFlag:
                                vals.constBuff[0].put(mouseX)
                                vals.constBuff[1].put(mouseY)

                                sX = np.mean(fun.smooth(vals.constBuff[0].data, window_len = vals.constBuff[0].size()))
                                sY = np.mean(fun.smooth(vals.constBuff[1].data, window_len = vals.constBuff[1].size()))


                                # The speed of the cursor
                                speed = np.sqrt( (sX - vals.traceX)**2 + (sY - vals.traceY)**2 )
                                if speed < 0.0001:
                                    speed = 0.0001
                                vals.speedBuff.put(speed)
                                vals.smoothSpeed = np.mean(fun.smooth(vals.speedBuff.data, window_len = vals.speedBuff.size()))

                                # Several method to get buffer size from speed:
                                
                                # paramA, paramB = 8.5, 20

                                # 1) size = A + B / speed
                                # newSize = max(int(paramA + paramB / vals.smoothSpeed), vals.minBuffSize)

                                # 2) size = A + B / sqrt(speed)
                                # newSize = max(int(paramA + paramB / np.sqrt(vals.smoothSpeed)), vals.minBuffSize)
                                
                                # newSize = min(newSize, vals.maxBuffSize)

                                # P1(minSpeed, maxBuff), P2(maxSpeed, minBuff)
                                maxSpeed = 25
                                minSpeed = 0.1
                                maxBuff = 35
                                minBuff = 10

                                # 3) size = A + B * speed
                                paramB = float(minBuff - maxBuff) / (maxSpeed - minSpeed)
                                paramA = maxBuff - paramB * minSpeed

                                newSize = paramA + paramB * vals.smoothSpeed
                                newSize = max(min(int(newSize), maxBuff), minBuff)
                                
                                vals.buff[0].setBuffSize(newSize)
                                vals.buff[1].setBuffSize(newSize)

                            if not vals.testTypeFlag or (vals.testTypeFlag and vals.testPointFlag):
                                # Record the last trace point
                                vals.traceX, vals.traceY = smoothX, smoothY
                                # if vals.featureFlag:# and vals.mouseState == vals.MOUSE_READY:
                                #     # param = 20.0 / speed2
                                #     # vals.traceX = int((vals.traceX * param + smoothX) / (1 + param))
                                #     # vals.traceY = int((vals.traceY * param + smoothY) / (1 + param))
                                #     vals.traceX = np.mean(fun.smooth(vals.buff[0].data[-vals.smoothSize:], window_len = vals.smoothSize))
                                #     vals.traceY = np.mean(fun.smooth(vals.buff[1].data[-vals.smoothSize:], window_len = vals.smoothSize))
                                #     # vals.traceX = (vals.traceX * 4 + smoothX) / 5
                                #     # vals.traceY = (vals.traceY * 4 + smoothY) / 5

                                m.move(vals.traceX, vals.traceY)
                                # m.move(vals.buff[0].data[-1],vals.buff[1].data[-1])
                                # m.move(smoothX, smoothY)
                                # m.move(mouseX, mouseY)
            
            if vals.wiimoteNum == vals.wiimoteMaxNum \
            and not (vals.calibLoadFlag or vals.calibration or vals.rec_flg):
                doDraw.drawDefault(screen, defaultFont)

            eventsObject=pygame.event.get()
            doEvents.eventHandling(eventsObject)
            
            msElapsed=clock.tick(pygameRate)
            pygame.display.update() 
            
            
             
            if kill==True or vals.quit_FLG:
                pygame.quit()
                sys.exit()
                break
            
            for event in eventsObject: 
                if (event.type == QUIT) or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    kill=True
                    pygame.quit()
                    sys.exit()
                    break
            
        
        
        
        #working run function
'''        
    def run(self):
        pygame.init()
        clock=pygame.time.Clock()
        infoObject = pygame.display.Info()
        width=infoObject.current_w
        height=infoObject.current_h
        screen=pygame.display.set_mode((width/2,height/2))
        global kill
        
        while kill==False:
            global coords
            
#             print coords[0]
#             print coords[1]
            screen.fill((0,0,0))
            pygame.draw.circle(screen, (255,0,0), (int(coords[0][0][0]),int(coords[0][0][1])),10)
            pygame.draw.circle(screen, (255,0,0), (int(coords[0][1][0]),int(coords[0][1][1])),10)
            pygame.draw.circle(screen, (255,0,0), (int(coords[0][2][0]),int(coords[0][2][1])),10)
            pygame.draw.circle(screen, (255,0,0), (int(coords[0][3][0]),int(coords[0][3][1])),10)
            
            pygame.draw.circle(screen, (0,0,255), (int(coords[1][0][0]),int(coords[1][0][1])),10)
            pygame.draw.circle(screen, (0,0,255), (int(coords[1][1][0]),int(coords[1][1][1])),10)
            pygame.draw.circle(screen, (0,0,255), (int(coords[1][2][0]),int(coords[1][2][1])),10)
            pygame.draw.circle(screen, (0,0,255), (int(coords[1][3][0]),int(coords[1][3][1])),10)
            
            pygame.display.update()
            msElapsed=clock.tick(100)
            if kill==True:
                pygame.quit()
                sys.exit()
                break
            
            for event in pygame.event.get(): 
                if (event.type == QUIT) or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                    break
'''            
            







def messageDecypher(messageData):
    mess=messageData.split(',')
    for i in range(len(mess)):
        if mess[i]=='':
            mess.pop(i)

    data=[[0,0] for i in range(4)]

    for i in mess:

        if i.find('wii')>=0:
            wiiID=i


        if i.find('|')>=0:
            ind=int(i[int(i.find('|')-1)])
            indx=i.find('x')
            indy=i.find('y')
            data[ind][0]=float(i[indx+1:indy])
            data[ind][1]=float(i[indy+1:])
    
    return wiiID,data
    
        
        

class Server:
    
    def __init__(self):
        print('Starting server')
        self.host = ''
        self.port = 50000
        self.backlog = 5
        self.size = 1024
        self.server = None
        self.threads = []
        self.data=[[],[],[]]

    def open_socket(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.host,self.port))
            self.server.listen(5)
        except socket.error, (value,message):
            if self.server:
                self.server.close()
            print "Could not open socket: " + message
            sys.exit(1)

    def run(self):
        self.open_socket()
        input = [self.server,sys.stdin]
        running = 1
        while running:
            inputready,outputready,exceptready = select.select(input,[],[])

            for s in inputready:

                if s == self.server:
                    # handle the server socket
                    c = Client(self.server.accept())
                    c.start()
                    self.threads.append(c)
                    

                elif s == sys.stdin:
                    # handle standard input
                    junk = sys.stdin.readline()
                    running = 0

        # close all threads

        self.server.close()
        for c in self.threads:
            c.join()

class Client(threading.Thread):
    def __init__(self,(client,address)):
        print('Started client comm')
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.size = 1024
        self.data=[]
        vals.wiimoteNum = vals.wiimoteNum + 1

    def run(self):
        running = 1
        while running:
            data = self.client.recv(self.size)                
            if data:
                try:
                    self.wiiID,self.data=messageDecypher(data)
                except:
                    print "User quit."
                    return
                global coords
                
                if self.wiiID.find('1')>=0:
                    coords[0]=self.data
                else:
                    coords[1]=self.data
                
            else:
                self.client.close()
                global kill
                kill=True
                running = 0
                
            

if __name__ == "__main__":
    kill=False
    global coords
    coords=[[],[]]
    coords[0]=[[0,0] for i in range(4)]
    coords[1]=[[0,0] for i in range(4)]
    
    
    a=mainThread()
    a.start()
    s = Server()
    s.run()
    a.join()


