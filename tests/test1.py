"""
Author:Fangmin Chen
Version: 0.1

This script will add an locator at a selected vertex aligned to its normals

USAGE: Select mesh vertex, run script

ToDo: Add functionality to put a locator at the face center aligned to its normal
"""
import collections as coll
import maya.api.OpenMaya as om2


def geIDs(selList):
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

def getPolygonCenter(selList, componentID):
    """
    Method to iter through an selection list components and return center of an polygon
    :param selList: MSelectionList
    :return: list
    """
    iter = om2.MItSelectionList(selList, om2.MFn.kMeshPolygonComponent)

    polygonNormalCenter = list()

    while not iter.isDone():
        dag, mObj = selList.getComponent(0)
        selMObj = selList.getDependNode(0)
        norm = om2.MFnMesh(dag)
        pNormal = norm.getPolygonNormal(componentID)

        mFn = om2.MFnDependencyNode(selMObj)
        wMtx = mFn.findPlug("worldMatrix", False)
        mtxPlug = wMtx.elementByLogicalIndex(0)
        mtxMObj = mtxPlug.asMObject()

        mtxMFn = om2.MFnMatrixData(mtxMObj)
        mtx = mtxMFn.matrix()

        polyIter = om2.MItMeshPolygon(dag, mObj)
        while not polyIter.isDone():

            triMPointList, triVtxID = polyIter.getTriangle(0)

            point0 = triMPointList[0]
            point1 = triMPointList[1]
            point2 = triMPointList[2]

            polygonCenterMPoint = polyIter.center(om2.MSpace.kWorld)
            centerVector = om2.MVector(polygonCenterMPoint.x, polygonCenterMPoint.y, polygonCenterMPoint.z)

            p1Vector = om2.MVector(point0.x, point0.y, point0.z)
            p2Vector = om2.MVector(point1.x, point1.y, point1.z)
            p3Vector = om2.MVector(point2.x, point2.y, point2.z)

            vector0 = point1 - point0
            vector1 = point2 - point1

            normalVector = vector0 ^ vector1

            createLocator("center", centerVector)
            createLocator("p1", p1Vector)
            createLocator("p2", p2Vector)
            createLocator("p3", p3Vector)
            createLocator("vector0", vector0)
            createLocator("vector1", vector1)
            createLocator("normal", normalVector)


            polygonNormalCenter.append((pNormal, polygonCenterMPoint))
            polyIter.next(0)
        iter.next()

    return polygonNormalCenter

def createLocator(name, locVector):
    """
    create a locator with vertexID in the name
    :param componentID: int
    :return: MObjectHandle
    """
    locLocalScale = 0.1
    mDagMod = om2.MDagModifier()
    mDagPath = om2.MDagPath()
    loc = mDagMod.createNode("locator")
    locMFn = om2.MFnDependencyNode(loc)
    newName = "LOC_{}".format(name)
    mDagMod.renameNode(loc, newName)
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

    transX = locMFn.findPlug("translateX", False)
    transY = locMFn.findPlug("translateY", False)
    transZ = locMFn.findPlug("translateZ", False)
    transX.setFloat(locVector.x)
    transY.setFloat(locVector.y)
    transZ.setFloat(locVector.z)


def createLocAtFace(componentID, selList):
    polygonCenters = getPolygonCenter(selList, componentID)

    for normal, center in polygonCenters:
        mtxConstruct = (
            normal[0], normal[1], normal[2], 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            center[0], center[1], center[2], center[3]
        )
        polygonMMatrix = om2.MMatrix(mtxConstruct)  # Convert to Maya MMatrix
        polygonMtransMtx = om2.MTransformationMatrix(polygonMMatrix)

        # Get rotation/translation
        rot = polygonMtransMtx.rotation(asQuaternion=False)
        trans = polygonMtransMtx.translation(om2.MSpace.kWorld)


        # if loc.isValid():
        #     locMObj = loc.object()
        #     mFn = om2.MFnDependencyNode(locMObj)
        #
        #     transX = mFn.findPlug("translateX", False)
        #     transY = mFn.findPlug("translateY", False)
        #     transZ = mFn.findPlug("translateZ", False)
        #
        #     transX.setFloat(translate.X)
        #     transY.setFloat(translate.Y)
        #     transZ.setFloat(translate.Z)
        #
        #     rotX = mFn.findPlug("rotateX", False)
        #     rotY = mFn.findPlug("rotateY", False)
        #     rotZ = mFn.findPlug("rotateZ", False)
        #
        #     rotX.setFloat(rotate.X)
        #     rotY.setFloat(rotate.Y)
        #     rotZ.setFloat(rotate.Z)

def createLocAtVertex(componentID):
    # Get vertex normal/position
    meshDagPath = selList.getDagPath(0)
    mFnMesh = om2.MFnMesh(meshDagPath)
    vtxNormal = mFnMesh.getVertexNormal(componentID, False, om2.MSpace.kObject)
    vtxPoint = mFnMesh.getPoint(componentID)

    # Construct a matrix
    mtxConstruct = (
        vtxNormal[0], vtxNormal[1], vtxNormal[2], 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        vtxPoint[0], vtxPoint[1], vtxPoint[2], vtxPoint[3]
    )

    vtxMMatrix = om2.MMatrix(mtxConstruct)  # Convert to Maya MMatrix
    vtxMtransMtx = om2.MTransformationMatrix(vtxMMatrix)

    # Get rotation/translation
    rot = vtxMtransMtx.rotation(asQuaternion=False)
    trans = vtxMtransMtx.translation(om2.MSpace.kWorld)
    axisData = coll.namedtuple("axis", ["X", "Y", "Z"])
    translate = axisData(trans[0], trans[1], trans[2])
    rotate = axisData(rot[0], rot[1], rot[2])

    if loc.isValid():
        locMObj = loc.object()
        mFn = om2.MFnDependencyNode(locMObj)

        transX = mFn.findPlug("translateX", False)
        transY = mFn.findPlug("translateY", False)
        transZ = mFn.findPlug("translateZ", False)

        transX.setFloat(translate.X)
        transY.setFloat(translate.Y)
        transZ.setFloat(translate.Z)

        rotX = mFn.findPlug("rotateX", False)
        rotY = mFn.findPlug("rotateY", False)
        rotZ = mFn.findPlug("rotateZ", False)

        rotX.setFloat(rotate.X)
        rotY.setFloat(rotate.Y)
        rotZ.setFloat(rotate.Z)


selList = om2.MGlobal.getActiveSelectionList()
componentIDs, typeID = geIDs(selList)


if typeID == 550:  # kMeshVertComponent
    for componentID in componentIDs:
        loc = createLocator(id)
        createLocAtVertex(id)
elif typeID == 548:  # kMeshPolygonComponent
    createLocAtFace(componentIDs[0], selList)

else:
    pass
