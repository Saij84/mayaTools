"""
Author:Fangmin Chen
Version: 0.1

This script will add an locator at a selected vertex aligned to its normals

USAGE: Select mesh vertex, run script

ToDo: Add functionality to put a locator at the face center aligned to its normal
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


def getNodeMatrix(mObjHandle, searchMatrix="worldMatrix"):
    """
    Search for a matrix plug and return it as a MMatrix
    :param mObjHandle: MObjectHandle
    :param searchMatrix: string
    :return: MMatrix
    """
    if mObjHandle.isValid():
        mObj = mObjHandle.object()
        mFn = om2.MFnDependencyNode(mObj)
        getMtxPlug = mFn.findPlug(searchMatrix, False)

        mtxPlug = getMtxPlug
        if getMtxPlug.isArray():
            mtxPlug = getMtxPlug.elementByLogicalIndex(0)

        mFnMtxData = om2.MFnMatrixData(mtxPlug)
        mMatrixData = mFnMtxData.matrix()

        return mMatrixData


def createLocAtVertex(selList, componentID):
    """
    Create an locator on vertex aligned with the vertex normal
    :param selList: MSelectionList
    :param componentID: int
    :return: None
    """
    # Get vertex normal/position
    meshDagPath = selList.getDagPath(0)
    mFnMesh = om2.MFnMesh(meshDagPath)
    vtxNormal = mFnMesh.getVertexNormal(componentID, False, om2.MSpace.kWorld)
    vtxPoint = mFnMesh.getPoint(componentID, om2.MSpace.kWorld)

    # Get offsetMatrix
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

    vtxMMatrix = om2.MMatrix(mtxConstruct)  # Convert to Maya MMatrix
    newMtx = vtxMMatrix * offsetMtx  # multiply vertex mtx with the offset mtx of geo
    vtxMtransMtx = om2.MTransformationMatrix(newMtx)

    # Get rotation/translation
    rot = vtxMtransMtx.rotation(asQuaternion=False)
    trans = vtxMtransMtx.translation(om2.MSpace.kWorld)

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


selList = om2.MGlobal.getActiveSelectionList()
componentIDs, typeID = geIDsAndTypes(selList)

if typeID == 550:  # kMeshVertComponent
    for componentID in componentIDs:
        loc = createLocator(componentID)
        createLocAtVertex(selList, componentID)
elif typeID == 548:  # kMeshPolygonComponent
    pass
else:
    pass
