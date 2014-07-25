# -*- coding: utf-8 -*-
"""
Created on Sun Apr 13 19:31:46 2014

@author: julian
"""
import moosegesture as mg
import numpy as np
import matplotlib.pyplot as plt
from math import pi, log
import pylab
from scipy import fft, ifft
from scipy.optimize import curve_fit
from sys import stdout
import textwrap
import pygame
import string
from pygame.locals import *

def arrowsSequence(X,Y,color=None):
    '''
    Draws an arrows sequence from 2d coordinates
    '''
    if color==None:
        color=['b','g','k']
#    print(type(X[0])==list)
    if type(X[0])==list:
        plt.figure()
        plt.hold(True)
        for i in range(len(X)):
            x=np.array(X[i])
            y=np.array(Y[i])            
            plt.plot(x[0],y[0],'ro')
            plt.plot(x,y,color=color[i])
            plt.quiver(x[:-1], y[:-1], x[1:]-x[:-1], y[1:]-y[:-1], scale_units='xy', angles='xy', scale=1)
        plt.axis((0,1020,0,800))
        plt.show()
    else:
        x=np.array(X)
        y=np.array(Y)
        plt.figure()
        plt.hold(True)
        plt.plot(x[0],y[0],'r')
        plt.plot(x,y,'b')
        plt.quiver(x[:-1], y[:-1], x[1:]-x[:-1], y[1:]-y[:-1], scale_units='xy', angles='xy', scale=1)
        plt.axis((0,1020,0,800))
        plt.show()
        
    
import numpy

