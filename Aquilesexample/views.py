from PyQt5.QtCore import Qt, QThread, QTimer
from PyQt5 import QtGui
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QGridLayout,QHBoxLayout, QApplication, QSlider
from pyqtgraph import ImageView
import pyqtgraph as pg
import pyqtgraph.exporters
import numpy as np


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
        self.button_movie = QPushButton('Start Movie', self.central_widget)
        self.image_view = ImageView()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0,1000)
        self.spectra_view = pg.GraphicsLayoutWidget()

        self.layout = QGridLayout(self.central_widget)

        self.layout.addWidget(self.image_view, 0, 0)
        self.layout.addWidget(self.slider, 1, 0)
        self.layout.addWidget(self.button_frame, 2, 0)
        self.layout.addWidget(self.button_movie, 3, 0)
        self.setCentralWidget(self.central_widget)


        self.layout.addWidget(self.spectra_view,0,1)

        self.spectra_plot = self.spectra_view.addPlot(title = 'Live Spectra Acquisition')
        self.spectra_plot.setXRange(300,900)
        self.spectra_plot.setYRange(0, 1)
        self.spectra_plot.showGrid(x=True,y=True,alpha=1.0)
        x_axis = self.spectra_plot.getAxis('bottom')
        y_axis = self.spectra_plot.getAxis('left')

        x_axis.setLabel(text='Wavelength [nm]')  # set axis labels
        y_axis.setLabel(text='Intensity [u.a.]')

        self.drawplot = self.spectra_plot.plot(pen='y')


        self.numPoints = 3648
        self.x = np.array([], dtype=float)
        self.y = np.array([], dtype=float)

        self.counter = 0

        QtGui.QApplication.processEvents()
        self.exporter = pg.exporters.ImageExporter(self.spectra_view.scene())
        self.image_counter = 1

        # self.update_plot()


        self.button_frame.clicked.connect(self.update_image)
        self.button_movie.clicked.connect(self.start_movie)
        self.slider.valueChanged.connect(self.update_brightness)

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_movie)

    def update_image(self):
        frame = self.camera.get_frame()
        self.image_view.setImage(frame,autoHistogramRange=True)

    def update_movie(self):
        self.image_view.setImage(self.camera.last_frame)

    def update_brightness(self, value):
        value /= 10
        self.camera.set_brightness(value)

    def start_movie(self):
        self.movie_thread = MovieThread(self.camera)
        self.movie_thread.start()
        self.update_timer.start(30)

    # def update_plot(self):



class MovieThread(QThread):
    def __init__(self, camera):
        super().__init__()
        self.camera = camera

    def run(self):
        while True:
            self.camera.acquire_movie(10)

class SpectraThread(QThread):
    def __init__(self, spectrometer):
        super().__init__()
        self.spectrometer = spectrometer

    def run(self):
        while True:
            self.camera.acquire_spectra(10)

if __name__ == '__main__':
    app = QApplication([])
    window = StartWindow()
    window.show()
    app.exit(app.exec_())