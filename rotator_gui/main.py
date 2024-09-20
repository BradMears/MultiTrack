#!/usr/bin/env python3
'''Presents a control panel for the Yaesu GS5500 az/el rotator. Allows the user to move the
axes left/right/up/down. Shows the reported state of both axes.'''
import sys

from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtCore import QTimer, QObject, pyqtSignal

from time import strftime, localtime

app = QGuiApplication(sys.argv)

engine = QQmlApplicationEngine()
engine.quit.connect(app.quit)
engine.load('main.qml')


class Backend(QObject):

    updated = pyqtSignal(str, arguments=['az_voltage'])

    def __init__(self):
        super().__init__()

        self.az_voltage = 0.0

        # Define timer.
        self.timer = QTimer()
        self.timer.setInterval(100)  # msecs 100 = 1/10th sec
        self.timer.timeout.connect(self.update_time)
        self.timer.start()

    def update_time(self):
        self.az_voltage += 0.1
        self.updated.emit(str(self.az_voltage))


# Define our backend object, which we pass to QML.
backend = Backend()

engine.rootObjects()[0].setProperty('backend', backend)

# Initial call to trigger first update. Must be after the setProperty to connect signals.
backend.update_time()

sys.exit(app.exec())