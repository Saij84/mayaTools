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


def fromFile():
    filename = max(fileList)
    print("Loading json file: {}".format(filename))
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
    jsonDataDict.update({ctrlName: matrixForSerialization})

    return jsonDataDict


def setAtters(mObjectHandle, mtx):
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


def saveCtrlMtx():
    """
    Save all selected ctrl's world matrix
    """
    selList = om2.MGlobal.getActiveSelectionList()
    mObjs = [selList.getDependNode(idx) for idx in range(selList.length())]
    newFileName = "{}_{}.json".format(baseName, "001")
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
        if len(fileList) > 0:
            newFileName = constructNewFilename(baseName)

        toFile(jsonDataDict, newFileName)
        folderCleanup(fileList)
    else:
        os.makedirs(USERHOMEPATH)
        toFile(jsonDataDict, newFileName)


def createConstraints(driver, driven):
    pConstraint = cmds.parentConstraint(driver, driven, maintainOffset=False)
    cmds.delete(pConstraint)


def loadCtrlMtx():
    """
    load ctrl mtx
    if: there is a selection the script will try to load the value on the specific ctrl
    else: try to load everything from file
    """
    selList = om2.MGlobal.getActiveSelectionList()
    mDagMod = om2.MDagModifier()
    jsonData = fromFile()
    matchObject = mDagMod.createNode("transform")
    matchObjectHandle = om2.MObjectHandle(matchObject)
    mDagMod.doIt()

    if not selList.length():
        for key, value in jsonData.items():
            fullName = "*:{}".format(key)
            selList = om2.MSelectionList()
            selList.add(fullName)
            mMtx = om2.MMatrix(value)
            setAtters(matchObjectHandle, mMtx)

            mDagPath = om2.MDagPath()
            driverPath = mDagPath.getAPathTo(matchObject)
            createConstraints(driverPath, fullName)
    else:
        mObjs = [selList.getDependNode(idx) for idx in range(selList.length())]

        for mobj in mObjs:
            mFn = om2.MFnDependencyNode(mobj)
            objName = mFn.name()

            if mFn.namespace:
                objName = objName.split(":")[-1]

            if objName in jsonData:
                mMtx = om2.MMatrix(jsonData.get(objName))
                setAtters(matchObjectHandle, mMtx)
                mDagPath = om2.MDagPath()
                driverPath = mDagPath.getAPathTo(matchObject)
                createConstraints(driverPath, "*:{}".format(objName))

    mDagMod.deleteNode(matchObject)


# saveCtrlMtx()
loadCtrlMtx()
