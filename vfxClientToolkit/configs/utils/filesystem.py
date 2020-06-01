from qtpy import QtWidgets
from os.path import expanduser


def browseForFileRoot(uiInstance):
    fileRoot = QtWidgets.QFileDialog.getExistingDirectory(
        uiInstance,
        "Select project root directory",
        expanduser("~"),
        QtWidgets.QFileDialog.ShowDirsOnly,
    )
    uiInstance.setSetting(fileRoot)


def browseForPosix(uiInstance):
    fileRoot = QtWidgets.QFileDialog.getExistingDirectory(
        uiInstance,
        "Select POSIX path root",
        expanduser("~"),
        QtWidgets.QFileDialog.ShowDirsOnly,
    )
    uiInstance.setSetting(fileRoot)
