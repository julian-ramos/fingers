import tkFileDialog
import os.path
from Tkinter import *

def timerFired(canvas):
	redrawAll(canvas)
	delay = 250 # milliseconds
	def f():
		timerFired(canvas) # DK: define local fn in closure
	canvas.after(delay, f) # pause, then call timerFired again

def redrawAll(canvas):   # DK: redrawAll() --> redrawAll(canvas)
	canvas.delete(ALL)
	for i in xrange(len(canvas.data.allData)):
		[x,y,z,ret] = canvas.data.allData[i]
		visualizeValue(canvas,x,y,z,ret)
	displayStatistics(canvas)

#reads the calibration file
def openFile(canvas):
	canvas.data.file_path = tkFileDialog.askopenfilename()
	with open(canvas.data.file_path) as f:
		while True:
			line = str(f.readline()).rstrip()
			if line == "":
				break
			canvas.data.total+=1
			canvas.data.allData.append(getIndividualValues(canvas,line))
			[x,y,z,ret] = getIndividualValues(canvas,line)
			#visualizeValue(canvas,x,y,z,ret)
			if ret:
				canvas.data.hitValue += 1
		print "done"
		displayStatistics(canvas)

def visualizeValue(canvas, x,y,z,ret):
	circleSize = 2
	color = "red"
	if ret:
		color = "green"
	canvas.create_oval(x-circleSize,y-circleSize,x+circleSize,y+circleSize, fill = color)

def displayStatistics(canvas):
	canvas.create_text(100,100, text = canvas.data.file_path)
	canvas.create_text(100,200, text = "total:"+str(canvas.data.total))
	canvas.create_text(100,300, text = "hit:"+str(canvas.data.hitValue))
	canvas.create_text(100,400, text = str(canvas.data.hitValue*1.0/canvas.data.total))

def getIndividualValues(canvas,line):
	x = ""
	y = ""
	z = ""
	ret = ""
	count = 0 
	for i in xrange(len(line)):
		if line[i] == ",":
			count += 1
			continue
		elif (count == 0):
			x += (line[i])
		elif (count == 1):
			y += (line[i])
		elif (count == 2):
			z += (line[i])
		elif (count == 3):
			#print line[i]
			if (line[i] == "T"):
				ret = True
			else:
				ret = False
			break
	return [canvas.data.constant* int(float(x)),canvas.data.constant*int(float(y)),canvas.data.constant*int(float(z)),ret]


def init(canvas):
#condition
	canvas.data.total = 0
	canvas.data.hitValue = 0
	canvas.data.allData = []
	canvas.data.file_path = ""
	canvas.data.constant = 0.4

	openFile(canvas)

def run():
	# create the root and the canvas
	root = Tk()
	cHeight=800
	cWidth=800
	#root.attributes("-fullscreen", True) #substitute `Tk` for whatever your `Tk()` object is called
	canvas = Canvas(root, width=cWidth, height=cHeight)
	canvas.pack()
	# Set up canvas data and call init
	class Struct: pass
	canvas.data = Struct()
	canvas.data.width=cWidth
	canvas.data.height=cHeight
	init(canvas) 
	timerFired(canvas) 
	root.mainloop()  # This call BLOCKS (so your program waits until you close the window!)
run()

