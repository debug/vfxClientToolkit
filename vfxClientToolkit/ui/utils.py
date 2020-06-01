from qtpy import QtGui


def centerWidget(parent):
    frame = parent.frameGeometry()
    primaryScreen = QtGui.QGuiApplication.primaryScreen()
    center = primaryScreen.availableGeometry().center()
    frame.moveCenter(center)
    parent.move(frame.topLeft())
