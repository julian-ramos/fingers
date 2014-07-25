import miniQueue as q

quit_FLG=0

contDist=0
inrange=0

red = (255,0,0,120)
green = (0,255,0)
blue = (0,0,255)
white = (255,255,255)
black = (0,0,0)
yellow = (255,255,0)
gray= (205,200, 177)

width = 800
height = 600

buff=[[],[]]
maxBuff = 10 		# Max buffer size of the x-y queue
buff[0]=q.miniQueue(maxBuff)#, minBuff)
buff[1]=q.miniQueue(maxBuff)#, minBuff)


rpt=[ [0,0] for i in range(4)]
rpt2=[ [0,0] for i in range(4)]

tipThumb=0
tipIndex=0
kThumb=0
kIndex=0

tipThumb2=0
tipIndex2=0
kThumb2=0
kIndex2=0

tipIndexAngle=0
kIndexAngle=0
tipThumbAngle=0
kThumbAngle=0

#wiimote number
wiimoteNum = 0
wiimoteMaxNum = 2

# Test and collect data
testTypeFlag = False
testPointFlag = False
testTypeFile = 'testTypeFile.csv'
testTypeData = []
testStartTime = 0

textContentFile = 'textFiles/text01.txt'
textContent = ''
textGUI = None
typeContentFile = 'textFiles/user01.txt'
'''
typeContent = ''
typeGUI = None
'''

# Debug Mode
debugFlag = False

#calibration constants
mouseModeValue=10
clickValue=10
knuckleValue=80
calibration=False
mouseModeCalibList=[]
clickingCalibList=[[], []]		#time, value


boxLimit=41 #(the upper bound of box. Note as value decreases, box size increases)
boxBoundCalibList=[]

rightClickValue=180

clickNum = 5

'''
# Not used in current version
lagValue=100
mouseModeCalib=False
startMouseModeCalib=False
clickingCalib=False
startClickModeCalib=False
calibWriteFinished = False
'''

# Define the calibration state machine
calibState = -1
START_CALIB, \
MOUSE_MODE_CALIB, \
CLICK_CALIB, \
END_CALIB = range(4)

#calibration file using JSON
calibFile = 'calib.data'
calibLoadFlag = False
calibReadFinished = False

# Used to get user's  clickValue and clickTime(mouseActTimeThre)
clickCalibSTime = 0

#recording flags
rec_flg =0
mouse_flg=0

'''
# Not used in current version of click&drag
flg=True
click_flg=0
doubleClick_flg=0
drag_flg=0
wait_flg=0
mouseClickBuff = [[], []]
'''

# Mark down the possible point of click or drag
clickX = 0
clickY = 0
dragX = 0
dragY = 0

# Define the mouse state machine
mouseState = 0
MOUSE_NORMAL, \
MOUSE_CLICK_READY, \
MOUSE_CLICK, \
MOUSE_DRAG = range(4)

# Calculating the variance may not work, because we can both click and drag without moving.
'''
# The variance threshold of X and Y to judge the correct action(click / drag)
# Click var is smaller than actionVar, and drag var is bigger
# (varX + varY) / 2 
mouseActVarThre = 30

# Original data used to get actionVar
mouseActBuff = [[], []]
'''
# The time threshold to do the judge(millisecond)
mouseActTimeThre = 150

mouseSwitched_flg=0
mouseModeSwitchTime=0

timeHold=80 #in milliseconds      
mouseModeSwitchTime=0

stime=0

#Check inrange
LED1=[]
LED2=[]
LED3=[]
LED4=[]
rptList=[]

#Depth Constants
maxDepthBuff=10
depthBuff=[[],[],[],[]]
depthBuff[0]=q.miniQueue(maxDepthBuff)
depthBuff[1]=q.miniQueue(maxDepthBuff)
depthBuff[2]=q.miniQueue(maxDepthBuff)
depthBuff[3]=q.miniQueue(maxDepthBuff)

#gesture constants
gestureRightThreshHold=800
gestureLeftThreshHold=550
gestureDownThreshHold=550
gestureUpThreshHold=350

gesture_flg_UD=0
gesture_flg_DU=0
gesture_flg_LR=0
gesture_flg_RL=0

gestureTime=0


#just my constants for enabling actual clicking using thumb
yeah_flg=0
oh_yeah_flg=0

ASDFTTD=0
ASDFTKD=0
ASDFITD=0
ASDFIKD=0



clickDistance=0
tipDistance=0
dist3D=0

