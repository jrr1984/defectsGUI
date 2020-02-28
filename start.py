from PyQt5.QtWidgets import QApplication

from models import Camera
from Spectrometer import Spectrometer
from views import StartWindow


camera = Camera(0)
camera.initialize()

spectrometer = Spectrometer()
spectrometer.connect()

app = QApplication([])
start_window = StartWindow(camera,spectrometer)
# start_window = StartWindow(camera)
start_window.show()
app.exit(app.exec_())
spectrometer.disconnect()
camera.close_camera()