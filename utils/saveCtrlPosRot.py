import os
import json
import re
import maya.api.OpenMaya as om2

FINDDIGITS = re.compile(r"\d+")
USERHOMEPATH = r"c:\mayaCtrlJsons"

filename = "ctrlRotPos_001.json"
jsonDataDict = {"savedCtrls": []}


def constructNiceName(fullPathName):
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

def constructNewFilename(filename):
    """
    Create a new name based on the largest version number in USERHOMEPATH
    :param filename: str
    :return: str
    """
    listFiles = os.listdir(USERHOMEPATH)
    baseName = filename.split("_")[0]

    versionList = list()
    for file in listFiles:
        digit = FINDDIGITS.findall(file)
        intDigit = int(digit[0])
        versionList.append(intDigit)

    maxVersionNumber = max(versionList)
    nextVersion = maxVersionNumber + 1

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

def folderCleanup(USERHOMEPATH):
    numbOfFiles = len(os.listdir(USERHOMEPATH))
    sortedFileList = sorted(os.listdir(USERHOMEPATH))

    if numbOfFiles >= 10:
        firstFile = sortedFileList[0]
        os.remove(os.path.join(USERHOMEPATH, firstFile))

def organizeData(ctrlName, matrix):
    """
    Organizes data ready to be exported to json file
    :param ctrlName: str, fullDagPath with namespace replaced with wildcard sign
    :param matrix
    :return: json
    """
    matrixForSerialization = tuple(matrix)
    jsonDataDict["savedCtrls"].append(
        {
            ctrlName: {
                "matrix": matrixForSerialization
            }
        }
    )

    return jsonDataDict


selList = om2.MGlobal.getActiveSelectionList()
mObjs = [selList.getDependNode(idx) for idx in range(selList.length())]

for mObj in mObjs:
    if mObj.apiType() == om2.MFn.kTransform:
        mObjHandle = om2.MObjectHandle(mObj)
        dagPath = om2.MDagPath()
        pathName = dagPath.getAPathTo(mObj).fullPathName()
        niceName = constructNiceName(pathName)

        mtx = getMatrix(mObjHandle)
        jsonDataDict = organizeData(niceName, mtx)

if os.path.isdir(USERHOMEPATH):
    newFileName = filename
    if os.path.exists(os.path.join(USERHOMEPATH, filename)):
        newFileName = constructNewFilename(filename)

    toFile(jsonDataDict, newFileName)

else:
    os.makedirs(USERHOMEPATH)
    toFile(jsonDataDict, filename)
