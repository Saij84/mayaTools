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
import json
import maya.api.OpenMaya as om2

FINDDIGITS = re.compile(r"\d+")
USERHOMEPATH = r"c:\mayaCtrlJsons"
filename = "ctrlWorldMtx_v001.json"
fileList = sorted(os.listdir(USERHOMEPATH))
dagPath = om2.MDagPath()


def toFile(jsonDataDump, filename):
    """
    Write to json file
    :param jsonDataDump: jason data
    :return: None
    """
    with open(os.path.join(USERHOMEPATH, filename), "w") as jDump2File:
        json.dump(jsonDataDump, jDump2File)


def fromFile(filename):
    """
    Read json file
    :param filename: str
    :return: json dictionary
    """
    with open(os.path.join(USERHOMEPATH, filename), "r") as jsonFile:
        jsonData = json.load(jsonFile)
        return jsonData


def stripNameSpace(name):
    """
    Check to see if there is a namespace on the incoming name, if yes, strip and return name with no namespace
    :param name: str
    :return: str, name with no namespace
    """
    name = name
    if ":" in name:
        name = name.split(":")[1]
    return name


def getNextCtrlNode(mObjHandle, parent=True):
    """
    Recursively find parent/child ctrl
    :param mObjHandle: MObjectHandle
    :return: str
    """
    if mObjHandle.isValid():
        mObj = mObjHandle.object()
        mFnDag = om2.MFnDagNode(mObj)

        nextCtrlNode = mFnDag.parent(0)
        if not parent:
            nextCtrlNode = mFnDag.child(0)

        mFnDepend = om2.MFnDependencyNode(nextCtrlNode)
        nextCtrlNodePath = dagPath.getAPathTo(nextCtrlNode)
        nextCtrlNodeMObjHandle = om2.MObjectHandle(nextCtrlNode)

        if not nextCtrlNode.apiType() == om2.MFn.kWorld:
            try:
                shape = nextCtrlNodePath.extendToShape()
                if shape.apiType() == om2.MFn.kNurbsCurve:
                    return mFnDepend.name()
            except:
                return getNextCtrlNode(nextCtrlNodeMObjHandle)
        else:
            return ""


def organizeData(jsonDataDict, ctrlName, parentNode, matrix):
    """
    Organizes data ready to be exported to json file
    :param ctrlName: str, fullDagPath with namespace replaced with wildcard sign
    :param matrix
    :return: json
    """
    matrixForSerialization = tuple(matrix)
    jsonDataDict.update(
        {
            ctrlName:
                {
                    "parent": parentNode,
                    "matrix": matrixForSerialization
                }
        }
    )

    return jsonDataDict


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

        transX = mFn.findPlug("translateX", False)
        transY = mFn.findPlug("translateY", False)
        transZ = mFn.findPlug("translateZ", False)
        transX.setFloat(trans.x)
        transY.setFloat(trans.y)
        transZ.setFloat(trans.z)

        rotX = mFn.findPlug("rotateX", False)
        rotY = mFn.findPlug("rotateY", False)
        rotZ = mFn.findPlug("rotateZ", False)
        rotX.setFloat(rot.x)
        rotY.setFloat(rot.y)
        rotZ.setFloat(rot.z)

        if matchScl:
            scl = mTransMtx.scale(om2.MSpace.kObject)
            rotX = mFn.findPlug("scaleX", False)
            rotY = mFn.findPlug("scaleY", False)
            rotZ = mFn.findPlug("scaleZ", False)
            rotX.setFloat(scl[0])
            rotY.setFloat(scl[1])
            rotZ.setFloat(scl[2])


def getMatrix(mObjectHandle, matrixPlug="worldMatrix"):
    """
    Get matrix, if plug is an array it will return index 0 of that plug
    :param mObjectHandle: MObjectHandle
    :return: matrix
    """
    if mObjectHandle.isValid():
        mObj = mObjectHandle.object()
        mFn = om2.MFnDependencyNode(mObj)
        mtxPlug = mFn.findPlug(matrixPlug, False)

        if mtxPlug.isArray:
            mtxPlug = mtxPlug.elementByLogicalIndex(0)

        plugMObj = mtxPlug.asMObject()
        mFnMtxData = om2.MFnMatrixData(plugMObj)
        mtx = mFnMtxData.matrix()

        return mtx


def setNextNode(nextNode, jsonData):
    pass


def saveCtrlMtx():
    """
    Save all selected ctrl's world matrix
    """
    selList = om2.MGlobal.getActiveSelectionList()
    mObjs = [selList.getDependNode(idx) for idx in range(selList.length())]
    jsonDataDict = dict()

    for mObj in mObjs:
        if mObj.apiType() == om2.MFn.kTransform:
            mObjHandle = om2.MObjectHandle(mObj)
            dagPath = om2.MDagPath()
            pathName = dagPath.getAPathTo(mObj).partialPathName()

            pathNameNoNameSpace = stripNameSpace(pathName)

            mtx = getMatrix(mObjHandle)
            nextCtrlNode = getNextCtrlNode(mObjHandle)
            jsonDataDict = organizeData(jsonDataDict, pathNameNoNameSpace, nextCtrlNode, mtx)

    if os.path.isdir(USERHOMEPATH):
        toFile(jsonDataDict, filename)
    else:
        os.makedirs(USERHOMEPATH)
        toFile(jsonDataDict, filename)


def loadCtrlMtx(matchScl=True):
    """
    load ctrl mtx
    if: there is a selection the script will try to load the value on the selected ctrl
    else: try to load everything from file
    """
    selList = om2.MGlobal.getActiveSelectionList()
    jsonData = fromFile(filename)

    mObjs = [selList.getDependNode(idx) for idx in range(selList.length())]
    for mobj in mObjs:
        mFn = om2.MFnDependencyNode(mobj)
        name = mFn.name()
        objName = stripNameSpace(name)

        if objName in jsonData:
            ctrlParent = jsonData[objName].get("parent")
            mMtx = om2.MMatrix(jsonData[objName].get("matrix"))
            drivenMObjHandle = om2.MObjectHandle(mobj)
            parentInverseMtx = getMatrix(drivenMObjHandle, "parentInverseMatrix")
            mMtx = mMtx * parentInverseMtx
            setAtters(drivenMObjHandle, mMtx, matchScl=matchScl)
        else:
            print("{} is not in the saved json dictionary!".format(objName))
    print("Done!")