def smooth(x,window_len=11,window='hanning'):
    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)
    
    see also: 
    
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """
    if type(x)!=np.array:
        x=np.array(x)

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"


    s=numpy.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=numpy.ones(window_len,'d')
    else:
        w=eval('numpy.'+window+'(window_len)')

    y=numpy.convolve(w/w.sum(),s,mode='valid')
    return y

def corrWin(x,y,window_len=20):
    corr=[]    
    rows=np.min([np.shape(x)[0],np.shape(y)[0]])
    
    for i in range(rows-window_len):
        temp=np.corrcoef(x[i:i+window_len],y[i:i+window_len])
        corr.append(temp[0,1])
        
    return corr
        
        
def distanceVec(x0,y0,x1,y1):
#    print(len(x0),len(x1))
    dist=[]
    dataPts=min(len(x0),len(x1))
    for i in range(dataPts):
        temp=np.sqrt((x0[i]-x1[i])**2+(y0[i]-y1[i])**2)
        dist.append(temp)
    return dist
    
def fftWin(x,window_len):
    '''
    Computes the fourier transform over the window specified
    '''
    fftVals=[]
    for i in range(len(x)-window_len):
        temp=np.abs(np.fft.fft(x[i:i+window_len]))/window_len
        temp=temp[range(window_len/2)]
        fftVals.append(temp)
    return fftVals
    
def ptsPreprocess(data):
    '''
    smooths and centers the data points using the 
    default parameters for smooth
    '''
    return smooth(data-np.mean(data))


def dist2pts(dist):
    '''
    Transforms from distances to points
    '''
    pts=[ [i,val] for i,val in enumerate(dist)]
    return pts
    
    
def gestureReco(buff1,buff2,gestures):
    pt1=np.array(buff1.allData())
    pt2=np.array(buff2.allData())
    x0=pt1[:,0]
    y0=pt1[:,1]
    x1=pt2[:,0]
    y1=pt2[:,1]
    x0=ptsPreprocess(x0)
    y0=ptsPreprocess(y0)
    x1=ptsPreprocess(x1)
    y1=ptsPreprocess(y1)
    dist=distanceVec(x0,y0,x1,y1)
    pts=dist2pts(dist)
    currgest=mg.getGesture(pts)
    currgest=[str(i) for i in currgest]
    result=mg.findClosestMatchingGesture(currgest,gestures)
    return str(result).strip('['),currgest
    
#def extrapol(x1,y1,x2,y2,d):

def _datacheck_peakdetect(x_axis, y_axis):
    if x_axis is None:
        x_axis = range(len(y_axis))
    
    if len(y_axis) != len(x_axis):
        raise (ValueError, 
                'Input vectors y_axis and x_axis must have same length')
    
    #needs to be a numpy array
    y_axis = np.array(y_axis)
    x_axis = np.array(x_axis)
    return x_axis, y_axis
    
def peakdetect(y_axis, x_axis = None, lookahead = 300, delta=0):
    """
    Converted from/based on a MATLAB script at: 
    http://billauer.co.il/peakdet.html
    
    function for detecting local maximas and minmias in a signal.
    Discovers peaks by searching for values which are surrounded by lower
    or larger values for maximas and minimas respectively
    
    keyword arguments:
    y_axis -- A list containg the signal over which to find peaks
    x_axis -- (optional) A x-axis whose values correspond to the y_axis list
        and is used in the return to specify the postion of the peaks. If
        omitted an index of the y_axis is used. (default: None)
    lookahead -- (optional) distance to look ahead from a peak candidate to
        determine if it is the actual peak (default: 200) 
        '(sample / period) / f' where '4 >= f >= 1.25' might be a good value
    delta -- (optional) this specifies a minimum difference between a peak and
        the following points, before a peak may be considered a peak. Useful
        to hinder the function from picking up false peaks towards to end of
        the signal. To work well delta should be set to delta >= RMSnoise * 5.
        (default: 0)
            delta function causes a 20% decrease in speed, when omitted
            Correctly used it can double the speed of the function
    
    return -- two lists [max_peaks, min_peaks] containing the positive and
        negative peaks respectively. Each cell of the lists contains a tupple
        of: (position, peak_value) 
        to get the average peak value do: np.mean(max_peaks, 0)[1] on the
        results to unpack one of the lists into x, y coordinates do: 
        x, y = zip(*tab)
    """
    max_peaks = []
    min_peaks = []
    dump = []   #Used to pop the first hit which almost always is false
       
    # check input data
    x_axis, y_axis = _datacheck_peakdetect(x_axis, y_axis)
    # store data length for later use
    length = len(y_axis)
    
    
    #perform some checks
    if lookahead < 1:
        raise ValueError, "Lookahead must be '1' or above in value"
    if not (np.isscalar(delta) and delta >= 0):
        raise ValueError, "delta must be a positive number"
    
    #maxima and minima candidates are temporarily stored in
    #mx and mn respectively
    mn, mx = np.Inf, -np.Inf
    
    #Only detect peak if there is 'lookahead' amount of points after it
    for index, (x, y) in enumerate(zip(x_axis[:-lookahead], 
                                        y_axis[:-lookahead])):
        if y > mx:
            mx = y
            mxpos = x
        if y < mn:
            mn = y
            mnpos = x
        
        ####look for max####
        if y < mx-delta and mx != np.Inf:
            #Maxima peak candidate found
            #look ahead in signal to ensure that this is a peak and not jitter
            if y_axis[index:index+lookahead].max() < mx:
                max_peaks.append([mxpos, mx])
                dump.append(True)
                #set algorithm to only find minima now
                mx = np.Inf
                mn = np.Inf
                if index+lookahead >= length:
                    #end is within lookahead no more peaks can be found
                    break
                continue
            #else:  #slows shit down this does
            #    mx = ahead
            #    mxpos = x_axis[np.where(y_axis[index:index+lookahead]==mx)]
        
        ####look for min####
        if y > mn+delta and mn != -np.Inf:
            #Minima peak candidate found 
            #look ahead in signal to ensure that this is a peak and not jitter
            if y_axis[index:index+lookahead].min() > mn:
                min_peaks.append([mnpos, mn])
                dump.append(False)
                #set algorithm to only find maxima now
                mn = -np.Inf
                mx = -np.Inf
                if index+lookahead >= length:
                    #end is within lookahead no more peaks can be found
                    break
            #else:  #slows shit down this does
            #    mn = ahead
            #    mnpos = x_axis[np.where(y_axis[index:index+lookahead]==mn)]
    
    
    #Remove the false hit on the first value of the y_axis
    try:
        if dump[0]:
            max_peaks.pop(0)
        else:
            min_peaks.pop(0)
        del dump
    except IndexError:
        #no peaks were found, should the function return empty lists?
        pass
        
    return [max_peaks, min_peaks]

    ########## Reader - 1.3 ##########
# Download from http://www.pygame.org/project-Reader-1813-3179.html
# This module can show a text area with auto-split to fit the size.

pygame.font.init()

class Reader(pygame.Rect,object):
    
    class ln(object):
        def __init__(self,string,nl,sp):
            self.string = string
            self.nl = nl
            self.sp = sp

    def __init__(self,text,pos,width,fontsize,height=None,font=None,bg=(250,250,250),fgcolor=(0,0,0),hlcolor=(180,180,200),split=True):
        self._original = text.expandtabs(4).split('\n')
        self.BG = bg
        self.FGCOLOR = fgcolor
        self._line = 0
        self._index = 0
        if not font:
            self._fontname = pygame.font.match_font('mono',1)
            self._font = pygame.font.Font(self._fontname,fontsize)
        elif type(font) == str:
            self._fontname = font
            self._font = pygame.font.Font(font,fontsize)
        self._w,self._h = self._font.size(' ')
        self._fontsize = fontsize
        if not height: pygame.Rect.__init__(self,pos,(width,self._font.get_height()))
        else: pygame.Rect.__init__(self,pos,(width,height))
        self.split = split
        self._splitted = self.splittext()
        self._x,self._y = pos
        self._src = pygame.display.get_surface()
        self._select = self._line,self._index
        self._hlc = hlcolor
        self.HLCOLOR = hlcolor

    def splittext(self):
        nc = self.width / self._w
        out = []
        for e,i in enumerate(self._original):
            a = Reader.ln('',e,0)
            if not i:
                out.append(a)
                continue
            for j in textwrap.wrap(i,nc,drop_whitespace=False) if self.split else [i]:
                out.append(Reader.ln(j,e,a.sp+len(a.string)))
                a = out[-1]
        return out

    @property
    def HLCOLOR(self):
        return self._hlc
    @HLCOLOR.setter
    def HLCOLOR(self,color):
        self._hlsurface = pygame.Surface((self._w,self._h),pygame.SRCALPHA)
        self._hlsurface.fill(color)

    @property
    def POS(self):
        return self._line,self._index

    @property
    def NLINE(self):
        return self._splitted[self._line].nl

    @property
    def LINE(self):
        return self._original[self.NLINE]
        
    @property
    def WORD(self):
        try:
            s = self._splitted[self._line].sp+self.wrd
            p1 = self.LINE[:s].split(' ')[-1]
            p2 = self.LINE[s:].split(' ')[0]
            if p2: return p1+p2
        except: return None
    
    @property
    def SELECTION(self):
        p1,p2 = sorted(((self._line,self._index),self._select))
        if p1 != p2:
            selection = [len(i.string) for i in self._splitted[:p2[0]]]
            return '\n'.join(self._original)[sum(selection[:p1[0]]) + self._splitted[p1[0]].nl + p1[1]:sum(selection) + self._splitted[p2[0]].nl + p2[1]]
        return ''
                
    @property
    def FONTSIZE(self):
        return self._fontsize
    @FONTSIZE.setter
    def FONTSIZE(self,size):
        self._font = pygame.font.Font(self._fontname,size)
        self._fontsize = size
        self._w,self._h = self._font.size(' ')
        self._splitted = self.splittext()
        y = self._y
        h = len(self._splitted) * self._h
        if h > self.height:
            if self._y - self._h < self.bottom - h: self._y = self.bottom - h
        self._y += (self.top - self._y)%self._h
        self.HLCOLOR = self._hlc
    
    def screen(self):
        clip = self._src.get_clip()
        self._src.set_clip(self.clip(clip))
        try: self._src.fill(self.BG,self)
        except: self._src.blit(self.BG,self)
        
        start = (self.top - self._y) / self._h
        end = (self.bottom - self._y) / self._h + 1

        p1,p2 = sorted(((self._line,self._index),self._select))

        y = self._y + start * self._h
        for py,i in enumerate(self._splitted[start:end],start):
            x = self._x
            for px,j in enumerate(i.string):
                if p1<=(py,px)<p2:
                    self._src.blit(self._hlsurface,(x,y))
                    self._src.blit(self._font.render(j,1,self.FGCOLOR),(x,y))
                else:
                    self._src.blit(self._font.render(j,1,self.FGCOLOR),(x,y))
                x += self._w
            y += self._h
        self._src.set_clip(clip)
        
    def show(self):
        self.screen()
        pygame.display.update(self)
            
    def update(self,ev):

        line,index = self._line,self._index
        ctrl = pygame.key.get_pressed()
        ctrl = ctrl[pygame.K_RCTRL]|ctrl[pygame.K_LCTRL]
        
        def scrollup(n):
            y = self._y
            if self._y + self._h * n > self.top: self._y = self.top
            else: self._y += self._h * n
        
        def scrolldown(n):
            y = self._y
            h = len(self._splitted) * self._h
            if h > self.height:
                if self._y - self._h * n < self.bottom - h: self._y = self.bottom - h
                else: self._y -= self._h * n
        
        if ev.type == pygame.KEYDOWN:            
            if ev.key == pygame.K_UP:
                scrollup(1)
                
            elif ev.key == pygame.K_DOWN:
                scrolldown(1)           
            
            elif ctrl and ev.key == pygame.K_KP_PLUS:
                self.FONTSIZE += 1         
            
            elif ctrl and ev.key == pygame.K_KP_MINUS and self._fontsize:
                self.FONTSIZE -= 1

        elif ev.type == pygame.MOUSEBUTTONDOWN and self.collidepoint(ev.pos):
            if ev.button == 1:
                self._line = (ev.pos[1] - self._y) / self._h
                self._index = (ev.pos[0] - self._x) / self._w
                self.wrd = self._index
                if ((ev.pos[0] - self._x) % self._w) > (self._w / 2): self._index += 1
                if self._line > len(self._splitted)-1:
                    self._line = len(self._splitted)-1
                    self._index = len(self._splitted[self._line].string)
                if self._index > len(self._splitted[self._line].string): self._index = len(self._splitted[self._line].string)
                self._select = self._line,self._index
                
        elif ev.type == pygame.MOUSEBUTTONUP and self.collidepoint(ev.pos):
            try:
                if ev.click[4]: scrollup(sum(range(1,ev.click[4]+1))/10+1)
                elif ev.click[5]: scrolldown(sum(range(1,ev.click[5]+1))/10+1)
            except:
                if ev.button == 4:
                    scrollup(3)
                
                elif ev.button == 5:
                    scrolldown(3)
        
        elif ev.type == pygame.MOUSEMOTION and ev.buttons[0] and self.collidepoint(ev.pos):
            self._line = (ev.pos[1] - self._y) / self._h
            self._index = (ev.pos[0] - self._x) / self._w
            if ((ev.pos[0] - self._x) % self._w) > (self._w / 2): self._index += 1
            if self._line > len(self._splitted)-1:
                self._line = len(self._splitted)-1
                self._index = len(self._splitted[self._line].string)
            if self._index > len(self._splitted[self._line].string): self._index = len(self._splitted[self._line].string)
            
##############################
