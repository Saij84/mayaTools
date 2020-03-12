import maya.api.OpenMaya as om2


def maya_useNewAPI():
    pass


class Matrix2Vectors(om2.MPxNode):
    nodeName = 'matrixVisualizer'
    nodeID = om2.MTypeId(0x83123)
    mtxIn = om2.MObject()
    row0 = om2.MObject()
    row1 = om2.MObject()
    row2 = om2.MObject()
    row3 = om2.MObject()

    def __init__(self):
        om2.MPxNode.__init__(self)

    @staticmethod
    def creator():
        return Matrix2Vectors()

    @staticmethod
    def initialize():
        mtxMFnAttr = om2.MFnMatrixAttribute()
        compoundMFnAttr = om2.MFnCompoundAttribute()
        numMFnAttr = om2.MFnNumericAttribute()
        mFnNumericData = om2.MFnNumericData()

        Matrix2Vectors.mtxIn = mtxMFnAttr.create('matrixIn', 'mtxIn')
        mtxMFnAttr.readable = True
        mtxMFnAttr.writable = True
        mtxMFnAttr.storable = True
        Matrix2Vectors.addAttribute(Matrix2Vectors.mtxIn)

        Matrix2Vectors.row0 = mtxMFnAttr.create('row0Mtx', 'row0Mtx')
        mtxMFnAttr.readable = True
        Matrix2Vectors.addAttribute(Matrix2Vectors.row0)

        Matrix2Vectors.row1 = mtxMFnAttr.create('row1Mtx', 'row1Mtx')
        mtxMFnAttr.readable = True
        Matrix2Vectors.addAttribute(Matrix2Vectors.row1)

        Matrix2Vectors.row2 = mtxMFnAttr.create('row2Mtx', 'row2Mtx')
        mtxMFnAttr.readable = True
        Matrix2Vectors.addAttribute(Matrix2Vectors.row2)

        Matrix2Vectors.row3 = mtxMFnAttr.create('row3Mtx', 'row3Mtx')
        mtxMFnAttr.readable = True
        Matrix2Vectors.addAttribute(Matrix2Vectors.row2)


        Matrix2Vectors.attributeAffects(Matrix2Vectors.mtxIn, Matrix2Vectors.row0)
        Matrix2Vectors.attributeAffects(Matrix2Vectors.mtxIn, Matrix2Vectors.row1)
        Matrix2Vectors.attributeAffects(Matrix2Vectors.mtxIn, Matrix2Vectors.row2)
        Matrix2Vectors.attributeAffects(Matrix2Vectors.mtxIn, Matrix2Vectors.row3)

    def compute(self, plug, data):
        mtxInDataHandle = data.inputValue(Matrix2Vectors.mtxIn)
        row0DataHandle = data.outputValue(Matrix2Vectors.row0)
        row1DataHandle = data.outputValue(Matrix2Vectors.row1)
        row2DataHandle = data.outputValue(Matrix2Vectors.row2)
        row3DataHandle = data.outputValue(Matrix2Vectors.row3)

        mtxIn = mtxInDataHandle.asMatrix()
        row0 = [mtxIn.getElement(0, idx) for idx in range(4)]
        row1 = [mtxIn.getElement(1, idx) for idx in range(4)]
        row2 = [mtxIn.getElement(2, idx) for idx in range(4)]
        row3 = [mtxIn.getElement(3, idx) for idx in range(4)]


        for row in [row0, row1, row2, row3]:
            mtx = [
                1, 0, 0, 0,
                0, 1, 0, 0,
                0, 0, 1, 0,
                row[0], row[1], row[2], row[3]
            ]

            rowMtx = om2.MMatrix(mtx)
            transformMatrix = mtxIn * rowMtx


            row0DataHandle.setMatrix(transformMatrix)

        data.setClean(plug)


def initializePlugin(obj):
    fn_plugin = om2.MFnPlugin(obj, 'Fangmin Chen', '1.0')
    fn_plugin.registerNode(Matrix2Vectors.nodeName, Matrix2Vectors.nodeID,
                           Matrix2Vectors.creator, Matrix2Vectors.initialize)


def uninitializePlugin(obj):
    fn_plugin = om2.MFnPlugin(obj)
    fn_plugin.deregisterNode(Matrix2Vectors.nodeID)
