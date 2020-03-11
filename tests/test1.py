import maya.api.OpenMaya as om2

selList = om2.MGlobal.getActiveSelectionList()
mObjs = [selList.getDependNode(idx) for idx in range(selList.length())]

for mObj in mObjs:
    mFn = om2.MFnDependencyNode(mObj)
    print(mFn.name())
