
import constants as vals
import pygame
from pygame import mouse
from pygame.locals import *
import pickle

import sys
from calibFileManager import *

def eventHandling(eventsObject):
    for event in eventsObject:
        if event.type==KEYDOWN:
            if event.key==pygame.K_r: #start recording
                vals.rec_flg=1
                vals.calibration=False
            elif event.key==pygame.K_c: #start vals.calibration
                vals.calibration=1
            elif event.key==pygame.K_s: #pauses the recording
                vals.rec_flg=False
                break
            elif event.key==pygame.K_q: #quits entirely
                print "q pressed"
                vals.quit_FLG=1
            #Load calibration data from file : 'l', load
            elif event.key == pygame.K_l:
                vals.calibLoadFlag = True
            if vals.rec_flg: #if recording, can change the lag time
                if event.key==pygame.K_z:
                    vals.lagValue+=100
                elif event.key==pygame.K_x:
                    vals.lagValue-=100
            #Forced mouse mode
            if event.key==pygame.K_m:
                if vals.mouse_flg==1:
                    vals.mouse_flg=0
                else:
                    vals.mouse_flg=1
                    
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
                        vals.calibState = vals.CLICK_CALIB

                    elif vals.calibState == vals.CLICK_CALIB:
                            while min(vals.clickingCalibList) < 30:
                                vals.clickingCalibList.remove(min(vals.clickingCalibList))
                            vals.clickValue=int(1.2 * min(vals.clickingCalibList))

                            while min(vals.boxBoundCalibList)<15:
                                vals.boxBoundCalibList.remove(min(vals.boxBoundCalibList))
                            sumBoxLimit=0
                            for i in xrange(len(vals.boxBoundCalibList)):
                                sumBoxLimit+=vals.boxBoundCalibList[i]
                            sumBoxLimit=sumBoxLimit/len(vals.boxBoundCalibList)
                            vals.boxLimit=int(sumBoxLimit)-4


                            #store them to file.
                            calibWriter = CalibFileManager(vals.calibFile)
                            calibWriter.write(vals.mouseModeValue, vals.clickValue, vals.boxLimit)
                            vals.calibState = vals.END_CALIB

            # Read calibration data from file, vals.calibLoadFlag mode
            if vals.calibLoadFlag:
                if not vals.calibReadFinished:
                    calibReader = CalibFileManager(vals.calibFile)
                    try:
                        vals.mouseModeValue = int(calibReader.read('mouseModeValue'))
                        vals.clickValue = int(calibReader.read('clickValue'))
                        vals.boxLimit = int(calibReader.read('boxLimit'))
                    except:
                        # Go back and press again
                        print 'Error: Calibration data file not found.'
                        vals.calibLoadFlag = False
                        return

                    vals.calibState = vals.END_CALIB
                    vals.calibReadFinished = True

        if event.type==QUIT:
            vals.quit_FLG=1
