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

def createCurveShape(crvName, pointVectors, closed=False):
    """
    Creates a curve with a given name
    :param crvName: string
    :param pointVectors: list of tuples
    :param closed: bool
    :return: None
    """
    # Add start point vector to the end of pointVector list to close the curve
    if closed:
        startPointVector = pointVectors[0]
        pointVectors.append(startPointVector)

    curve = cmds.curve(p=pointVectors, d=1, n=crvName)

    for shape in cmds.listRelatives(curve, s=True, f=True):
        cmds.rename(shape, "{}Shape".format(crvName))

reComp = re.compile("\[(.*?)\]")
shapeCVList = cmds.ls(sl=True)
cvIDList = getSelectedCvID(shapeCVList)
selList = om2.MGlobal.getActiveSelectionList()

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

createCurveShape("test", crvVectors, closed=False)
