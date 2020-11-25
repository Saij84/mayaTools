"""
Author:Fangmin Chen
Version: 1.0

Save: selected ctrl/s worldmatrix to a json file
load: json file value and multiply with ctrls inverseParentMatrix
USAGE save: Select Ctrl/s run save method to save
USAGE load: run load method to try load select ctrl/s

toDo list: Enable load everything in json file
toDo list: Currently ctrls needs to be uniquely named
toDo list: loading a negative XYZ value on selected object, will not work correctly. another item for my
"""

import os
import re
import maya.cmds as cmds
import maya.api.OpenMaya as om2
from mayaTools.saveLoadCtrls.constants import constants as CONST
from mayaTools.saveLoadCtrls.utils import utils as utils

FINDDIGITS = re.compile(CONST.FINDDIGITS)
dagPath = om2.MDagPath()
jsonDataDict = dict()
treeList = list()

def jsonNode(ctrlName, parentNode, matrix):
    """
    create json node
    :param ctrlName: str, fullDagPath with namespace replaced with wildcard sign
    :param matrix
    :return: json
    """
    nodeDict = {
        ctrlName:
            {
                'parent': parentNode,
                'matrix': matrix
            }
    }
    return nodeDict


def setFloatWithConditions(srtMTransMtx, mPlugList):
    """
    Setting values on unlocked attributes
    :param srtMTransMtx: MTransformationMatrix (translation, rotation or scale)
    :param mPlugList: MPlug
    :return: None
    """
    for idx, srtPlug in enumerate(mPlugList):
        if not srtPlug.isLocked and not srtPlug.isFreeToChange():
            srtPlug.setFloat(srtMTransMtx[idx])
        else:
            continue


def setAtters(mObjectHandle, mtx, matchScl=True):
    """
    Sets translation/rotation
    :param mObjectHandle: MObjectHandle
    :param mtx: MMatrix
    :param matchScl: bool, default False, match scale
    :return: None
    """
    if mObjectHandle.isValid():
        mObj = mObjectHandle.object()
        mFn = om2.MFnDependencyNode(mObj)
        mTransMtx = om2.MTransformationMatrix(mtx)

        trans = mTransMtx.translation(om2.MSpace.kWorld)
        rot = mTransMtx.rotation()

        transX = mFn.findPlug('translateX', False)
        transY = mFn.findPlug('translateY', False)
        transZ = mFn.findPlug('translateZ', False)
        setFloatWithConditions(trans, [transX, transY, transZ])

        rotX = mFn.findPlug('rotateX', False)
        rotY = mFn.findPlug('rotateY', False)
        rotZ = mFn.findPlug('rotateZ', False)
        setFloatWithConditions(rot, [rotX, rotY, rotZ])

        if matchScl:
            scl = mTransMtx.scale(om2.MSpace.kObject)
            sclX = mFn.findPlug('scaleX', False)
            sclY = mFn.findPlug('scaleY', False)
            sclZ = mFn.findPlug('scaleZ', False)
            setFloatWithConditions(scl, [sclX, sclY, sclZ])


def getNextCtrlNode(mObjHandle):
    """
    Recursively find parent node and stops at the given blacklist
    :param mObjHandle: MObjectHandle
    :return: None
    """
    blackList = ['world', 'rig']
    if mObjHandle.isValid():
        mObj = mObjHandle.object()
        mFnDag = om2.MFnDagNode(mObj)
        nextCtrlNode = mFnDag.parent(0)
        parentMFnDag = om2.MFnDagNode(nextCtrlNode)

        mFnDepend = om2.MFnDependencyNode(nextCtrlNode)
        nextCtrlNodeMObjHandle = om2.MObjectHandle(nextCtrlNode)

        name = utils.stripNameSpace(mFnDag.name())
        parentName = utils.stripNameSpace(mFnDepend.name())
        mtx = utils.getMatrix(mObjHandle)
        if parentMFnDag.child(0).apiType() == om2.MFn.kNurbsCurve or parentMFnDag.childCount() > 1 \
                or parentName in blackList:
            jsonDataDict.update(jsonNode(name, '', mtx))
            return
        else:
            jsonDataDict.update(jsonNode(name, parentName, mtx))
            getNextCtrlNode(nextCtrlNodeMObjHandle)


def getTreeList(jsonData, objName):
    """
    Recursively add the parent srtBuffers to a parentList
    :param jsonData: json
    :param objName: str
    :return: None
    """
    if jsonData[objName].get('parent') == '':
        return
    else:
        parent = jsonData[objName].get('parent')
        treeList.append(parent)
        getTreeList(jsonData, parent)


def saveCtrlMtx(userHomePath, filename):
    """
    Save all selected ctrl and parents world matrix
    """
    print(userHomePath, filename)
    selList = om2.MGlobal.getActiveSelectionList()
    mObjs = [selList.getDependNode(idx) for idx in range(selList.length())]

    for mObj in mObjs:
        if mObj.apiType() == om2.MFn.kTransform:
            mObjHandle = om2.MObjectHandle(mObj)
            getNextCtrlNode(mObjHandle)

    if os.path.isdir(userHomePath):
        utils.toFile(jsonDataDict, userHomePath, filename)
    else:
        os.makedirs(userHomePath)
        utils.toFile(jsonDataDict, userHomePath, filename)
    print('Save Done!')


def loadCtrlMtx( matchScl=False, loadBuffers=False):
    """
    load ctrl mtx
    if: there is a selection the script will try to load the value on the selected ctrl
    else: try to load everything from file
    """

    treeList = list()
    jsonData = utils.fromFile(CONST.USERHOMEPATH, CONST.FILENAME)
    selList = om2.MGlobal.getActiveSelectionList()
    mObjs = [selList.getDependNode(idx) for idx in range(selList.length())]
    for mobj in mObjs:
        mFn = om2.MFnDependencyNode(mobj)
        name = mFn.name()
        objName = utils.stripNameSpace(name)

        treeList.append(objName)
        getTreeList(jsonData, objName)

        if objName in jsonData:
            objectList = [objName]
            if loadBuffers:
                objectList = reversed(treeList)

            for obj in objectList:
                myObjName = obj
                if not cmds.objExists(myObjName):
                    myObjName = '*:{}'.format(obj)

                objSelList = om2.MGlobal.getSelectionListByName(myObjName)
                mObj = objSelList.getDependNode(0)
                fromFileMtx = om2.MMatrix(jsonData[obj].get('matrix'))
                drivenMObjHandle = om2.MObjectHandle(mObj)
                parentInverseMtx = utils.getMatrix(drivenMObjHandle, 'parentInverseMatrix')
                parentInverseMMtx = om2.MMatrix(parentInverseMtx)

                mtx = fromFileMtx * parentInverseMMtx

                setAtters(drivenMObjHandle, mtx, matchScl=matchScl)
        else:
            print('{} is not in the saved json dictionary!'.format(objName))
    print('Load Done!')
