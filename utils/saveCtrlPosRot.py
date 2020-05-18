import os
import json
import maya.api.OpenMaya as om2

def getTransRot(mObjectHandle):
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

        return((trans, rot))

selList = om2.MGlobal.getActiveSelectionList()
mObjs = [selList.getDependNode(idx) for idx in range(selList.length())]

for mObj in mObjs:
    mObjHandle = om2.MObjectHandle(mObj)
    mFn = om2.MFnDependencyNode(mObj)
    mObjName = mFn.name()
    if mObj.apiType() == om2.MFn.kTransform:
        if mFn.namespace:
            mObjName = mObjName.split(":")[1]

        print(getTransRot(mObjHandle))

