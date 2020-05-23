import maya.api.OpenMaya as om2

selList = om2.MGlobal.getActiveSelectionList()
mObjs = [selList.getDependNode(idx) for idx in range(selList.length())]

def findParent(mObjHandle):
    if mObjHandle.isValid():
        mObj = mObjHandle.object()
        mFnDag = om2.MFnDagNode(mObj)
        parentmObj = mFnDag.parent(0)
        mFn = om2.MFnDependencyNode(parentmObj)

        return mFn.name()
