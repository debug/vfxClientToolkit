from qtpy import QtWidgets
from os.path import expanduser


def browseForIncoming(uiInstance):
    incomingDir = QtWidgets.QFileDialog.getExistingDirectory(
        uiInstance,
        "Select incoming directory",
        expanduser("~"),
        QtWidgets.QFileDialog.ShowDirsOnly,
    )

    uiInstance.setSetting(incomingDir)
