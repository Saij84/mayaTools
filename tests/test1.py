import maya.api.OpenMaya as om2

def createDagNode(nodeType, nodeName, mDagMod):
    """
    Create and rename node
    :param nodeType: string
    :param nodeName: string
    :param mDagMod: MDagModifier
    :return: MObjectHandle
    """
    nodeMObj = mDagMod.createNode(nodeType)
    mDagMod.renameNode(nodeMObj, nodeName)
    mDagMod.doIt()

    nodeMObjHandle = om2.MObjectHandle(nodeMObj)
    return nodeMObjHandle

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


selList = om2.MGlobal.getActiveSelectionList()
dagPath = selList.getDagPath(0)
mObj = selList.getDependNode(0)
nurbsMFn = om2.MFnNurbsCurve()
mDagMod = om2.MDagModifier()

# Create negX matrix
negX = (
    -1, 0, 0, 0,
    0, 1, 0, 0,
    0, 0, 1, 0,
    0, 0, 0, 1
)
negXMtx = om2.MMatrix(negX)

# Create a group node to apply the world matrix and potentially negX matrix
transformMObj = om2.MObject()  # Placeholder for transform MObject as it needs to be accessed later in the script
transformNode = createDagNode("transform", "curveTransform", mDagMod)
if transformNode.isValid():
    transformMObj = transformNode.object()

mObjHandle = om2.MObjectHandle(mObj)
mFn = om2.MFnDependencyNode(mObj)
objName = mFn.name()

# Create and apply translate, rotate and scale
worldMtx = getNodeMatrix(mObjHandle) * negXMtx
mTransMtx = om2.MTransformationMatrix(worldMtx)
scale = mTransMtx.scale(om2.MSpace.kWorld)
rot = mTransMtx.rotation()
trans = mTransMtx.translation(om2.MSpace.kWorld)

shapeNode = dagPath.extendToShape()
shapeMObj = shapeNode.node()
nurbsMFn.copy(shapeMObj)