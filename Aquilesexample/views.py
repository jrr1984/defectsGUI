from PyQt5.QtCore import Qt, QThread, QTimer
from PyQt5 import QtGui
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QGridLayout,QHBoxLayout, QApplication, QSlider
from pyqtgraph import ImageView
import pyqtgraph as pg
import pyqtgraph.exporters
import numpy as np
import time
import pandas as pd
wavel_df = pd.read_pickle("wavel_df.pkl")
wavel_array = wavel_df.iloc[:, 0].values


class StartWindow(QMainWindow):
    def __init__(self, camera = None,spectrometer=None):
        super().__init__()
        self.camera = camera
        self.spectrometer = spectrometer

        self.title = 'LECacqGUI'
        self.left = 1000
        self.top = 1000
        self.width = 1000
        self.height = 1000
        self.icon = "logo_LEC.ico"

        self.setWindowTitle(self.title)
        self.setWindowIcon(QtGui.QIcon(self.icon))


        self.central_widget = QWidget()
        self.button_frame = QPushButton('Acquire Frame', self.central_widget)
        self.button_movie = QPushButton('Start Live View', self.central_widget)
        # self.button_stop_movie = QPushButton('Stop Live View', self.central_widget)
        self.button_live_spectra = QPushButton('Start Live AcqSpectra', self.central_widget)
        self.image_view = ImageView()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0,1000)
        self.spectra_view = pg.GraphicsLayoutWidget()

        self.layout = QGridLayout(self.central_widget)
        self.showFullScreen()

        self.layout.addWidget(self.image_view, 0, 0)
        self.layout.addWidget(self.slider, 1, 0)
        self.layout.addWidget(self.button_frame, 2, 0)
        self.layout.addWidget(self.button_movie, 3, 0)
        # self.layout.addWidget(self.button_stop_movie, 4, 0)
        self.setCentralWidget(self.central_widget)


        self.layout.addWidget(self.spectra_view,0,1)
        self.layout.addWidget(self.button_live_spectra, 1, 1)

        self.spectra_plot = self.spectra_view.addPlot(title = 'Live Spectra Acquisition')
        self.spectra_plot.setXRange(300,900)
        self.spectra_plot.setYRange(0, 1)
        self.spectra_plot.showGrid(x=True,y=True,alpha=1.0)
        x_axis = self.spectra_plot.getAxis('bottom')
        y_axis = self.spectra_plot.getAxis('left')

        x_axis.setLabel(text='Wavelength [nm]')  # set axis labels
        y_axis.setLabel(text='Intensity [u.a.]')

        self.drawplot = self.spectra_plot.plot(pen='y')


        self.x = wavel_array
        self.y = wavel_array
        self.drawplot.setData(self.x, self.y)

        self.counter = 0
        self.fps = 0.
        self.lastupdate = time.time()

        QtGui.QApplication.processEvents()
        self.exporter = pg.exporters.ImageExporter(self.spectra_view.scene())
        self.image_counter = 1


        self.button_frame.clicked.connect(self.update_image)
        self.button_movie.clicked.connect(self.start_movie)
        # self.button_stop_movie.clicked.connect(self.camera.stop)
        self.button_live_spectra.clicked.connect(self.start_live_spectra)
        self.slider.valueChanged.connect(self.update_brightness)

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_movie)

        self.spectra_update_timer = QTimer()
        self.spectra_update_timer.timeout.connect(self.update_spectra)

        self.label = QtGui.QLabel()
        self.layout.addWidget(self.label, 2, 1)


    def update_image(self):
        self.camera.stop()
        frame = self.camera.get_frame()
        self.image_view.setImage(frame,autoHistogramRange=True)

    def update_movie(self):
        self.image_view.setImage(self.camera.last_frame)

    def update_framerate(self):
        now = time.time()
        dt = (now - self.lastupdate)
        if dt <= 0:
            dt = 0.000000000001
        fps2 = 1.0 / dt
        self.lastupdate = now
        self.fps = self.fps * 0.9 + fps2 * 0.1
        tx = 'Mean Frame Rate:  {fps:.3f} FPS'.format(fps=self.fps)
        self.label.setText(tx)
        QTimer.singleShot(1, self.update_spectra)
        self.counter += 1

    def update_spectra(self):
        intensity = self.spectrometer.measure_spectra(2,'50 ms')
        self.drawplot.setData(intensity)
        self.update_framerate()


    def update_brightness(self, value):
        value /= 10
        self.camera.set_brightness(value)

    def start_movie(self):
        self.camera.stopped = False
        self.movie_thread = MovieThread(self.camera)
        self.movie_thread.start()
        self.update_timer.start(100)



    def start_live_spectra(self):
        self.spectra_thread = SpectraThread(self.spectrometer)
        self.spectra_thread.start()
        self.spectra_update_timer.start(10000)



class MovieThread(QThread):
    def __init__(self, camera):
        super().__init__()
        self.camera = camera

    def run(self):
        while True:
            if self.camera.stopped:
                return
            self.camera.acquire_movie(1)


class SpectraThread(QThread):
    def __init__(self, spectrometer):
        super().__init__()
        self.spectrometer = spectrometer

    def run(self):
        while True:
            self.spectrometer.acquire_spectra(1,2,'50 ms')

if __name__ == '__main__':
    app = QApplication([])
    window = StartWindow()
    window.show()
    app.exit(app.exec_())