"""
Author:Fangmin Chen
Version: 0.1

This script designed to copy a shapes index/RGB override color value/s
USAGE: select Source, select Target/s then run script
"""

import maya.api.OpenMaya as om2

selList = om2.MGlobal.getActiveSelectionList()
mObjs = [selList.getDependNode(idx) for idx in range(selList.length())]

assert len(mObjs) > 1, "Select two or more nodes source then target/s"

def getShapeMObj(mObjHandle):
    """
    Get the shape MObject from an transform node
    :param mObjHandle: MObjectHandle
    :return: MObject
    """
    mObj = mObjHandle.object()
    mDagPath = om2.MDagPath.getAPathTo(mObj)
    shape = mDagPath.extendToShape()
    shapeMObj = shape.node()
    shapeMObj

    return shapeMObj

srcMObjHandle = om2.MObjectHandle(mObjs[0])
srcShapeMObj = getShapeMObj(srcMObjHandle)
srcMFn = om2.MFnDependencyNode(srcShapeMObj)

# Get/Set override color
srcDisplayOverridePlug = srcMFn.findPlug("overrideEnabled", False)
srcDisplayOverridePlug.setBool(True)

# Get override color index
srcOverrideRGBPlug = srcMFn.findPlug("overrideColorRGB", False)
srcOverrideColorPlug = srcMFn.findPlug("overrideColor", False)
srcOverrideColorVal = srcOverrideColorPlug.asInt()

for mObj in mObjs[1:]:
    trgMObjHandle = om2.MObjectHandle(mObj)
    trgShapeMObj = getShapeMObj(trgMObjHandle)
    trgMFn = om2.MFnDependencyNode(trgShapeMObj)

    # Get/Set override color
    trgDisplayOverridePlug = trgMFn.findPlug("overrideEnabled", False)
    trgDisplayOverridePlug.setBool(True)

    # Get plugs
    trgOverrideRGBPlug = trgMFn.findPlug("overrideColorRGB", False)
    trgOverrideColorPlug = trgMFn.findPlug("overrideColor", False)

    # Get source RGB values
    srcRGBValList = list()
    for idx in range(srcOverrideRGBPlug.numChildren()):
        srcChildPlug = srcOverrideRGBPlug.child(idx)
        srcRGBVal = srcChildPlug.asFloat()
        srcRGBValList.append(srcRGBVal)

    # Set target RBG/Index values
    for idx, val in enumerate(srcRGBValList):
        trgOverrideColorPlug.setInt(srcOverrideColorVal)
        trgChildPlug = trgOverrideRGBPlug.child(idx)
        trgChildPlug.setFloat(val)
