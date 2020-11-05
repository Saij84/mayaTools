from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omUi
import mayaTools.saveLoadCtrls.core.saveLoadCtrls as test


def maya_main_window():
    '''
    Get Maya main window
    :return: int (maya main ptr)
    '''
    maya_main_ptr = omUi.MQtUtil.mainWindow()
    return wrapInstance(int(maya_main_ptr), QtWidgets.QWidget)

class mainDialog(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super(mainDialog, self).__init__(parent)

        self.setWindowTitle('')
        self.setMinimumSize(463, 80)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.create_widgets()
        self.create__layout()
        self.create_connections()

    def create_widgets(self):
        self.lineEdit = QtWidgets.QLineEdit()
        self.checkBox = QtWidgets.QCheckBox()
        self.path_btn = QtWidgets.QPushButton('...')
        self.save_btn = QtWidgets.QPushButton('Save')
        self.load_btn = QtWidgets.QPushButton('Load')

    def create__layout(self):
        # form layout
        self.path_formLayout = QtWidgets.QFormLayout()
        self.path_formLayout.addRow('Path: ', self.lineEdit)
        self.path_formLayout.addRow('', self.checkBox)

        self.uiTop = QtWidgets.QHBoxLayout()
        self.uiTop.addLayout(self.path_formLayout)
        self.uiTop.addWidget(self.path_btn)

        # create button layout
        self.btn_hBoxLayout = QtWidgets.QHBoxLayout()
        self.btn_hBoxLayout.addStretch()
        self.btn_hBoxLayout.addWidget(self.save_btn)
        self.btn_hBoxLayout.addWidget(self.load_btn)

        # create and add to main _layout
        self.main_vBoxLayout = QtWidgets.QVBoxLayout(self)
        self.main_vBoxLayout.addLayout(self.uiTop)
        self.main_vBoxLayout.addLayout(self.btn_hBoxLayout)

    def create_connections(self):
        pass


if __name__ == '__main__':

    global open_import_dialog
    try:
        open_import_dialog.close()
        open_import_dialog.deleteLater()
    except:
        pass
    open_import_dialog = mainDialog()
    open_import_dialog.show()
