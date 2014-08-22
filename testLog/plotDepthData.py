# Analysis the depth data from depthData.csv

from pylab import *
from mpl_toolkits.mplot3d import Axes3D
import numpy as np 

def getPlane(x, y, z):
    matXY = np.array([x, y, np.ones(len(x))], np.float64)
    matXY = matXY.T
    vecZ = z
    ret = np.linalg.lstsq(matXY, vecZ)
    return ret

def run():
    plotTogether = True
    colors = ['y.', 'bx', 'c*', 'ko', 'g+', 'r.', 'mx', 'y*', 'bo', 'c+', 'k.', 'gx', 'r*', 'mo']

    # If Plot together
    if plotTogether:
        fig = figure(0)
        ax = Axes3D(fig)#fig.add_subplot(111, projection = '3d') #Axes3D(figure())
        ax.set_aspect('equal')
        
    indent = '    '
    for fi in range(20, 22):
        print 'Start No.' + str(fi)

        # Load the data and get X, Y and Z
        data = np.genfromtxt('depthData{}.csv'.format(fi), dtype = float, delimiter = ',', names = True)
        # keys = ['tipThumb', 'knuThumb', 'tipIndex', 'knuIndex']

        dataX = data['rawX']
        dataY = data['rawY']
        dataZ = data['tipIndex']
        dataNum = len(dataX)

        # If Plot seperately
        if not plotTogether:
            fig = figure(fi)
            ax = Axes3D(fig)#fig.add_subplot(111, projection = '3d') #Axes3D(figure())
            ax.set_aspect('equal')

        # Show original point
        ax.plot(dataX, dataY, dataZ, colors[fi%len(colors)], label = 'data No.' + str(fi))

        # Get the plane parameter
        # Linear function: z = a * x + b * y + c
        ret = getPlane(dataX, dataY, dataZ)
        param = ret[0]

        print indent + str(dataNum) + ' points'
        print indent + 'Least square result: ' + str(ret)
        print indent + 'z = f(x, y) = {}*x + {}*y + {}'.format(param[0], param[1], param[2])

        # Show the plane
        planeX, planeY = np.meshgrid(range(200, 600, 100), range(200, 600, 100))
        planeZ = param[0] * planeX + param[1] * planeY + param[2]
        ax.plot_surface(planeX, planeY, planeZ, label = 'plane', alpha = 1)

        # Get the training set and testing set
        # The device works at 100Hz, so there are 1000 data points in 10 sec.
        setSize = 1000
        setNum = dataNum / setSize
        if setNum >= 2:
            # Split
            edge = []
            for i in range(setNum):
                edge.append(dataNum/setNum * i)
            edge.append(dataNum)
            print indent + 'Split: ' + str(edge)

            setX, setY, setZ = [], [], []
            for i in range(setNum):
                setX.append(dataX[edge[i]:edge[i+1]])
                setY.append(dataY[edge[i]:edge[i+1]])
                setZ.append(dataZ[edge[i]:edge[i+1]])

            # Train and Test
            boxTopInc = np.linspace(0, 2, 50)
            # Error rate [m,n]: use No.m to train, and boxTopInc increase boxTopInc[n]
            errorRate = np.zeros((setNum, len(boxTopInc)))
            for i in range(setNum):#(0,1):
                # Train
                x, y, z = setX[i], setY[i], setZ[i]
                ret = getPlane(x, y, z)
                a, b, c = ret[0]

                print indent + 'Train No.' + str(i)
                print indent*2 + 'Least square result: ' + str(ret)
                print indent*2 + 'z = f(x, y) = {}*x + {}*y + {}'.format(a, b, c)

                # z = ax + by + c => Ax + By + Cz + D = 0, E = sqrt(A^2 + B^2 + C^2)
                # A = a, B = b, C = -1, D = c, E = sqrt(a**2 + b**2 + 1)
                A, B, C, D, E = a, b, -1, c, np.sqrt(a**2 + b**2 + 1)

                # From distance(planeZ, rawZ), positive means the point is 'under' the plane, negative means the point is 'above' the plane.
                # So the max(positive) is the top of the 3D box of keyboard.
                deviation = np.zeros(len(x))
                for j in range(len(x)):
                    distance = np.abs((A*x[j] + B*y[j] + C*z[j] + D) / E)
                    zj = a*x[j] + b*y[j] + c
                    if zj < z[j]:
                        # this point is above the plane
                        distance = -distance
                    deviation[j] = distance

                # For this problem, we need the max, to get all training points in the box.
                maxDev, minDev = max(deviation), min(deviation)
                print indent*2 + 'MaxDeviation:{}, MinDeviation:{}, Std:{}'.format(maxDev, minDev, np.std(deviation))

                # Test
                # Total testing number and error number
                testNum = 0
                errNum = np.zeros(len(boxTopInc))
                for j in range(setNum):
                    if j == i:
                        continue

                    x, y, z = setX[j], setY[j], setZ[j]
                    testNum += len(x)

                    for k in range(len(x)):
                        # Each point in this test set
                        distance = np.abs((A*x[k] + B*y[k] + C*z[k] + D) / E)
                        zk = a*x[k] + b*y[k] + c
                        if zk < z[k]:
                            # this point is above the plane
                            distance = -distance
                        # loop for different box size
                        for m in range(len(boxTopInc)):
                            if distance > maxDev + boxTopInc[m]:
                                # Error
                                errNum[m] += 1

                # Get errors
                for m in range(len(boxTopInc)):
                    errorRate[i][m] = float(errNum[m]) / testNum

                figure(fi)
                plot(boxTopInc, errorRate[i], colors[i%len(colors)]+'-', label = 'Train No.' + str(i))

                print indent*2 + 'Test number: ' + str(testNum)
                print indent*2 + 'Errors for different box size: ' + str(errNum)
                print indent*2 + 'Error rate: ' + str(errorRate[i])

            figure(fi)
            title('data No.' + str(fi))
            legend()

        # data2 = np.genfromtxt('depthData15.csv', dtype = float, delimiter = ',', names = True)

        # above keyboard surface
        # ax.plot(data2['rawX'], data2['rawY'], data2['tipIndex'], color = 'c', label = 'on keyboard')


        if not plotTogether:
            title('data No.' + str(fi))

    legend()
    show()

run()