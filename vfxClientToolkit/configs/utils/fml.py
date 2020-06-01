import platform
from os.path import expanduser

from qtpy import QtWidgets


def browseForRV(uiInstance):

    # TODO support Linux
    systemType = platform.system()

    if systemType == "Windows":
        rvBinary = QtWidgets.QFileDialog.getOpenFileName(
            uiInstance, "Open File", expanduser("~"), "Images (*.exe)"
        )
    else:
        rvBinary = QtWidgets.QFileDialog.getExistingDirectory(
            uiInstance, "Select RV", expanduser("~"), QtWidgets.QFileDialog.ShowDirsOnly
        )

    uiInstance.setSetting(rvBinary)
