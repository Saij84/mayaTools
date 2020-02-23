import maya.api.OpenMaya as om2


selList = om2.MGlobal.getActiveSelectionList()
mObjs = [selList.getDependNode(idx) for idx in range(selList.length())]

def getNodeMatrix(mObjHandle, searchMatrix="worldMatrix"):
    """
    Search for a matrix plug and return it as a MMatrix
    :param mObjHandle: MObjectHandle
    :param searchMatrix: string
    :return: MMatrix
    """
    if mObjHandle.isValid():
        mObj = mObjHandle.object()
        mFn = om2.MFnDependencyNode(mObj)
        getMtxPlug = mFn.findPlug(searchMatrix, False)

        mtxPlug = getMtxPlug
        if getMtxPlug.isArray:
            mtxPlug = getMtxPlug.elementByLogicalIndex(0)
        plugMObj = mtxPlug.asMObject()

        mFnMtxData = om2.MFnMatrixData(plugMObj)
        mMatrixData = mFnMtxData.matrix()

        return mMatrixData

def vectorCross(vector1, vector2):
    newVector = vector1 ^ vector2

    return newVector

print(vectorCross(om2.MVector(1, 0, 0), om2.MVector(0, 1, 0)))
