from qtpy.QtWidgets import QComboBox, QItemDelegate, QCheckBox
from qtpy.QtGui import QStandardItem, QStandardItemModel


class ComboCheckBoxDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(ComboCheckBoxDelegate, self).__init__(parent)

    def createEditor(parent, op, idx):
        parent.editor = QCheckBox(parent)


class CheckComboBox(QComboBox):
    def __init__(self):
        QComboBox.__init__(self)

        self.itemModel = QStandardItemModel(0, 1)
        self.setModel(self.itemModel)
        checkBoxDelegate = ComboCheckBoxDelegate()
        self.setItemDelegate(checkBoxDelegate)

    def addData(self, dataIn):
        item = QStandardItem(dataIn)
        item.setCheckable(True)
        item.setSelectable(False)

        self.itemModel.setItem(self.itemModel.rowCount(), 0, item)
