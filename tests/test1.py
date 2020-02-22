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
        norm = om2.MFnMesh(dag)
        pNormal = norm.getPolygonNormal(componentID)

        mFn = om2.MFnDependencyNode(dag)
        wMtx = mFn.findPlug("worldMatrix", False)
        mtxPlug = wMtx.elementByLogicalIndex(0)

        wMmtx = om2.MMatrix(mtxPlug)
        print(wMtx)

        polyIter = om2.MItMeshPolygon(dag, mObj)
        while not polyIter.isDone():
            polygonCenterMPoint = polyIter.center(om2.MSpace.kWorld)
            polygonNormalCenter.append((pNormal, polygonCenterMPoint))
            polyIter.next(0)
        iter.next()

    return polygonNormalCenter

def createLocator(componentID):
    """
    create a locator with vertexID in the name
    :param componentID: int
    :return: MObjectHandle
    """
    mDagMod = om2.MDagModifier()
    loc = mDagMod.createNode("locator")
    newName = "LOC_{}".format(componentID)
    mDagMod.renameNode(loc, newName)
    mDagMod.doIt()

    locMObjHandle = om2.MObjectHandle(loc)
    return locMObjHandle

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
    loc = createLocator(componentIDs[0])
    createLocAtFace(componentIDs[0], selList)

else:
    pass
