import re
import maya.api.OpenMaya as om2
import maya.cmds as cmds

def getSelectedCvID(shapeCVList):
    """
    Takes maya.cmds selection list to parese for the selected CVs id
    :param shapeCVList: list, maya.cmds selection list
    :return: list of ints
    """
    cvIdList = list()
    for shapeID in shapeCVList:
        rangeList = reComp.findall(shapeID)
        rangeString = rangeList[0]
        if ":" in rangeString:
            idMin, idMax = rangeString.split(":")
            idRange = range(int(idMin), int(idMax) + 1)
            cvIdList += idRange
        else:
            cvIdList.append(int(rangeString))
    return cvIdList

reComp = re.compile("\[(.*?)\]")
shapeCVList = cmds.ls(sl=True)
cvIDList = getSelectedCvID(shapeCVList)

mDagMod = om2.MDagModifier()
selList = om2.MGlobal.getActiveSelectionList()

mObj = selList.getDependNode(0)
mFn = om2.MFnDependencyNode(mObj)
objName = mFn.name()

dagPath = selList.getDagPath(0)
shape = dagPath.extendToShape()
shapeMObj = shape.node()

shapeMFn = om2.MFnDependencyNode(shapeMObj)
shapeCtrlPoints = shapeMFn.findPlug("controlPoints", False)

crvVectors = list()
for idx in cvIDList:
    shapeElement = shapeCtrlPoints.elementByLogicalIndex(idx)
    shapePointValX = shapeElement.child(0).asFloat()
    shapePointValY = shapeElement.child(1).asFloat()
    shapePointValZ = shapeElement.child(2).asFloat()

    crvVectors.append((shapePointValX, shapePointValY, shapePointValZ))

print(crvVectors)
