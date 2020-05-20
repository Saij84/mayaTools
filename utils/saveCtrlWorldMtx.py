import os
import re
import json
import maya.api.OpenMaya as om2
import maya.cmds as cmds
FINDDIGITS = re.compile(r"\d+")
USERHOMEPATH = r"c:\mayaCtrlJsons"

baseName = "ctrlWorldMtx"
fileVersion = 1
fileList = sorted(os.listdir(USERHOMEPATH))


def constructNiceMayaName(fullPathName):
    """
    Makes sure that namespaces are switched out for a wildcard sign
    :param fullPathName: str
    :return: str
    """
    splitNameList = fullPathName.split("|")
    objectName = splitNameList[-1]

    if ":" in objectName:
        nameNoNamespace = "*:{}".format(objectName.split(":")[-1])
        splitNameList[-1] = nameNoNamespace

    niceName = ("|".join(splitNameList))

    return niceName


def constructNewFilename(baseName):
    """
    Create a new name based on the largest version number in USERHOMEPATH
    :param filename: str
    :return: str
    """
    digitList = list()
    for file in fileList:
        digit = FINDDIGITS.findall(file)
        digitList.append(int(digit[0]))
    maxVersion = max(digitList)
    nextVersion = maxVersion + 1
    newName = "{baseName}_{0:0=3d}.json".format(nextVersion, baseName=baseName)
    return newName


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
    with open(os.path.join(USERHOMEPATH, filename), "r") as jsonFile:
        jsonData = json.load(jsonFile)
        return jsonData


def folderCleanup(fileList):
    if len(fileList) >= 6:
        firstFile = fileList[0]
        os.remove(os.path.join(USERHOMEPATH, firstFile))


def organizeData(jsonDataDict, ctrlName, matrix):
    """
    Organizes data ready to be exported to json file
    :param ctrlName: str, fullDagPath with namespace replaced with wildcard sign
    :param matrix
    :return: json
    """
    matrixForSerialization = tuple(matrix)
    jsonDataDict["savedCtrls"].append(
        {
            ctrlName: matrixForSerialization
        }
    )

    return jsonDataDict


def saveCtrlMtx():
    """
    Save all selected ctrl's world matrix
    """
    selList = om2.MGlobal.getActiveSelectionList()
    mObjs = [selList.getDependNode(idx) for idx in range(selList.length())]
    newFileName = "{}_{}.json".format(baseName, "001")
    jsonDataDict = {"savedCtrls": []}

    for mObj in mObjs:
        if mObj.apiType() == om2.MFn.kTransform:
            mObjHandle = om2.MObjectHandle(mObj)
            dagPath = om2.MDagPath()
            pathName = dagPath.getAPathTo(mObj).fullPathName()
            niceName = constructNiceMayaName(pathName)

            mtx = getMatrix(mObjHandle)
            jsonDataDict = organizeData(jsonDataDict, niceName, mtx)

    if os.path.isdir(USERHOMEPATH):
        if len(fileList) > 0:
            newFileName = constructNewFilename(baseName)

        toFile(jsonDataDict, newFileName)
        folderCleanup(fileList)
    else:
        os.makedirs(USERHOMEPATH)
        toFile(jsonDataDict, newFileName)


def loadCtrlMtx():
    """
    load ctrl mtx
    if: there is a selection the script will try to load the value on the specific ctrl
    else: try to load everything from file
    """
    mDagMod = om2.MDagModifier()
    transformMObj = mDagMod.createNode("transform")

    jsonData = fromFile("{}_003.json".format(baseName))
    for i in jsonData["savedCtrls"]:
        for key, value in i.items():
            mMtx = om2.MMatrix(value)
            selList = om2.MSelectionList()
            selList.add(key)
            mObj = selList.getDependNode(0)
            mObjHandle = om2.MObjectHandle(mObj)
            mFn = om2.MFnDependencyNode(transformMObj)

            mTransMtx = om2.MTransformationMatrix(mMtx)
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
    mDagMod.doIt()
loadCtrlMtx()

# saveCtrlMtx()

