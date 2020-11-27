import mayaTools.saveLoadCtrls.ui.saveLoadCtrl_UI as mainUI


if __name__ == '__main__':

    global open_import_dialog
    try:
        open_import_dialog.close()
        open_import_dialog.deleteLater()
    except:
        pass
    open_import_dialog = mainUI.MainDialog()
    open_import_dialog.show()
