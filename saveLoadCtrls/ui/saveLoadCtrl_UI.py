from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omUi
from mayaTools.saveLoadCtrls.constants import constants as CONST
from mayaTools.saveLoadCtrls.core import saveLoadCtrls as core


def maya_main_window():
    """
    Get Maya main window
    :return: int (maya main ptr)
    """
    maya_main_ptr = omUi.MQtUtil.mainWindow()
    return wrapInstance(int(maya_main_ptr), QtWidgets.QWidget)


class MainDialog(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(MainDialog, self).__init__(parent)
        self.setWindowTitle('')
        self.setMinimumSize(470, 115)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        """
        pyside2 create widgets and set defaults
        :return: None
        """

        self.lineEdit = QtWidgets.QLineEdit('{}\\{}'.format(CONST.USERHOMEPATH, CONST.DEFAULTFILENAME))

        self.levelSpinBox = QtWidgets.QSpinBox()
        self.levelSpinBox.setValue(3)

        self.levelSpinBoxLable = QtWidgets.QLabel('Set Levels')

        self.loadBuffers_checkBox = QtWidgets.QCheckBox('Load Buffers')
        self.loadBuffers_checkBox.setChecked(True)

        self.loadScale_checkBox = QtWidgets.QCheckBox('Load Scale')
        self.loadScale_checkBox.setChecked(True)

        self.path_btn = QtWidgets.QPushButton('...')
        self.save_btn = QtWidgets.QPushButton('Save')
        self.load_btn = QtWidgets.QPushButton('Load')

    def create_layout(self):
        """
        pyside2 create layout
        :return: None
        """
        self.uiTopHBox = QtWidgets.QHBoxLayout()
        self.uiTopHBox.addWidget(self.lineEdit)
        self.uiTopHBox.addWidget(self.path_btn)

        self.levelSpinBoxHBox = QtWidgets.QHBoxLayout()
        self.levelSpinBoxHBox.addWidget(self.levelSpinBoxLable)
        self.levelSpinBoxHBox.addWidget(self.levelSpinBox)
        self.levelSpinBoxHBox.addStretch()

        self.uiFormLayout = QtWidgets.QFormLayout()
        self.uiFormLayout.addRow('Path: ', self.uiTopHBox)
        self.uiFormLayout.addRow('', self.levelSpinBoxHBox)
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
        """
        pyside2 create connections
        :return: None
        """
        self.path_btn.clicked.connect(self.setfilePath)
        self.save_btn.clicked.connect(self.saveCtrls)
        self.load_btn.clicked.connect(self.loadCtrls)

    def saveCtrls(self):
        core.saveCtrlMtx(self.lineEdit.text(), self.levelSpinBox.value())

    def loadCtrls(self):
        """
        pyside2 connection instructions for load ctrl button
        :return: None
        """
        matchScl = False
        loadBuffers = False
        if self.loadScale_checkBox.isChecked():
            matchScl = True

        if self.loadBuffers_checkBox.isChecked():
            loadBuffers = True

        core.loadCtrlMtx(self.lineEdit.text(), matchScl=matchScl, loadBuffers=loadBuffers)

    def setfilePath(self):
        """
        pyside2 connection instructions for setPath button
        :return: None
        """
        file_path, self.selected_filter = QtWidgets.QFileDialog.getOpenFileName(self, "Select File",
                                                                                CONST.USERHOMEPATH,
                                                                                CONST.FILE_FILTERS,
                                                                                CONST.SELECTED_FILTER)
        if file_path:
            self.lineEdit.setText(file_path)
