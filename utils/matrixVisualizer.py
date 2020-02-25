import maya.api.OpenMaya as om2


def createLocator(name, mDagMod):
    """
    create a locator with vertexID in the name
    :param componentID: int
    :return: MObjectHandle
    """
    locLocalScale = 0.1
    mDagMod = om2.MDagModifier()
    mDagPath = om2.MDagPath()
    loc = mDagMod.createNode("locator")
    newName = "LOC_f{}".format(name)
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


def getPolygonCenter(selList, mDagMod):
    """
    Method to iter through an selection list components and return center of an polygon
    :param selList: MSelectionList
    :return: list
    """
    iter = om2.MItSelectionList(selList, om2.MFn.kMeshPolygonComponent)

    while not iter.isDone():
        dag, mObj = selList.getComponent(0)
        idList = om2.MFnSingleIndexedComponent(mObj)
        idElement = idList.getElements()
        polyIter = om2.MItMeshPolygon(dag, mObj)
        while not polyIter.isDone():
            triMPointList, triVtxID = polyIter.getTriangle(0)
            point1 = triMPointList[0]
            point2 = triMPointList[1]
            point3 = triMPointList[2]

            polygonCenterMPoint = polyIter.center(om2.MSpace.kWorld)

            p1Vector = om2.MVector(point1.x, point1.y, point1.z)
            p2Vector = om2.MVector(point2.x, point2.y, point2.z)

            p2MidVector = p2Vector - p1Vector

            vector1 = point3 - point1
            vector2 = point2 - point1
            normalVector = vector1 ^ -vector2

            mtx = (
                normalVector.x, normalVector.y, normalVector.z, 0,
                p2MidVector.x, p2MidVector.y, p2MidVector.z, 0,
                0, 0, 1, 0,
                polygonCenterMPoint.x, polygonCenterMPoint.y, polygonCenterMPoint.z, polygonCenterMPoint.w
            )

            compositMtx = om2.MMatrix(mtx)
            mTransMtx = om2.MTransformationMatrix(compositMtx)
            trans = mTransMtx.translation(om2.MSpace.kWorld)
            rot = mTransMtx.rotation()

            locMObjHandle = createLocator(idElement[0], mDagMod)
            if locMObjHandle.isValid():
                locMObj = locMObjHandle.object()
                locMFn = om2.MFnDependencyNode(locMObj)

                transX = locMFn.findPlug("translateX", False)
                transY = locMFn.findPlug("translateY", False)
                transZ = locMFn.findPlug("translateZ", False)
                transX.setFloat(trans.x)
                transY.setFloat(trans.y)
                transZ.setFloat(trans.z)

                rotX = locMFn.findPlug("rotateX", False)
                rotY = locMFn.findPlug("rotateY", False)
                rotZ = locMFn.findPlug("rotateZ", False)
                rotX.setFloat(rot.x)
                rotY.setFloat(rot.y)
                rotZ.setFloat(rot.z)
            polyIter.next(0)
        iter.next()

selList = om2.MGlobal.getActiveSelectionList()
mDagMod = om2.MDagModifier()

getPolygonCenter(selList, mDagMod)
