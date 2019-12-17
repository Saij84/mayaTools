import maya.api.OpenMaya as om2
from mayaTools.creation_utils import creation_utils as cUtils
from mayaTools.constants import type_constants as tConst

selList = om2.MGlobal.getActiveSelectionList()
srcMobj = selList.getDependNode(0)
#trgMobj = selList.getDependNode(1)



def connectWithWorldMtx(srcMobj, trgMobj):
    #assert srcMobj == True and trgMobj == True, "Please select a source and a target"

    dgMod = om2.MDGModifier()

    srcMFn = om2.MFnDependencyNode(srcMobj)
    trgMFn = om2.MFnDependencyNode(trgMobj)

    matrixMultMobj = cUtils.createDGNode(tConst.MULTMATRIX, nodeName="test")
    decompMobj = cUtils.createDGNode(tConst.DECOMPOSEMATRIX, nodeName="test")

    srcPlug = srcMFn.findPlug("worldMatrix", False)
    srcWorldMtxPlug = srcPlug.elementByLogicalIndex(0)

    matrixMultMfn = om2.MFnDependencyNode(matrixMultMobj)
    matrixMultMfnPlug = matrixMultMfn.findPlug("matrixIn", False)
    plugIdx1 = matrixMultMfnPlug.elementByLogicalIndex(1)

    dgMod.connect(srcWorldMtxPlug, plugIdx1)
#connectWithWorldMtx(srcMobj, trgMobj)




