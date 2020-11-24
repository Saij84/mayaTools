import os
import json
import maya.api.OpenMaya as om2
import mayaTools.saveLoadCtrls.core.saveLoadCtrls as core


def toFile(jsonDataDump, userPath, filename):
    '''
    Write to json file
    :param jsonDataDump: json data
    :return: None
    '''
    with open(os.path.join(userPath, filename), 'w') as jDump2File:
        json.dump(jsonDataDump, jDump2File)


def fromFile(userPath, filename):
    '''
    Read json file
    :param filename: str
    :return: json dictionary
    '''
    with open(os.path.join(userPath, filename), 'r') as jsonFile:
        jsonData = json.load(jsonFile)
        return jsonData

jsonDataDict = dict()
def getNextCtrlNode( mObjHandle):
    '''
    Recursively find parent node and stops at the given blacklist
    :param mObjHandle: MObjectHandle
    :return: None
    '''
    blackList = ['world', 'rig']
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
        if parentMFnDag.child(0).apiType() == om2.MFn.kNurbsCurve or parentMFnDag.childCount() > 1 \
                or parentName in blackList:
            jsonDataDict.update(core.jsonNode(name, '', mtx))
            return
        else:
            jsonDataDict.update(core.jsonNode(name, parentName, mtx))
            getNextCtrlNode(nextCtrlNodeMObjHandle)


def getMatrix( mObjectHandle, matrixPlug='worldMatrix'):
    '''
    Get matrix, if plug is an array it will return index 0 of that plug
    :param mObjectHandle: MObjectHandle
    :return: matrix
    '''
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


def getTreeList( jsonData, objName):
    '''
    Recursively add the parent srtBuffers to a parentList
    :param jsonData: json
    :param objName: str
    :return: None
    '''
    if jsonData[objName].get('parent') == '':
        return
    else:
        parent = jsonData[objName].get('parent')
        treeList.append(parent)
        getTreeList(jsonData, parent)


def stripNameSpace( objName):
    '''
    Check to see if there is a namespace on the incoming name, if yes, strip and return name with no namespace
    :param name: str
    :return: str, name with no namespace
    '''
    name = objName
    if ':' in name:
        name = name.split(':')[-1]
    return name
