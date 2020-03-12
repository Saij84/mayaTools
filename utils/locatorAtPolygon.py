"""
Author:Fangmin Chen
Version: 0.2

This script will add an locator at a selected polygon aligned(not necessary same orientation) to its normals

USAGE: Select mesh/polygon, run script
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


def createLocAtFace(selList, mDagMod):
    """
    Method to create a locator at face center and align it to it's normal
    :param selList: MSelsctionList
    :param mDagMod: MDagModifier
    :return: None
    """
    iter = om2.MItSelectionList(selList, om2.MFn.kMeshPolygonComponent)
    mObj = selList.getDependNode(0)
    mFn = om2.MFnDependencyNode(mObj)
    getMtxPlug = mFn.findPlug("worldMatrix", False)

    mtxPlug = getMtxPlug.elementByLogicalIndex(0)
    plugMObj = mtxPlug.asMObject()

    mFnMtxData = om2.MFnMatrixData(plugMObj)
    offsetMtx = mFnMtxData.matrix()

    while not iter.isDone():
        dag, mObj = selList.getComponent(0)
        idList = om2.MFnSingleIndexedComponent(mObj)
        idElements = idList.getElements()
        polyIter = om2.MItMeshPolygon(dag, mObj)
        while not polyIter.isDone():
            for id in idElements:
                # Get polygon points
                triMPointList, triVtxID = polyIter.getTriangle(0)
                point1 = triMPointList[0]
                point2 = triMPointList[1]
                point3 = triMPointList[2]
                polygonCenterMPoint = polyIter.center(om2.MSpace.kObject)

                # Convert points to MVectors
                p1Vector = om2.MVector(point1.x, point1.y, point1.z)
                p2Vector = om2.MVector(point2.x, point2.y, point2.z)
                p3Vector = om2.MVector(point3.x, point3.y, point3.z)

                # Find Mid points to aim at
                p1MidVector = p2Vector - p1Vector
                p2MidVector = p3Vector - p1Vector

                vector1 = point3 - point1
                vector2 = point2 - point1

                # Cross vectors NOTE: vectors2 is negative ti make X axsis aiming "out"
                normalVector = vector1 ^ -vector2

                mtx = (
                    normalVector.x, normalVector.y, normalVector.z, 0,
                    p1MidVector.x, p1MidVector.y, p1MidVector.z, 0,
                    p2MidVector.x, p2MidVector.y, p2MidVector.z, 0,
                    polygonCenterMPoint.x, polygonCenterMPoint.y, polygonCenterMPoint.z, polygonCenterMPoint.w
                )

                compositMtx = om2.MMatrix(mtx) * offsetMtx
                mTransMtx = om2.MTransformationMatrix(compositMtx)
                trans = mTransMtx.translation(om2.MSpace.kWorld)
                rot = mTransMtx.rotation()

                # Set transform
                locMObjHandle = createLocator(id, "f", mDagMod)
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
                polyIter.next()
        iter.next()


selList = om2.MGlobal.getActiveSelectionList()
componentIDs, typeID = geIDsAndTypes(selList)
mDagMod = om2.MDagModifier()

if typeID == om2.MFn.kMeshPolygonComponent:
    createLocAtFace(selList, mDagMod)
    print("Done! Face locator/s created and placed!")
else:
    print("Please select an polygon")
