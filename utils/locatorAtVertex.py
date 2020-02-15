import maya.api.OpenMaya as om2

selList = om2.MGlobal.getActiveSelectionList()
mObjs = [selList.getDependNode(idx) for idx in range(selList.length())]

def getVtxIDs(selList):
    __, vtxs = selList.getComponent(0)
    vtxList = om2.MFnSingleIndexedComponent(vtxs)
    vtxIdxList = vtxList.getElements()
    return vtxIdxList

def createLocator(vtxID):
    mDagMod = om2.MDagModifier()
    loc = mDagMod.createNode("locator")
    mDagMod.renameNode(loc, "{}_LOC".format(vtxID))
    mDagMod.doIt()

    locMObjHandle = om2.MObjectHandle(loc)
    return locMObjHandle

vtxIDs = getVtxIDs(selList)

for vtxID in vtxIDs:
    loc = createLocator(vtxID)
    mFnMesh = om2.MFnMesh(mObjs[0])
    vtxNormal = mFnMesh.getVertexNormal(vtxID, False, om2.MSpace.kObject)
    vtxPoint = mFnMesh.getPoint(vtxID)

    mtxConstruct = (
        vtxNormal[0], vtxNormal[1], vtxNormal[2], 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        vtxPoint[0], vtxPoint[1], vtxPoint[2], vtxPoint[3]
    )
    vtxMMatrix = om2.MMatrix(mtxConstruct)
    vtxMtransMtx = om2.MTransformationMatrix(vtxMMatrix)

    rot = vtxMtransMtx.rotation(asQuaternion=False)
    trans =vtxMtransMtx.translation(om2.MSpace.kWorld)

    if loc.isValid():
        locMObj = loc.object()
        mFn = om2.MFnDependencyNode(locMObj)

        transX = mFn.findPlug("translateX", False)
        transY = mFn.findPlug("translateY", False)
        transZ = mFn.findPlug("translateZ", False)

        transX.setFloat(trans[0])
        transY.setFloat(trans[1])
        transZ.setFloat(trans[2])

        rotX = mFn.findPlug("rotateX", False)
        rotY = mFn.findPlug("rotateY", False)
        rotZ = mFn.findPlug("rotateZ", False)

        rotX.setFloat(rot[0])
        rotY.setFloat(rot[1])
        rotZ.setFloat(rot[2])
