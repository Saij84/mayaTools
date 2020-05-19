import os
import json
import math
import maya.api.OpenMaya as om2

USERHOMEPATH = r"C:\mayaCtrlJsons"
FILENAME = "ctrlRotPos_001.json"
jsonDataDict = {"savedCtrls": {}}

def getTransRot(mObjectHandle):
    """
    Get translation and rotation of passed in MObjectHandle
    :param mObjectHandle: MObjectHandle
    :return: tuples ((tx, ty, tz), (rx, ry, rz))
    """
    if mObjectHandle.isValid():
        mObj = mObjectHandle.object()
        mFn = om2.MFnDependencyNode(mObj)
        getMtxPlug = mFn.findPlug("worldMatrix", False)

        mtxPlug = getMtxPlug.elementByLogicalIndex(0)
        plugMObj = mtxPlug.asMObject()
        mFnMtxData = om2.MFnMatrixData(plugMObj)

        mTransMtx = om2.MTransformationMatrix(mFnMtxData.matrix())
        trans = mTransMtx.translation(om2.MSpace.kWorld)
        rot = mTransMtx.rotation(asQuaternion=False)
        rotDegree = (math.degrees(rot[0]), math.degrees(rot[1]), math.degrees(rot[2]))
        return (trans, rotDegree)


def toFile(jsonDataDump):
    """
    Write to json file
    :param jsonDataDump: jason data
    :return: None
    """
    with open(os.path.join(USERHOMEPATH, FILENAME), "w") as jDump2File:
        json.dump(jsonDataDump, jDump2File)


def data2Json(ctrlName, transRotData):
    """
    Organizes data to be exported
    :param ctrlName: str, fullDagPath with no namespace
    :param transRotData: tuple, ((tx, ty, tz), (rx, ry, rz))
    :return: json
    """
    translateData, rotateData = transRotData

    jsonDataDict["savedCtrls"].update(
        {
            ctrlName: {
                'translateX': translateData[0],
                'translateY': translateData[1],
                'translateZ': translateData[2],
                'rotateX': rotateData[0],
                'rotateY': rotateData[1],
                'rotateZ': rotateData[2]
            }
        }
    )

    return jsonDataDict


def constructNiceName(fullPathName):
    splitNameList = fullPathName.split("|")
    objectName = splitNameList[-1]

    if ":" in objectName:
        nameNoNamespace = "*:{}".format(objectName.split(":")[-1])
        splitNameList[-1] = nameNoNamespace

    niceName = ("|".join(splitNameList))

    return niceName


selList = om2.MGlobal.getActiveSelectionList()
mObjs = [selList.getDependNode(idx) for idx in range(selList.length())]

for mObj in mObjs:
    if mObj.apiType() == om2.MFn.kTransform:
        mObjHandle = om2.MObjectHandle(mObj)
        dagPath = om2.MDagPath()
        pathName = dagPath.getAPathTo(mObj).fullPathName()
        niceName = constructNiceName(pathName)

        transRotdata = getTransRot(mObjHandle)
        jsonDataDict = data2Json(niceName, transRotdata)

        if os.path.isdir(USERHOMEPATH):
            toFile(jsonDataDict)
        else:
            os.makedirs(USERHOMEPATH)
            toFile(jsonDataDict)
