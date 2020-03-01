"""
Author:Fangmin Chen
Version: 0.1

This script will copy a shape node and negX it across XY plane

USAGE: Select a curve, run script
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


def createLocator(name, selType, mDagMod):
    """
    create a locator with vertexID in the name
    :param componentID: str/int
    :param selType: str
    :param mDagMod: MDagModifier
    :return: MObjectHandle
    """
    locLocalScale = 0.5
    mDagPath = om2.MDagPath()
    loc = mDagMod.createNode("locator")
    newName = "{}_{}_LOC".format(selType, name)
    mDagMod.renameNode(loc, newName)

    locMObjHandle = om2.MObjectHandle(loc)
    mDagMod.doIt()

    dagPath = mDagPath.getAPathTo(loc)
    shapeDagPath = dagPath.extendToShape()
    shapeMObj = shapeDagPath.node()
    shapeMFn = om2.MFnDependencyNode(shapeMObj)

    shapeLocalScaleX = shapeMFn.findPlug("localScaleX", False)
    shapeLocalScaleY = shapeMFn.findPlug("localScaleY", False)
    shapeLocalScaleZ = shapeMFn.findPlug("localScaleZ", False)
    shapeLocalScaleX.setFloat(locLocalScale)
    shapeLocalScaleY.setFloat(locLocalScale)
    shapeLocalScaleZ.setFloat(locLocalScale)

    return locMObjHandle


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

# Create negX matrix
negX = (
    -1, 0, 0, 0,
    0, 1, 0, 0,
    0, 0, 1, 0,
    0, 0, 0, 1
)
negXMtx = om2.MMatrix(negX)

# Get current selection MObject
mObj = selList.getDependNode(0)
mObjHandle = om2.MObjectHandle(mObj)
mFn = om2.MFnDependencyNode(mObj)
objName = mFn.name()

# Create a group node to apply the world matrix and potentially negX matrix
transformMObj = om2.MObject()  # Placeholder for transform MObject as it needs to be accessed later in the script
transformNode = createDagNode("transform", "curveTransform", mDagMod)
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

mDagMod.doIt()
