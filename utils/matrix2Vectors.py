import maya.api.OpenMaya as om2

def maya_useNewAPI():
    pass


class Matrix2Vectors(om2.MPxNode):
    node_name = 'matrix2Vectors'
    node_id = om2.MTypeId(0x83123)
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

        Matrix2Vectors.row0 = compoundMFnAttr.create('row0', 'row0')
        r0xChild = numMFnAttr.create("r0x", "r0x", mFnNumericData.kFloat)
        r0yChild = numMFnAttr.create("r0y", "r0y", mFnNumericData.kFloat)
        r0zChild = numMFnAttr.create("r0z", "r0z", mFnNumericData.kFloat)
        compoundMFnAttr.addChild(r0xChild)
        compoundMFnAttr.addChild(r0yChild)
        compoundMFnAttr.addChild(r0zChild)
        compoundMFnAttr.readable = True
        Matrix2Vectors.addAttribute(Matrix2Vectors.row0)

        Matrix2Vectors.row1 = compoundMFnAttr.create('row1', 'row1')
        r1xChild = numMFnAttr.create("r1x", "r1x", mFnNumericData.kFloat)
        r1yChild = numMFnAttr.create("r1y", "r1y", mFnNumericData.kFloat)
        r1zChild = numMFnAttr.create("r1z", "r1z", mFnNumericData.kFloat)
        compoundMFnAttr.addChild(r1xChild)
        compoundMFnAttr.addChild(r1yChild)
        compoundMFnAttr.addChild(r1zChild)
        compoundMFnAttr.readable = True
        Matrix2Vectors.addAttribute(Matrix2Vectors.row1)

        Matrix2Vectors.row2 = compoundMFnAttr.create('row2', 'row2')
        r2xChild = numMFnAttr.create("r2x", "r2x", mFnNumericData.kFloat)
        r2yChild = numMFnAttr.create("r2y", "r2y", mFnNumericData.kFloat)
        r2zChild = numMFnAttr.create("r2z", "r2z", mFnNumericData.kFloat)
        compoundMFnAttr.addChild(r2xChild)
        compoundMFnAttr.addChild(r2yChild)
        compoundMFnAttr.addChild(r2zChild)
        compoundMFnAttr.readable = True
        Matrix2Vectors.addAttribute(Matrix2Vectors.row2)

        Matrix2Vectors.row3 = compoundMFnAttr.create('row3', 'row3')
        r3xChild = numMFnAttr.create("r3x", "r3x", mFnNumericData.kFloat)
        r3yChild = numMFnAttr.create("r3y", "r3y", mFnNumericData.kFloat)
        r3zChild = numMFnAttr.create("r3z", "r3z", mFnNumericData.kFloat)
        compoundMFnAttr.addChild(r3xChild)
        compoundMFnAttr.addChild(r3yChild)
        compoundMFnAttr.addChild(r3zChild)
        compoundMFnAttr.readable = True
        Matrix2Vectors.addAttribute(Matrix2Vectors.row3)

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
        
        row0DataHandle.set3Float(row0[0], row0[1], row0[2])
        row1DataHandle.set3Float(row1[0], row1[1], row1[2])
        row2DataHandle.set3Float(row2[0], row2[1], row2[2])
        row3DataHandle.set3Float(row3[0], row3[1], row3[2])
        
        data.setClean(plug)



def initializePlugin(obj):
    fn_plugin = om2.MFnPlugin(obj, 'Fangmin Chen', '1.0')
    fn_plugin.registerNode(Matrix2Vectors.node_name, Matrix2Vectors.node_id,
                           Matrix2Vectors.creator, Matrix2Vectors.initialize)


def uninitializePlugin(obj):
    fn_plugin = om2.MFnPlugin(obj)
    fn_plugin.deregisterNode(Matrix2Vectors.node_id)
