import re
import maya.api.OpenMaya as om2

selList = om2.MGlobal.getActiveSelectionList()
mObjs = [selList.getDependNode(idx) for idx in range(selList.length())]

def getVtxIdxs(selList):
    __, vtxs = selList.getComponent(0)
    vtxList = om2.MFnSingleIndexedComponent(vtxs)
    vtxIdxList = vtxList.getElements()
    return vtxIdxList

getVtxIdxs(selList)