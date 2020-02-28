from PyQt5.QtWidgets import QApplication

from models import Camera
from Spectrometer import Spectrometer
from views import StartWindow
import time



camera = Camera(0)
camera.initialize()
time.sleep(0.5)

# spectrometer = Spectrometer()
# spectrometer.connect()
# time.sleep(0.5)

app = QApplication([])
# start_window = StartWindow(camera,spectrometer)
start_window = StartWindow(camera)
start_window.show()
app.exit(app.exec_())
# spectrometer.disconnect()