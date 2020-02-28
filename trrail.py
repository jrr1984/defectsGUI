import time, sys
from pyqtgraph.Qt import QtGui, QtCore
from PyQt5.Qt import QMutex
import pyqtgraph as pg
from random import randint
from copy import copy


class DataGenerator(QtCore.QObject):
    newData = QtCore.pyqtSignal(object)

    def __init__(self, parent=None, sizey=100, rangey=[0, 100], delay=1000):
        QtCore.QObject.__init__(self)
        self.parent = parent
        self.sizey = sizey
        self.rangey = rangey
        self.delay = delay
        self.mutex = QMutex()
        self.y = [0 for i in range(sizey)]
        self.run = True

    def generateData(self):
        while self.run:
            try:
                self.mutex.lock()
                for i in range(self.sizey):
                    self.y[i] = randint(*self.rangey)
                self.mutex.unlock()
                self.newData.emit(self.y)
                QtCore.QThread.msleep(self.delay)
            except:
                pass


class MainWin(QtGui.QMainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        x_axis_min_range = 0
        x_axis_max_range = 100

        y_axis_min_range = 0
        y_axis_max_range = 100

        win2 = pg.GraphicsWindow(title="Test Plots")
        win2.resize(640, 480)
        pg.setConfigOptions(antialias=True)
        self.setCentralWidget(win2)

        self.p1 = win2.addPlot(title="Plot 1")
        self.p1curve = self.p1.plot(pen=(255, 0, 0))
        self.p1.showGrid(x=True, y=True)
        self.p1.setYRange(y_axis_min_range, y_axis_max_range)
        self.p1.setXRange(x_axis_min_range, x_axis_max_range)

        self.p2 = win2.addPlot(title="Plot 2")
        self.p2curve = self.p2.plot(pen=(0, 255, 0))
        self.p2.showGrid(x=True, y=True)
        self.p2.setYRange(y_axis_min_range, y_axis_max_range)
        self.p2.setXRange(x_axis_min_range, x_axis_max_range)

        self.x1 = range(1, 101)
        self.thread1 = QtCore.QThread()
        self.dgen1 = DataGenerator(self, len(self.x1), [0, 100], 1000)
        self.dgen1.moveToThread(self.thread1)
        self.dgen1.newData.connect(self.update_plot1)
        self.thread1.started.connect(self.dgen1.generateData)
        self.thread1.start()

        self.x2 = range(1, 101)
        self.thread2 = QtCore.QThread()
        self.dgen2 = DataGenerator(self, len(self.x2), [0, 100], 1)
        self.dgen2.moveToThread(self.thread2)
        self.dgen2.newData.connect(self.update_plot2)
        self.thread2.started.connect(self.dgen2.generateData)
        self.thread2.start()

    def update_plot1(self, y):
        if self.dgen1.mutex.tryLock():
            y1 = copy(y)
            self.dgen1.mutex.unlock()
            self.p1curve.setData(self.x1, y1)

    def update_plot2(self, y):
        if self.dgen2.mutex.tryLock():
            y2 = copy(y)
            self.dgen2.mutex.unlock()
            self.p2curve.setData(self.x2, y2)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main = MainWin()
    main.show()
    sys.exit(app.exec_())