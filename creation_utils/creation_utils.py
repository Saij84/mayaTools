import maya.api.OpenMaya as om2


def createDAGNode(dagNodeType, nodeName="newDAGNode"):
    """
    Create a new new DAG node of type with name
    :param createNodeType: str - node type
    :param nodeName: str
    :return: MObject - new node MObject
    """
    dagMod = om2.MDagModifier()
    newDAGNode = dagMod.createNode(dagNodeType)
    dagMod.renameNode(newDAGNode, nodeName + "_" + dagNodeType)
    dagMod.doIt()
    return newDAGNode


def createDGNode(dgNodeType, nodeName="newDGNode"):
    """
    Create a new new DG node of type with name
    :param createNodeType: str - node type
    :param nodeName: str
    :return: MObject - new node MObject
    """
    dgMod = om2.MDGModifier()
    newDGNode = dgMod.createNode(dgNodeType)
    dgMod.renameNode(newDGNode, nodeName + "_" + dgNodeType)
    dgMod.doIt()
    return newDGNode
