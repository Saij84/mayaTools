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

jsonDataDict = dict()
parentList = list()


def toFile(jsonDataDump, filename):
    """
    Write to json file
    :param jsonDataDump: json data
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


def stripNameSpace(objName):
    """
    Check to see if there is a namespace on the incoming name, if yes, strip and return name with no namespace
    :param name: str
    :return: str, name with no namespace
    """
    name = objName
    if ":" in name:
        name = name.split(":")[1]
    return name


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
                "parent": parentNode,
                "matrix": matrix
            }
    }
    return nodeDict


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


def getNextCtrlNode(mObjHandle):
    """
    Recursively find parent/child ctrl
    :param mObjHandle: MObjectHandle
    :return: None
    """
    if mObjHandle.isValid():
        mObj = mObjHandle.object()
        mFnDag = om2.MFnDagNode(mObj)
        nextCtrlNode = mFnDag.parent(0)
        parentMFnDag = om2.MFnDagNode(nextCtrlNode)

        mFnDepend = om2.MFnDependencyNode(nextCtrlNode)
        nextCtrlNodeMObjHandle = om2.MObjectHandle(nextCtrlNode)

        name = stripNameSpace(mFnDag.name())
        parentName = stripNameSpace(mFnDepend.name())
        mtx = getMatrix(mObjHandle)

        if nextCtrlNode.apiType() == om2.MFn.kWorld or \
                parentMFnDag.child(0).apiType() == om2.MFn.kNurbsCurve:
                jsonDataDict.update(jsonNode(name, "", mtx))
                return
        else:
            jsonDataDict.update(jsonNode(name, parentName, mtx))
            getNextCtrlNode(nextCtrlNodeMObjHandle)


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
        serializableMtx = tuple(mtx)
        return serializableMtx


def getParentList(jsonData, objName):
    """
    Recursively add the parent srtBuffers to a parentList
    :param jsonData: json
    :param objName: str
    :return: None
    """
    if jsonData[objName].get("parent") == "":
        return
    else:
        parent = jsonData[objName].get("parent")
        parentList.append(parent)
        getParentList(jsonData, parent)


def saveCtrlMtx():
    """
    Save all selected ctrl's world matrix
    """
    selList = om2.MGlobal.getActiveSelectionList()
    mObjs = [selList.getDependNode(idx) for idx in range(selList.length())]

    for mObj in mObjs:
        if mObj.apiType() == om2.MFn.kTransform:
            mObjHandle = om2.MObjectHandle(mObj)
            getNextCtrlNode(mObjHandle)

    if os.path.isdir(USERHOMEPATH):
        toFile(jsonDataDict, filename)
    else:
        os.makedirs(USERHOMEPATH)
        toFile(jsonDataDict, filename)
    print("Save Done!")

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

        parentList.append(objName)
        getParentList(jsonData, objName)

        if objName in jsonData:
            for parent in reversed(parentList):
                parentSelList = om2.MGlobal.getSelectionListByName(parent)
                parentMObj = parentSelList.getDependNode(0)
                parentMtx = om2.MMatrix(jsonData[parent].get("matrix"))
                drivenMObjHandle = om2.MObjectHandle(parentMObj)
                parentInverseMtx = getMatrix(drivenMObjHandle, "parentInverseMatrix")
                parentInverseMMtx = om2.MMatrix(parentInverseMtx)

                mtx = parentMtx * parentInverseMMtx
                setAtters(drivenMObjHandle, mtx, matchScl=matchScl)
        else:
            print("{} is not in the saved json dictionary!".format(objName))
    print("Load Done!")
