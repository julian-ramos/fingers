# Analysis the depth data from depthData.csv

from pylab import *
from mpl_toolkits.mplot3d import Axes3D
import numpy as np 

def run():
    fig = figure()
    ax = Axes3D(fig)#fig.add_subplot(111, projection = '3d') #Axes3D(figure())
    ax.set_aspect('equal')
    colors = ['y.', 'b.', 'c.', 'k.', 'g.', 'r.', 'm.']
    for fi in range(14,15):
        data = np.genfromtxt('depthData{}.csv'.format(fi), dtype = float, delimiter = ',', names = True)

        keys = ['tipThumb', 'knuThumb', 'tipIndex', 'knuIndex']


        dataX = data['rawX']
        dataY = data['rawY']
        dataZ = data['tipIndex']

        # fig = figure(fi)
        # ax = Axes3D(fig)#fig.add_subplot(111, projection = '3d') #Axes3D(figure())
        # ax.set_aspect('equal')

        # keyboard point
        ax.plot(dataX, dataY, dataZ, colors[fi%len(colors)], label = 'data No.' + str(fi))

        # Get the plane
        # linear: z = a * x + b * y + c
        matXY = np.array([dataX, dataY, np.ones(len(dataX))], np.float64)
        matXY = matXY.T
        vecZ = dataZ
        ret = np.linalg.lstsq(matXY, vecZ)
        print 'data No.' + str(fi) + str(ret[1] / len(dataX))

        planeX, planeY = np.meshgrid(range(200, 600, 100), range(200, 600, 100))
        param = ret[0]
        planeZ = param[0] * planeX + param[1] * planeY + param[2]
        ax.plot_surface(planeX, planeY, planeZ, label = 'plane', alpha = 1)


        data2 = np.genfromtxt('depthData15.csv', dtype = float, delimiter = ',', names = True)

        # above keyboard surface
        # ax.plot(data2['rawX'], data2['rawY'], data2['tipIndex'], color = 'c', label = 'on keyboard')

        # title('data No.' + str(fi))

    legend()
    show()

run()