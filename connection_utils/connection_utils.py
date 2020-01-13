import maya.api.OpenMaya as om2
from mayaTools.creation_utils import creation_utils as cUtils
from mayaTools.constants import type_constants as tConst


def connectWithDecompMtx(srcMobj, trgMobj):
    """
    Connect and two DAG nodes using matrixDecompose
    :param srcMobj: MObject
    :param trgMobj: MObject
    :return: None
    """
    assert srcMobj, "Please select a source"
    assert trgMobj, "Please select a target"

    dgMod = om2.MDGModifier()
    srcMFn = om2.MFnDependencyNode(srcMobj)
    trgMFn = om2.MFnDependencyNode(trgMobj)

    decompMobj = cUtils.createDGNode(tConst.DECOMPOSEMATRIX, nodeName="")

    srcPlug = srcMFn.findPlug("worldMatrix", False)
    srcWorldMtxPlug = srcPlug.elementByLogicalIndex(0)

    decompMfn = om2.MFnDependencyNode(decompMobj)
    decompMfnPlug = decompMfn.findPlug("inputMatrix", False)

    for srcAttr, trgAttr in [("outputRotate", "rotate"), ("outputTranslate", "translate"), ("outputScale", "scale")]:
        srcPlug = decompMfn.findPlug(srcAttr, False)
        trgPlug = trgMFn.findPlug(trgAttr, False)
        dgMod.connect(srcPlug, trgPlug)

    dgMod.connect(srcWorldMtxPlug, decompMfnPlug)

    dgMod.doIt()
