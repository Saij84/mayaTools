import maya.api.OpenMaya as om2

def sceneIter(findstring):
    """
    Find DAG node using name
    :param findstring: string
    :return: list of MObject
    """
    dagIterator = om2.MItDag()
    dagNodeFn = om2.MFnDagNode()
    returnList = list()

    while (not dagIterator.isDone()):
        dagObject = dagIterator.currentItem()
        depth = dagIterator.depth()
        dagNodeFn.setObject(dagObject)
        name = dagNodeFn.name()
        if name == findstring:
            returnList.append(dagObject)

        # print("{} ({}) depth: {}".format(name, dagObject.apiTypeStr, depth))
        dagIterator.next()
    return returnList

returnList = sceneIter("curveShape1")
print(returnList)
