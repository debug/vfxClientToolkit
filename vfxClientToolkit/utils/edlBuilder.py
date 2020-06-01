# flake8: noqa

from PySide2 import QtWidgets
import hiero.core
import vfxClientToolkit.api.sg as vfxSG


class EditBuilderUi(QtWidgets.QWidget):

    STEP_PREFERENCES = ["Latest", "cmp", "efx", "lgt", "ani", "lay"]
    TITLE = "Edit Builder"

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.__setup()
        self.__setupUi()
        self.__populateWidgets()
        self.__setupSignals()

    def __setupUi(self):
        mainLayout = QtWidgets.QVBoxLayout()

        self.setWindowTitle(self.TITLE)
        edlBrowseLayout = QtWidgets.QHBoxLayout()
        edlLabel = QtWidgets.QLabel("EDL File:")

        self.__edlCombo = QtWidgets.QComboBox()
        self.__edlLineEdit = QtWidgets.QLineEdit()
        self.__edlBrowseButton = QtWidgets.QPushButton("Browse")

        edlBrowseLayout.addWidget(edlLabel)
        edlBrowseLayout.addWidget(self.__edlLineEdit)
        edlBrowseLayout.addWidget(self.__edlBrowseButton)

        stagePreferenceLayout = QtWidgets.QHBoxLayout()
        stagePreferenceLabel = QtWidgets.QLabel("Stage Preference:")

        self.__stagePreferenceCombo = QtWidgets.QComboBox()
        stagePreferenceLayout.addWidget(stagePreferenceLabel)
        stagePreferenceLayout.addWidget(self.__stagePreferenceCombo)

        buttonLayout = QtWidgets.QHBoxLayout()
        self.__buildItButton = QtWidgets.QPushButton("Build")
        buttonLayout.addWidget(self.__buildItButton)

        mainLayout.addLayout(edlBrowseLayout)
        mainLayout.addLayout(stagePreferenceLayout)
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)

    def __setupSignals(self):
        self.__edlBrowseButton.released.connect(self.__browseForEDL)
        self.__buildItButton.released.connect(self.__buildIt)

    def __browseForEDL(self):
        edlFile = QtWidgets.QFileDialog.getOpenFileName(
            self, "Browse for EDL", None, "*.xml"
        )
        self.__edlLineEdit.setText(edlFile[0])

    def __populateWidgets(self):
        self.__stagePreferenceCombo.addItems(self.STEP_PREFERENCES)

    def __buildIt(self):
        seq = self.__loadEDL(self.__edlLineEdit.text())

        sgHandle = vfxSG.getShotgunHandle()

        for sequence in seq.project().sequences():
            seqItems = sequence.items()
            for seqItem in seqItems:
                for vItem in seqItem.items():
                    shotObj = vfxSG.getShot(vItem.name().split("_")[0], sgHandle)

                    if shotObj != None:
                        if self.__stagePreferenceCombo.currentText() == "Latest":

                            versionObj = shotObj.getVersions()
                        else:
                            versionObj = shotObj.getVersionsByDept(
                                str(self.__stagePreferenceCombo.currentText())
                            )

                        if versionObj != []:
                            if (
                                versionObj[0].task == "ret"
                                or versionObj[0].task == None
                            ):
                                if versionObj[1].pathToMov != None:
                                    vItem.replaceClips(versionObj[1].pathToMov)

                            elif versionObj[0].task == "":
                                if versionObj[1].pathToMov != None:
                                    vItem.replaceClips(versionObj[1].pathToMov)

                            else:
                                if versionObj[0].pathToMov != None:
                                    vItem.replaceClips(versionObj[0].pathToMov)

    def __loadEDL(self, edlFile):
        p = hiero.core.newProject()
        topLevelBin = p.clipsBin()
        topLevelBin.importSequence(edlFile)
        return topLevelBin


def run():
    ui = EditBuilderUi()
    ui.show()


if __name__ == "__main__":
    run()
