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
            #Depth
                doDepth.findingDepth(rpt, rpt2, tipThumb,tipThumb2, kThumb,kThumb2, tipIndex,tipIndex2,kIndex,kIndex2)
            #GUI
                doDraw.drawAllRecording(screen, rpt, rpt2, tipThumb,tipThumb2, kThumb,kThumb2, tipIndex,tipIndex2,kIndex,kIndex2,averageX,averageY,averageX2,averageY2,myfont,calibFont,depthFont)
                #doDraw.drawAllMiniRecording(miniScreen, rpt, rpt2, tipThumb,tipThumb2, kThumb,kThumb2, tipIndex,tipIndex2,kIndex,kIndex2,averageX,averageY,myfont,calibFont,depthFont)
        
            #Creating the 3d box


            #Mouse Events
                doMouse.mouseActivities(rpt, tipIndex,tipThumb,kIndex,kThumb,m,k)
            #Gestures
                # print doDepth.checkAllAboveBox()
                if doDepth.checkAllAboveBox():
                    doGestures.gestures(averageX,averageY,k,m)

                if vals.mouse_flg==1:
                    mouseX=(rpt[tipIndex][0]-600)*vals.width/400                    
                    mouseY=(rpt[tipIndex][1]-150)*vals.height/290
        
                    """Currently we have the setting such that if there is a single LED that is out of range then
                    the mouse wont move. The problem with this is that the range of the mouse gets limited, and 
                    some places (such as corners) are difficult/impossible to click. If we eliminate the if statement
                    then this problem won't exist, but then it may start to recognize the knuckle LED as the tip and vice 
                    versa. So this is a give or take until we have a better filtering method."""
        
                    if (vals.inrange and doDepth.checkIndexInBox()) or vals.mouseState == vals.MOUSE_DRAG:
                        vals.buff[0].put(mouseX)
                        vals.buff[1].put(mouseY)
                        # data0 = vals.buff[0].getData()
                        # data1 = vals.buff[1].getData() 
                        # smoothX = np.mean(fun.smooth(data0, window_len = len(data0)))
                        # smoothY = np.mean(fun.smooth(data1, window_len = len(data1)))
                        # print data0, data1
                        # print smoothX, smoothY
                        smoothX=np.mean(fun.smooth(vals.buff[0].data, window_len=len(vals.buff[0].data)))
                        smoothY=np.mean(fun.smooth(vals.buff[1].data, window_len=len(vals.buff[1].data)))


                        if not vals.testTypeFlag or (vals.testTypeFlag and vals.testPointFlag):
                            # m.move(vals.buff[0].data[-1],vals.buff[1].data[-1])
                            m.move(smoothX, smoothY)
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


