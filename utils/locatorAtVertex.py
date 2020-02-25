"""
Author:Fangmin Chen
Version: 0.1

This script will add an locator at a selected vertex/polygon aligned(not necessary same orientation) to its normals

USAGE: Select mesh/polygon vertex, run script
"""
import maya.api.OpenMaya as om2


def geIDsAndTypes(selList):
    """
    Get selected component's ID/s
    :param selList: MSelectionList
    :return: list of int
    """
    __, id = selList.getComponent(0)
    idList = om2.MFnSingleIndexedComponent(id)
    idElement = idList.getElements()
    selType = id.apiType()

    return idElement, selType


def createLocator(name, selType, mDagMod):
    """
    create a locator with vertexID in the name
    :param componentID: str/int
    :param selType: str
    :param mDagMod: MDagModifier
    :return: MObjectHandle
    """
    locLocalScale = 0.1
    mDagMod = om2.MDagModifier()
    mDagPath = om2.MDagPath()
    loc = mDagMod.createNode("locator")
    newName = "LOC_{}_{}".format(selType, name)
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


def createLocAtVertex(selList, componentID, mDagMod):
    """
    Create an locator on vertex aligned with the vertex normal
    :param selList: MSelectionList
    :param componentID: int
    :param mDagMod: MDagModifier
    :return: None
    """
    # Get vertex normal/position
    meshDagPath = selList.getDagPath(0)
    mFnMesh = om2.MFnMesh(meshDagPath)
    vtxNormal = mFnMesh.getVertexNormal(componentID, False, om2.MSpace.kObject)
    vtxPoint = mFnMesh.getPoint(componentID, om2.MSpace.kWorld)

    # Construct a matrix
    mtxConstruct = (
        vtxNormal.x, vtxNormal.y, vtxNormal.z, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        vtxPoint.x, vtxPoint.y, vtxPoint.z, vtxPoint.w
    )

    vtxMMatrix = om2.MMatrix(mtxConstruct)  # Convert to Maya MMatrix
    newMtx = vtxMMatrix
    vtxMtransMtx = om2.MTransformationMatrix(newMtx)

    # Get rotation/translation
    rot = vtxMtransMtx.rotation()
    trans = vtxMtransMtx.translation(om2.MSpace.kWorld)

    loc = createLocator(componentID, "vtx", mDagMod)
    if loc.isValid():
        locMObj = loc.object()
        mFn = om2.MFnDependencyNode(locMObj)

        transX = mFn.findPlug("translateX", False)
        transY = mFn.findPlug("translateY", False)
        transZ = mFn.findPlug("translateZ", False)
        transX.setFloat(trans.x)
        transY.setFloat(trans.y)
        transZ.setFloat(trans.z)

        rotX = mFn.findPlug("rotateX", False)
        rotY = mFn.findPlug("rotateY", False)
        rotZ = mFn.findPlug("rotateZ", False)
        rotX.setFloat(rot.x)
        rotY.setFloat(rot.y)
        rotZ.setFloat(rot.z)


def createLocAtFace(selList, mDagMod):
    """
    Method to create a locator at face center and align it to it's normal
    :param selList: MSelsctionList
    :param mDagMod: MDagModifier
    :return: None
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

            locMObjHandle = createLocator(idElement[0], "f", mDagMod)
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
componentIDs, typeID = geIDsAndTypes(selList)
mDagMod = om2.MDagModifier()

if typeID == 550:  # kMeshVertComponent
    for componentID in componentIDs:
        createLocAtVertex(selList, componentID, mDagMod)
elif typeID == 548:  # kMeshPolygonComponent
    createLocAtFace(selList, mDagMod)
else:
    pass
