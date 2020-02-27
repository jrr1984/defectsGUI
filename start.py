from PyQt5.QtWidgets import QApplication

from webcam import Camera
from mainGUI import StartWindow

camera = Camera(0)
camera.initialize()

app = QApplication([])
start_window = StartWindow(camera)
start_window.show()
app.exit(app.exec_())