"""
Author:Fangmin Chen
Version: 0.2

This script will add an locator at a selected vertex aligned(not necessary same orientation) to its normals

USAGE: Select mesh/vertex, run script
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


def createLocAtVertex(selList, componentIDs, mDagMod):
    """
    Create an locator on vertex aligned with the vertex normal
    :param selList: MSelectionList
    :param componentID: int
    :param mDagMod: MDagModifier
    :return: None
    """
    for componentID in componentIDs:
        # Get vertex normal/position
        meshDagPath = selList.getDagPath(0)
        mFnMesh = om2.MFnMesh(meshDagPath)
        vtxNormal = mFnMesh.getVertexNormal(componentID, False, om2.MSpace.kObject)
        vtxPoint = mFnMesh.getPoint(componentID, om2.MSpace.kObject)

        mObj = selList.getDependNode(0)
        mFn = om2.MFnDependencyNode(mObj)
        getMtxPlug = mFn.findPlug("worldMatrix", False)

        mtxPlug = getMtxPlug.elementByLogicalIndex(0)
        plugMObj = mtxPlug.asMObject()

        mFnMtxData = om2.MFnMatrixData(plugMObj)
        offsetMtx = mFnMtxData.matrix()

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


selList = om2.MGlobal.getActiveSelectionList()
componentIDs, typeID = geIDsAndTypes(selList)
mDagMod = om2.MDagModifier()

if typeID == om2.MFn.kMeshVertComponent:
    createLocAtVertex(selList, componentIDs, mDagMod)
    print("Done! Vertex locator/s created and placed!")
else:
    print("Please select a vertex")
