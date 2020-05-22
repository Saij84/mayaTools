import os
import re
import json
import maya.api.OpenMaya as om2


FINDDIGITS = re.compile(r"\d+")
USERHOMEPATH = r"c:\mayaCtrlJsons"

filename = "ctrlWorldMtx_v001.json"
fileList = sorted(os.listdir(USERHOMEPATH))


def constructNiceMayaName(pathName):
    """
    Makes sure that namespaces are switched out for a wildcard sign
    :param pathName: str
    :return: str
    """
    splitNameList = pathName.split("|")
    objectName = splitNameList[-1]

    if ":" in objectName:
        nameNoNamespace = objectName.split(":")[-1]
        splitNameList[-1] = nameNoNamespace

    niceName = ("|".join(splitNameList))

    return niceName


def getMatrix(mObjectHandle, matrixPlug="worldMatrix"):
    """
    Get world matrix
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


def organizeData(jsonDataDict, ctrlName, matrix):
    """
    Organizes data ready to be exported to json file
    :param ctrlName: str, fullDagPath with namespace replaced with wildcard sign
    :param matrix
    :return: json
    """
    matrixForSerialization = tuple(matrix)
    jsonDataDict.update({ctrlName: matrixForSerialization})

    return jsonDataDict


def setAtters(mObjectHandle, mtx):
    """
    Sets translation/rotation
    :param mObjectHandle: MObjectHandle
    :param mtx: MMatrix
    :return: None
    """
    if mObjectHandle.isValid():
        mObj = mObjectHandle.object()
        mFn = om2.MFnDependencyNode(mObj)
        mTransMtx = om2.MTransformationMatrix(mtx)

        trans = mTransMtx.translation(om2.MSpace.kWorld)
        rot = mTransMtx.rotation()
        scl = mTransMtx.scale(om2.MSpace.kObject)

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

        rotX = mFn.findPlug("scaleX", False)
        rotY = mFn.findPlug("scaleY", False)
        rotZ = mFn.findPlug("scaleZ", False)
        rotX.setFloat(scl[0])
        rotY.setFloat(scl[1])
        rotZ.setFloat(scl[2])


def saveCtrlMtx():
    """
    Save all selected ctrl's world matrix
    """
    selList = om2.MGlobal.getActiveSelectionList()
    mObjs = [selList.getDependNode(idx) for idx in range(selList.length())]
    jsonDataDict = {}

    for mObj in mObjs:
        if mObj.apiType() == om2.MFn.kTransform:
            mObjHandle = om2.MObjectHandle(mObj)
            dagPath = om2.MDagPath()
            pathName = dagPath.getAPathTo(mObj).partialPathName()
            niceName = constructNiceMayaName(pathName)

            mtx = getMatrix(mObjHandle)
            jsonDataDict = organizeData(jsonDataDict, niceName, mtx)

    if os.path.isdir(USERHOMEPATH):
        toFile(jsonDataDict, filename)
    else:
        os.makedirs(USERHOMEPATH)
        toFile(jsonDataDict, filename)


def loadCtrlMtx():
    """
    load ctrl mtx
    if: there is a selection the script will try to load the value on the specific ctrl
    else: try to load everything from file
    """
    selList = om2.MGlobal.getActiveSelectionList()
    jsonData = fromFile(filename)

    if not selList.length():
        for ctrlName, value in jsonData.items():
            mMtx = om2.MMatrix(value)
            selList = om2.MSelectionList()
            try:
                selList.add("*:{}".format(ctrlName))
            except:
                selList.add(ctrlName)

            driven = selList.getDependNode(0)
            drivenMObjHandle = om2.MObjectHandle(driven)

            parentInverseMtx = getMatrix(drivenMObjHandle, "parentInverseMatrix")
            newMtx = mMtx * parentInverseMtx

            setAtters(drivenMObjHandle, newMtx)
        print("Attrs loaded!")
    else:
        mObjs = [selList.getDependNode(idx) for idx in range(selList.length())]
        for mobj in mObjs:
            mFn = om2.MFnDependencyNode(mobj)
            objName = mFn.name()

            if mFn.namespace:
                objName = objName.split(":")[-1]

            if objName in jsonData:
                mMtx = om2.MMatrix(jsonData.get(objName))
                drivenMObjHandle = om2.MObjectHandle(mobj)
                parentInverseMtx = getMatrix(drivenMObjHandle, "parentInverseMatrix")
                mMtx = mMtx * parentInverseMtx

                setAtters(drivenMObjHandle, mMtx)

                print("Loaded attrs on: {}".format(objName))
            else:
                print("{} is not in the saved json dictionary!".format(objName))


# saveCtrlMtx()
loadCtrlMtx()
