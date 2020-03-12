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


def getNodeMatrix(mObjHandle, searchString="worldMatrix"):
    """
    Search for a matrix plug and return it as a MMatrix
    :param mObjHandle: MObjectHandle
    :param searchString: string
    :return: MMatrix
    """
    if mObjHandle.isValid():
        mObj = mObjHandle.object()
        mFn = om2.MFnDependencyNode(mObj)
        getMtxPlug = mFn.findPlug(searchString, False)

        # Handle array plugs
        mtxPlug = getMtxPlug
        if getMtxPlug.isArray:
            mtxPlug = getMtxPlug.elementByLogicalIndex(0)
        plugMObj = mtxPlug.asMObject()

        mFnMtxData = om2.MFnMatrixData(plugMObj)
        mMatrixData = mFnMtxData.matrix()

        return mMatrixData


def createLocator(name, selType, mDagMod):
    """
    create a locator with vertexID in the name
    :param componentID: str/int
    :param selType: str
    :param mDagMod: MDagModifier
    :return: MObjectHandle
    """
    locLocalScale = 0.2
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
    vtxPoint = mFnMesh.getPoint(componentID, om2.MSpace.kObject)

    mObj = selList.getDependNode(0)
    mObjHandle = om2.MObjectHandle(mObj)
    offsetMtx = getNodeMatrix(mObjHandle)

    # Construct a matrix
    mtxConstruct = (
        vtxNormal.x, vtxNormal.y, vtxNormal.z, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        vtxPoint.x, vtxPoint.y, vtxPoint.z, vtxPoint.w
    )

    vtxMMatrix = om2.MMatrix(mtxConstruct) * offsetMtx  # Convert to Maya MMatrix
    vtxMtransMtx = om2.MTransformationMatrix(vtxMMatrix)

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
    print("Done! Vertex locator/s created and placed!")


def createLocAtFace(selList, mDagMod):
    """
    Method to create a locator at face center and align it to it's normal
    :param selList: MSelsctionList
    :param mDagMod: MDagModifier
    :return: None
    """
    iter = om2.MItSelectionList(selList, om2.MFn.kMeshPolygonComponent)
    mObj = selList.getDependNode(0)
    mObjHandle = om2.MObjectHandle(mObj)
    offsetMtx = getNodeMatrix(mObjHandle)

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

                # Cross vectors NOTE: vectors2 is negative ti make X axis aiming "out"
                normalVector = vector1 ^ -vector2

                mtx = (
                    normalVector.x, normalVector.y, normalVector.z, 0,
                    p2MidVector.x, p2MidVector.y, p2MidVector.z, 0,
                    p1MidVector.x, p1MidVector.y, p1MidVector.z, 0,
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

    print("Done! Face locator/s created and placed!")


selList = om2.MGlobal.getActiveSelectionList()
componentIDs, typeID = geIDsAndTypes(selList)
mDagMod = om2.MDagModifier()

if typeID == om2.MFn.kMeshVertComponent:
    for componentID in componentIDs:
        createLocAtVertex(selList, componentID, mDagMod)
elif typeID == om2.MFn.kMeshPolygonComponent:
    createLocAtFace(selList, mDagMod)
else:
    print("Please select an polygon")
