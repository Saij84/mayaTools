"""
Author:Fangmin Chen
Version: 0.1

This script will add an locator at a selected vertex aligned to its normals

USAGE: Select mesh vertex, run script

ToDo: Add functionality to put a locator at the face center aligned to its normal
"""
import collections as coll
import maya.api.OpenMaya as om2


def getVtxIDs(selList):
    """
    Get selected vertexID/s
    :param selList: MSelectionList
    :return: list of int
    """
    __, vtxs = selList.getComponent(0)
    vtxList = om2.MFnSingleIndexedComponent(vtxs)
    vtxIdxList = vtxList.getElements()
    selType = vtxs.apiType()

    return vtxIdxList, selType


def createLocator(vtxID):
    """
    create a locator with vertexID in the name
    :param vtxID: int
    :return: MObjectHandle
    """
    mDagMod = om2.MDagModifier()
    loc = mDagMod.createNode("locator")
    newName = "LOC_{}".format(vtxID)
    mDagMod.renameNode(loc, newName)
    mDagMod.doIt()

    locMObjHandle = om2.MObjectHandle(loc)
    return locMObjHandle


def createLocAtVertex():
    # Get vertex normal/position
    meshMObj = selList.getDependNode(0)
    mFnMesh = om2.MFnMesh(meshMObj)
    vtxNormal = mFnMesh.getVertexNormal(vtxID, False, om2.MSpace.kObject)
    vtxPoint = mFnMesh.getPoint(vtxID)

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
vtxIDs, typeID = getVtxIDs(selList)

for vtxID in vtxIDs:
    loc = createLocator(vtxID)
    if typeID == 550:  # kMeshVertComponent
        createLocAtVertex()
    elif typeID == 548:  # kMeshPolygonComponent
        pass
    else:
        pass
