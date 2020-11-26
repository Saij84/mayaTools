import json
import maya.api.OpenMaya as om2


def toFile(jsonDataDump, fullPath):
    """
    Write to json file
    :param jsonDataDump: json data
    :return: None
    """
    with open(fullPath, 'w') as jDump2File:
        json.dump(jsonDataDump, jDump2File)


def fromFile(fullPath):
    """
    Read json file
    :param filename: str
    :return: json dictionary
    """
    with open(fullPath, 'r') as jsonFile:
        jsonData = json.load(jsonFile)
        return jsonData


def getMatrix(mObjectHandle, matrixPlug='worldMatrix'):
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


def stripNameSpace(objName):
    """
    Check to see if there is a namespace on the incoming name, if yes, strip and return name with no namespace
    :param name: str
    :return: str, name with no namespace
    """
    name = objName
    if ':' in name:
        name = name.split(':')[-1]
    return name
