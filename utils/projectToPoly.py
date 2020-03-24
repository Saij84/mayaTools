import maya.api.OpenMaya as om2

def createDagNode(nodeType, nodeName, mDagMod):
    dagNode = mDagMod.createNode(nodeType)
    mDagMod.renameNode(dagNode, nodeName)
    dagNodeMObjHandle = om2.MObjectHandle(dagNode)

    return dagNodeMObjHandle

def createDgNode(nodeType, nodeName, mDgMod):
    dgNode = mDgMod.createNode(nodeType)
    mDgMod.renameNode(dgNode, nodeName)
    dgNodeMObjHandle = om2.MObjectHandle(dgNode)

    return dgNodeMObjHandle

def createLocator(name, selType, mDagMod):
    """
    create a locator with vertexID in the name
    :param componentID: str/int
    :param selType: str
    :param mDagMod: MDagModifier
    :return: MObjectHandle
    """
    locLocalScale = 0.1
    mDagPath = om2.MDagPath()
    loc = mDagMod.createNode("locator")
    newName = "{}_{}_LOC".format(selType, name)
    mDagMod.renameNode(loc, newName)

    locMObjHandle = om2.MObjectHandle(loc)
    mDagMod.doIt()

    dagPath = mDagPath.getAPathTo(loc)
    shapeDagPath = dagPath.extendToShape()
    shapeMObj = shapeDagPath.node()
    shapeMFn = om2.MFnDependencyNode(shapeMObj)

    shapeLocalScaleX = shapeMFn.findPlug("localScaleX", False)
    shapeLocalScaleY = shapeMFn.findPlug("localScaleY", False)
    shapeLocalScaleZ = shapeMFn.findPlug("localScaleZ", False)
    shapeLocalScaleX.setFloat(locLocalScale)
    shapeLocalScaleY.setFloat(locLocalScale)
    shapeLocalScaleZ.setFloat(locLocalScale)

    return locMObjHandle

def getMtxRow(mtx, row):
    rowsDict = {0: [mtx.getElement(0, idx) for idx in range(4)],
                1: [mtx.getElement(1, idx) for idx in range(4)],
                2: [mtx.getElement(2, idx) for idx in range(4)],
                3: [mtx.getElement(3, idx) for idx in range(4)]}
    return rowsDict[row]

mDgMod = om2.MDagModifier()

selList = om2.MGlobal.getActiveSelectionList()

inMObj = selList.getDependNode(0)
inMFn = om2.MFnDependencyNode(inMObj)

inDagPath = selList.getDagPath(0)
shape = inDagPath.extendToShape()
shapeMObj = shape.node()
shapeMFn = om2.MFnDependencyNode(shapeMObj)
controlPointPlug = shapeMFn.findPlug("controlPoints", False)
controlPointNumb = controlPointPlug.numElements()

crvVectors = list()
for idx in range(controlPointNumb):
    shapeElement = controlPointPlug.elementByLogicalIndex(idx)
    shapePointValX = shapeElement.child(0).asFloat()
    shapePointValY = shapeElement.child(1).asFloat()
    shapePointValZ = shapeElement.child(2).asFloat()
    crvVectors.append((shapePointValX, shapePointValY, shapePointValZ))

wMtxCompPlug = inMFn.findPlug("worldMatrix", False)
wMtxPlug = wMtxCompPlug.elementByLogicalIndex(0)
wMtxPlugMObj = wMtxPlug.asMObject()
wMtxData = om2.MFnMatrixData(wMtxPlugMObj).matrix()

for idx, vector in enumerate(crvVectors):
    locMObjectHandle = createLocator(idx, "vector", mDgMod)
    if locMObjectHandle.isValid():
        locMObj = locMObjectHandle.object()

        dgNode = mDgMod.createNode("nodeType")
        mDgMod.renameNode(dgNode, nodeName)

        xMtx = (
            vector[0], vector[1], vector[2], 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1
        )

        wMtx = (
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            vector[0], vector[1], vector[2], 1
        )

        locatorMtx = om2.MMatrix(xMtx) * om2.MMatrix(wMtx) * wMtxData
        print(locatorMtx)

        mTransformMtx = om2.MTransformationMatrix(locatorMtx)
