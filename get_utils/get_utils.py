import maya.api.OpenMaya as om2


def getTypeNameTypeId(mObj):
    """
    Taskes an MObject and returns MObject name and type number
    :param mObj: MObject
    :return: tuple - (typeName, typeNumber)
    """
    mFn = om2.MFnDependencyNode(mObj)
    return (mFn.type(), mFn.typeName)

def getConnectedInputs(mObj):
    """
    Takes an MObject and list all of the connected
    :param mObj:
    :return:
    """
    pass

def getConnectedOutput(mObj):
    pass