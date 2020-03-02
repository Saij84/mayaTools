"""
Author:Fangmin Chen
Version: 0.1

This script will copy shape/s node apply negX across XY plane

USAGE: Select curve/s, run script
"""

import maya.api.OpenMaya as om2


def getNodeMatrix(mObjHandle, searchString="worldMatrix"):
    """
    Search for a matrix plug and return it as a MMatrix
    :param mObjHandle: MObjectHandle
    :param searchString: string
    :return: MMatrix
    """
    if mObjHandle.isValid():
        mObj = mObjHandle.object()
        mFn = om2.MFnDependencyNode(mObj)
        getMtxPlug = mFn.findPlug(searchString, False)

        # Handle array plugs
        mtxPlug = getMtxPlug
        if getMtxPlug.isArray:
            mtxPlug = getMtxPlug.elementByLogicalIndex(0)
        plugMObj = mtxPlug.asMObject()

        mFnMtxData = om2.MFnMatrixData(plugMObj)
        mMatrixData = mFnMtxData.matrix()

        return mMatrixData


def createDagNode(nodeType, nodeName, mDagMod):
    """
    Create and rename node
    :param nodeType: string
    :param nodeName: string
    :param mDagMod: MDagModifier
    :return: MObjectHandle
    """
    nodeMObj = mDagMod.createNode(nodeType)
    mDagMod.renameNode(nodeMObj, nodeName)
    mDagMod.doIt()

    nodeMObjHandle = om2.MObjectHandle(nodeMObj)
    return nodeMObjHandle


mDagMod = om2.MDagModifier()
selList = om2.MGlobal.getActiveSelectionList()
mObjs = [selList.getDependNode(idx) for idx in range(selList.length())]

# Construct negX matrix
negX = (
    -1, 0, 0, 0,
    0, 1, 0, 0,
    0, 0, 1, 0,
    0, 0, 0, 1
)
negXMtx = om2.MMatrix(negX)

for mObj in mObjs:
    # Get current selection MObject
    mObjHandle = om2.MObjectHandle(mObj)
    mFn = om2.MFnDependencyNode(mObj)
    objName = mFn.name()

    # Create a group node to apply the world matrix and potentially negX matrix
    transformMObj = om2.MObject()  # Placeholder for transform MObject as it needs to be accessed later in the script
    transformNode = createDagNode("transform", "{}_COPY".format(objName), mDagMod)
    if transformNode.isValid():
        transformMObj = transformNode.object()

    # Get shape node and get shape node control points
    nurbsMFn = om2.MFnNurbsCurve()
    dagPath = selList.getDagPath(0)
    shape = dagPath.extendToShape()
    shapeMObj = shape.node()

    # Copy and parent selected shape
    nurbsMFn.copy(shapeMObj, transformMObj)

    # Get from matrix translate, rotate and scale
    worldMtx = getNodeMatrix(mObjHandle) * negXMtx
    mTransMtx = om2.MTransformationMatrix(worldMtx)
    scale = mTransMtx.scale(om2.MSpace.kWorld)
    rot = mTransMtx.rotation()
    trans = mTransMtx.translation(om2.MSpace.kWorld)

    transformDict = {"translate": trans,
                     "rotate": rot,
                     "scale": scale}

    # Apply world transform (could include negX mtx)
    transformMFn = om2.MFnDependencyNode(transformMObj)
    srtAttrs = ["translate", "rotate", "scale"]
    for attr in srtAttrs:
        attrPlug = transformMFn.findPlug(attr, False)
        attrPlug.child(0).setFloat(transformDict[attr][0])
        attrPlug.child(1).setFloat(transformDict[attr][1])
        attrPlug.child(2).setFloat(transformDict[attr][2])

print("Your curve/s has been copied and negX-ed!")
mDagMod.doIt()
