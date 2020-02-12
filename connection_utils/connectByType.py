"""
Author:Fangmin Chen
Version: 0.1

This script is created to make life easier for ppl riggers that do a lot of connections in the Graph Editor.
Its designed to be easiely extended to encompas more node simply adding more node to the typeDict dictionary
in form of: {NODETYPE: (INPUTPLUG, OUTPUTPLUG)}
"""

import maya.api.OpenMaya as om2
dgMod = om2.MDGModifier()

typeDict = {
    "decomposeMatrix": ("inputMatrix", ["outputRotate", "outputTranslate", "outputScale"]),
    "transform": (["rotate", "translate", "scale"], "worldMatrix"),
    "multMatrix": ("matrixIn", "matrixSum"),
    "inverseMatrix": ("inputMatrix", "outputMatrix")}


def getInputOutput(srcMobj, trgMobj):
    """
    Get input based on selected MObjects
    :param srcMobj: MObject
    :param trgMobj: MObject
    :return: None
    """
    srcMFn = om2.MFnDependencyNode(srcMobj)
    trgMFn = om2.MFnDependencyNode(trgMobj)

    srcType = srcMFn.typeName
    trgType = trgMFn.typeName

    srcInputPlugs, srcOutputPlugs = typeDict[srcType]
    trgInputPlugs, trgOutputPlugs = typeDict[trgType]
    ioPlugsList = [srcInputPlugs, srcOutputPlugs, trgInputPlugs, trgOutputPlugs]

    return tuple(ioPlugsList)


def connectSRT(srcMobjHandle, trgMobjHandle):
    """
    Connect Scale, Rotate and Translate
    :param srcMobjHandle: MObjectHandle
    :param trgMObjHandle: MObjectHandle
    :return: None
    """
    assert srcMobjHandle.isValid() == True, "src MObject not valid"
    assert trgMobjHandle.isValid() == True, "trg MObject not valid"

    srcMobj = srcMobjHandle.object()
    trgMobj = trgMobjHandle.object()

    srcMFn = om2.MFnDependencyNode(srcMobj)
    trgMFn = om2.MFnDependencyNode(trgMobj)

    srcInputPlugs, srcOutputPlugs, trgInputPlugs, trgOutputPlugs = getInputOutput(srcMobj, trgMobj)
    ioCombinedList = zip(srcOutputPlugs, trgInputPlugs)
    for outAttr, inAttr in ioCombinedList:
        srcPlug = srcMFn.findPlug(outAttr, False)
        trgPlug = trgMFn.findPlug(inAttr, False)
        dgMod.connect(srcPlug, trgPlug)


def connectNodes(srcMobjHandle, trgMobjHandle):
    """
    connect nodes
    :param srcMobjHandle: MObjectHandle
    :param trgMobjHandle: MObjectHandle
    :return: None
    """
    assert srcMobjHandle.isValid() == True, "src MObject not valid"
    assert trgMobjHandle.isValid() == True, "trg MObject not valid"

    srcMobj = srcMobjHandle.object()
    trgMobj = trgMobjHandle.object()

    srcMFn = om2.MFnDependencyNode(srcMobj)
    trgMFn = om2.MFnDependencyNode(trgMobj)

    srcInputPlugs, srcOutputPlugs, trgInputPlugs, trgOutputPlugs = getInputOutput(srcMobj, trgMobj)
    srcPlug = srcMFn.findPlug(srcOutputPlugs, False)
    trgPlug = trgMFn.findPlug(trgInputPlugs, False)

    if srcPlug.isArray and not trgMFn.hasAttribute("matrixIn"):
        srcWorldMtxPlug = srcPlug.elementByLogicalIndex(0)
        dgMod.connect(srcWorldMtxPlug, trgPlug)
        print("connecting: {} to {}".format(srcWorldMtxPlug, trgPlug))
    elif trgMFn.hasAttribute("matrixIn"):
        srcWorldMtxPlug = srcPlug.elementByLogicalIndex(0)
        trgMtxPlug = trgPlug.elementByLogicalIndex(0)
        dgMod.connect(srcWorldMtxPlug, trgMtxPlug)
        print("connecting: {} to {}".format(srcWorldMtxPlug, trgMtxPlug))
    else:
        dgMod.connect(srcPlug, trgPlug)


selList = om2.MGlobal.getActiveSelectionList()
mobjs = [selList.getDependNode(idx) for idx in range(selList.length())]
srcMFn = om2.MFnDependencyNode(mobjs[0])
srcMobjHandle = om2.MObjectHandle(mobjs[0])
srcType = srcMFn.typeName

for mobj in mobjs[1:]:
    trgMobjHandle = om2.MObjectHandle(mobj)
    if srcType == "decomposeMatrix":
        connectSRT(srcMobjHandle, trgMobjHandle)
    else:
        connectNodes(srcMobjHandle, trgMobjHandle)

dgMod.doIt()
