import sys
from qtpy import QtWidgets, QtCore, QtGui
import vfxClientToolkit.api.sg as sg
from vfxClientToolkit.icons import PLUS_ICON, MINUS_ICON


def launchRecipientsByVendorUI(uiInstance):
    settings = uiInstance.getParentSettings()
    groupWidget = GroupDisplayWidget(settings["recipients_by_vendor"], uiInstance)
    groupWidget.show()


class GroupDisplayWidget(QtWidgets.QDialog):
    def __init__(self, data, parent):
        QtWidgets.QDialog.__init__(self, parent=parent)
        self.__data = data
        self.__parent = parent
        self.__setupUi()
        self.__setupSignals()

    def __setupUi(self):
        layout = QtWidgets.QVBoxLayout()
        buttonLayout = QtWidgets.QHBoxLayout()

        treeButtonLayout = QtWidgets.QHBoxLayout()

        self.__closeButton = QtWidgets.QPushButton("Close")
        self.__okayButton = QtWidgets.QPushButton("Okay")

        self.__addButton = QtWidgets.QPushButton("")
        self.__addButton.setIcon(QtGui.QIcon(PLUS_ICON))

        self.__minusButton = QtWidgets.QPushButton("")
        self.__minusButton.setIcon(QtGui.QIcon(MINUS_ICON))

        treeButtonLayout.addWidget(self.__minusButton)
        treeButtonLayout.addWidget(self.__addButton)

        buttonLayout.addWidget(self.__closeButton)
        buttonLayout.addWidget(self.__okayButton)

        self.__vendorTree = QtWidgets.QTreeWidget()

        vendors = sg.getVendors()

        for vendor in vendors:
            item = QtWidgets.QTreeWidgetItem()
            item.setText(0, vendor.name)
            item.setCheckState(0, QtCore.Qt.CheckState.Unchecked)
            self.__vendorTree.addTopLevelItem(item)

            if vendor.name in self.__data:
                for recipientName in self.__data[vendor.name]:
                    recipientItem = QtWidgets.QTreeWidgetItem()
                    recipientItem.setText(0, recipientName)
                    item.addChild(recipientItem)
                    item.setExpanded(True)

        layout.addWidget(self.__vendorTree)
        layout.addLayout(treeButtonLayout)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)

    def __setupSignals(self):
        self.__closeButton.released.connect(self.close)
        self.__okayButton.released.connect(self.__saveIt)
        self.__minusButton.released.connect(self.__removeRecipient)
        self.__addButton.released.connect(self.__addRecipient)

    def __saveIt(self):
        recipientsDict = {}
        for i in range(self.__vendorTree.topLevelItemCount()):
            vendorItem = self.__vendorTree.topLevelItem(i)
            recipientsDict[vendorItem.text(0)] = []
            for childIndex in range(vendorItem.childCount()):
                childItem = vendorItem.child(childIndex)
                recipientsDict[vendorItem.text(0)].append(childItem.text(0))

        self.__parent.setSetting(recipientsDict)
        self.close()

    def __removeRecipient(self):
        currentItem = self.__vendorTree.currentItem()

        if currentItem.parent() != None:
            currentItem.parent().removeChild(currentItem)

    def __addRecipient(self):
        currentItem = self.__vendorTree.currentItem()
        if currentItem != None:

            if currentItem.parent() == None:

                value, status = QtWidgets.QInputDialog.getText(
                    self, "Add Email Recipient", "Add Email Recipient:"
                )
                if status:
                    childItem = QtWidgets.QTreeWidgetItem()
                    childItem.setText(0, value)
                    currentItem.addChild(childItem)
                    currentItem.setExpanded(True)


def run():
    app = QtWidgets.QApplication(sys.argv)
    ui = GroupDisplayWidget()
    ui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run()
