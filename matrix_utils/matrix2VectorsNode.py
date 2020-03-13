import maya.api.OpenMaya as om2


def maya_useNewAPI():
    pass


class Matrix2Vectors(om2.MPxNode):
    node_name = 'matrix2Vectors'
    node_id = om2.MTypeId(0x00134b80)
    mtxIn = om2.MObject()

    row0 = om2.MObject()
    row0W = om2.MObject()

    row1 = om2.MObject()
    row1W = om2.MObject()

    row2 = om2.MObject()
    row2W = om2.MObject()

    row3 = om2.MObject()
    row3W = om2.MObject()

    def __init__(self):
        om2.MPxNode.__init__(self)

    @staticmethod
    def creator():
        return Matrix2Vectors()

    @staticmethod
    def initialize():
        mtxMFnAttr = om2.MFnMatrixAttribute()
        compoundMFnAttr = om2.MFnCompoundAttribute()
        numericMFnAttr = om2.MFnNumericAttribute()
        numMFnAttr = om2.MFnNumericAttribute()
        mFnNumericData = om2.MFnNumericData()

        Matrix2Vectors.mtxIn = mtxMFnAttr.create('matrixIn', 'mtxIn')
        mtxMFnAttr.readable = True
        mtxMFnAttr.writable = True
        mtxMFnAttr.storable = True
        Matrix2Vectors.addAttribute(Matrix2Vectors.mtxIn)

        Matrix2Vectors.row0 = compoundMFnAttr.create('row0', 'row0')
        r0XChild = numMFnAttr.create("r0X", "r0X", mFnNumericData.kFloat)
        r0YChild = numMFnAttr.create("r0Y", "r0Y", mFnNumericData.kFloat)
        r0ZChild = numMFnAttr.create("r0Z", "r0Z", mFnNumericData.kFloat)
        compoundMFnAttr.readable = True
        compoundMFnAttr.addChild(r0XChild)
        compoundMFnAttr.addChild(r0YChild)
        compoundMFnAttr.addChild(r0ZChild)
        Matrix2Vectors.addAttribute(Matrix2Vectors.row0)

        Matrix2Vectors.row0W = numericMFnAttr.create('row0W', 'row0W', mFnNumericData.kFloat, 0.0)
        compoundMFnAttr.readable = True
        Matrix2Vectors.addAttribute(Matrix2Vectors.row0W)

        Matrix2Vectors.row1 = compoundMFnAttr.create('row1', 'row1')
        r1xChild = numMFnAttr.create("r1X", "r1X", mFnNumericData.kFloat)
        r1yChild = numMFnAttr.create("r1Y", "r1Y", mFnNumericData.kFloat)
        r1zChild = numMFnAttr.create("r1Z", "r1Z", mFnNumericData.kFloat)
        compoundMFnAttr.readable = True
        compoundMFnAttr.addChild(r1xChild)
        compoundMFnAttr.addChild(r1yChild)
        compoundMFnAttr.addChild(r1zChild)
        Matrix2Vectors.addAttribute(Matrix2Vectors.row1)

        Matrix2Vectors.row1W = numericMFnAttr.create('row1W', 'row1W', mFnNumericData.kFloat, 0.0)
        compoundMFnAttr.readable = True
        Matrix2Vectors.addAttribute(Matrix2Vectors.row1W)

        Matrix2Vectors.row2 = compoundMFnAttr.create('row2', 'row2')
        r2xChild = numMFnAttr.create("r2X", "r2X", mFnNumericData.kFloat)
        r2yChild = numMFnAttr.create("r2Y", "r2Y", mFnNumericData.kFloat)
        r2zChild = numMFnAttr.create("r2Z", "r2Z", mFnNumericData.kFloat)
        compoundMFnAttr.readable = True
        compoundMFnAttr.addChild(r2xChild)
        compoundMFnAttr.addChild(r2yChild)
        compoundMFnAttr.addChild(r2zChild)
        Matrix2Vectors.addAttribute(Matrix2Vectors.row2)

        Matrix2Vectors.row2W = numericMFnAttr.create('row2W', 'row2W', mFnNumericData.kFloat, 0.0)
        compoundMFnAttr.readable = True
        Matrix2Vectors.addAttribute(Matrix2Vectors.row2W)

        Matrix2Vectors.row3 = compoundMFnAttr.create('row3', 'row3')
        r3xChild = numMFnAttr.create("r3X", "r3X", mFnNumericData.kFloat)
        r3yChild = numMFnAttr.create("r3Y", "r3Y", mFnNumericData.kFloat)
        r3zChild = numMFnAttr.create("r3Z", "r3Z", mFnNumericData.kFloat)
        compoundMFnAttr.readable = True
        compoundMFnAttr.addChild(r3xChild)
        compoundMFnAttr.addChild(r3yChild)
        compoundMFnAttr.addChild(r3zChild)
        Matrix2Vectors.addAttribute(Matrix2Vectors.row3)

        Matrix2Vectors.row3W = numericMFnAttr.create('row3W', 'row3W', mFnNumericData.kFloat, 0.0)
        compoundMFnAttr.readable = True
        Matrix2Vectors.addAttribute(Matrix2Vectors.row3W)

        Matrix2Vectors.attributeAffects(Matrix2Vectors.mtxIn, Matrix2Vectors.row0)
        Matrix2Vectors.attributeAffects(Matrix2Vectors.mtxIn, Matrix2Vectors.row0W)

        Matrix2Vectors.attributeAffects(Matrix2Vectors.mtxIn, Matrix2Vectors.row1)
        Matrix2Vectors.attributeAffects(Matrix2Vectors.mtxIn, Matrix2Vectors.row1W)

        Matrix2Vectors.attributeAffects(Matrix2Vectors.mtxIn, Matrix2Vectors.row2)
        Matrix2Vectors.attributeAffects(Matrix2Vectors.mtxIn, Matrix2Vectors.row2W)

        Matrix2Vectors.attributeAffects(Matrix2Vectors.mtxIn, Matrix2Vectors.row3)
        Matrix2Vectors.attributeAffects(Matrix2Vectors.mtxIn, Matrix2Vectors.row3W)

    def compute(self, plug, data):
        mtxInDataHandle = data.inputValue(Matrix2Vectors.mtxIn)

        row0DataHandle = data.outputValue(Matrix2Vectors.row0)
        row0WDataHandle = data.outputValue(Matrix2Vectors.row0W)

        row1DataHandle = data.outputValue(Matrix2Vectors.row1)
        row1WDataHandle = data.outputValue(Matrix2Vectors.row1W)

        row2DataHandle = data.outputValue(Matrix2Vectors.row2)
        row2WDataHandle = data.outputValue(Matrix2Vectors.row2W)

        row3DataHandle = data.outputValue(Matrix2Vectors.row3)
        row3WDataHandle = data.outputValue(Matrix2Vectors.row3W)

        mtxIn = mtxInDataHandle.asMatrix()

        row0DataHandle.set3Float(mtxIn[0], mtxIn[1], mtxIn[2])
        row0WDataHandle.setFloat(mtxIn[3])

        row1DataHandle.set3Float(mtxIn[4], mtxIn[5], mtxIn[6])
        row1WDataHandle.setFloat(mtxIn[7])

        row2DataHandle.set3Float(mtxIn[8], mtxIn[9], mtxIn[10])
        row2WDataHandle.setFloat(mtxIn[11])

        row3DataHandle.set3Float(mtxIn[12], mtxIn[13], mtxIn[14])
        row3WDataHandle.setFloat(mtxIn[15])

        data.setClean(plug)


def initializePlugin(obj):
    fn_plugin = om2.MFnPlugin(obj, 'Fangmin Chen', '1.0')
    fn_plugin.registerNode(Matrix2Vectors.node_name, Matrix2Vectors.node_id,
                           Matrix2Vectors.creator, Matrix2Vectors.initialize)


def uninitializePlugin(obj):
    fn_plugin = om2.MFnPlugin(obj)
    fn_plugin.deregisterNode(Matrix2Vectors.node_id)
