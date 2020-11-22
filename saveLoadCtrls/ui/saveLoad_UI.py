import os
from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omUi
from saveLoadCtrls.core.saveLoadCtrls import SaveLoadCtrls

def maya_main_window():
    """
    Get Maya main window
    :return: int (maya main ptr)
    """
    maya_main_ptr = omUi.MQtUtil.mainWindow()
    return wrapInstance(int(maya_main_ptr), QtWidgets.QWidget)

class mainDialog(QtWidgets.QDialog):


    FILE_FILTERS = "json (*.json);;All Files (*.*)"
    selected_filter = "json (*json *.json)"

    def __init__(self, parent=maya_main_window()):
        super(mainDialog, self).__init__(parent)
        self.FILENAME = 'ctrlWorldMtx_v001.json'
        self.USERHOMEPATH = r'C:\tools\mayaTools\saveLoadCtrls\json'
        self.slc = SaveLoadCtrls()
        self.setWindowTitle('')
        self.setMinimumSize(470, 115)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.create_widgets()
        self.create_layout()
        self.create_connections()


    def create_widgets(self):
        self.lineEdit = QtWidgets.QLineEdit('{}\\{}'.format(self.USERHOMEPATH, self.FILENAME))
        self.loadBuffers_checkBox = QtWidgets.QCheckBox('Load Buffers')
        self.loadBuffers_checkBox.setChecked(True)
        self.loadScale_checkBox = QtWidgets.QCheckBox('Load Scale')
        self.loadScale_checkBox.setChecked(True)
        self.path_btn = QtWidgets.QPushButton('...')
        self.save_btn = QtWidgets.QPushButton('Save')
        self.load_btn = QtWidgets.QPushButton('Load')

    def create_layout(self):

        self.uiTopHBox = QtWidgets.QHBoxLayout()
        self.uiTopHBox.addWidget(self.lineEdit)
        self.uiTopHBox.addWidget(self.path_btn)
        self.uiFormLayout = QtWidgets.QFormLayout()
        self.uiFormLayout.addRow('Path: ', self.uiTopHBox)
        self.uiFormLayout.addRow('', self.loadBuffers_checkBox)
        self.uiFormLayout.addRow('', self.loadScale_checkBox)

        # create button layout
        self.btn_hBoxLayout = QtWidgets.QHBoxLayout()
        self.btn_hBoxLayout.addStretch()
        self.btn_hBoxLayout.addWidget(self.save_btn)
        self.btn_hBoxLayout.addWidget(self.load_btn)

        # create and add to main layout
        self.main_vBoxLayout = QtWidgets.QVBoxLayout(self)
        self.main_vBoxLayout.addLayout(self.uiFormLayout)
        self.main_vBoxLayout.addLayout(self.btn_hBoxLayout)

    def create_connections(self):
        self.path_btn.clicked.connect(self.setfilePath)
        self.save_btn.clicked.connect(self.saveCtrls)
        self.load_btn.clicked.connect(self.loadCtrls)

    def saveCtrls(self):
        self.slc.saveCtrlMtx(self.USERHOMEPATH, self.FILENAME)

    def loadCtrls(self):
        matchScl = False
        loadBuffers = False
        if self.loadScale_checkBox.isChecked():
            matchScl = True

        if self.loadBuffers_checkBox.isChecked():
            loadBuffers = True

        self.slc.loadCtrlMtx(matchScl=matchScl, loadBuffers=loadBuffers)

    def setfilePath(self):
        file_path, self.selected_filter = QtWidgets.QFileDialog.getOpenFileName(self, "Select File",
                                                                                "",
                                                                                self.FILE_FILTERS,
                                                                                self.selected_filter)
        if file_path:
            self.lineEdit.setText(file_path)
if __name__ == '__main__':

    global open_import_dialog
    try:
        open_import_dialog.close()
        open_import_dialog.deleteLater()
    except:
        pass
    open_import_dialog = mainDialog()
    open_import_dialog.show()
