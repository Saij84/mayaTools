import maya.api.OpenMaya as om2


def maya_useNewAPI():
    pass


class Vectors2Matrix(om2.MPxNode):
    node_name = 'vectors2Matrix'
    node_id = om2.MTypeId(0x00134b81)
    mtxOut = om2.MObject()

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
        return Vectors2Matrix()

    @staticmethod
    def initialize():
        mtxMFnAttr = om2.MFnMatrixAttribute()
        compoundMFnAttr = om2.MFnCompoundAttribute()
        numericMFnAttr = om2.MFnNumericAttribute()
        numMFnAttr = om2.MFnNumericAttribute()
        mFnNumericData = om2.MFnNumericData()

        Vectors2Matrix.mtxOut = mtxMFnAttr.create('matrixOut', 'mtxOut')
        mtxMFnAttr.readable = True
        Vectors2Matrix.addAttribute(Vectors2Matrix.mtxOut)

        Vectors2Matrix.row0 = compoundMFnAttr.create('row0', 'row0')
        r0XChild = numMFnAttr.create("r0X", "r0X", mFnNumericData.kFloat, 1.0)
        r0YChild = numMFnAttr.create("r0Y", "r0Y", mFnNumericData.kFloat, 0.0)
        r0ZChild = numMFnAttr.create("r0Z", "r0Z", mFnNumericData.kFloat, 0.0)
        mtxMFnAttr.readable = True
        mtxMFnAttr.writable = True
        mtxMFnAttr.storable = True
        compoundMFnAttr.addChild(r0XChild)
        compoundMFnAttr.addChild(r0YChild)
        compoundMFnAttr.addChild(r0ZChild)
        Vectors2Matrix.addAttribute(Vectors2Matrix.row0)

        Vectors2Matrix.row0W = numericMFnAttr.create('row0W', 'row0W', mFnNumericData.kFloat, 0.0)
        mtxMFnAttr.readable = True
        mtxMFnAttr.writable = True
        mtxMFnAttr.storable = True
        Vectors2Matrix.addAttribute(Vectors2Matrix.row0W)

        Vectors2Matrix.row1 = compoundMFnAttr.create('row1', 'row1')
        r1xChild = numMFnAttr.create("r1X", "r1X", mFnNumericData.kFloat, 0.0)
        r1yChild = numMFnAttr.create("r1Y", "r1Y", mFnNumericData.kFloat, 1.0)
        r1zChild = numMFnAttr.create("r1Z", "r1Z", mFnNumericData.kFloat, 0.0)
        mtxMFnAttr.readable = True
        mtxMFnAttr.writable = True
        mtxMFnAttr.storable = True
        compoundMFnAttr.addChild(r1xChild)
        compoundMFnAttr.addChild(r1yChild)
        compoundMFnAttr.addChild(r1zChild)
        Vectors2Matrix.addAttribute(Vectors2Matrix.row1)

        Vectors2Matrix.row1W = numericMFnAttr.create('row1W', 'row1W', mFnNumericData.kFloat, 0.0)
        mtxMFnAttr.readable = True
        mtxMFnAttr.writable = True
        mtxMFnAttr.storable = True
        Vectors2Matrix.addAttribute(Vectors2Matrix.row1W)

        Vectors2Matrix.row2 = compoundMFnAttr.create('row2', 'row2')
        r2xChild = numMFnAttr.create("r2X", "r2X", mFnNumericData.kFloat, 0.0)
        r2yChild = numMFnAttr.create("r2Y", "r2Y", mFnNumericData.kFloat, 0.0)
        r2zChild = numMFnAttr.create("r2Z", "r2Z", mFnNumericData.kFloat, 1.0)
        mtxMFnAttr.readable = True
        mtxMFnAttr.writable = True
        mtxMFnAttr.storable = True
        compoundMFnAttr.addChild(r2xChild)
        compoundMFnAttr.addChild(r2yChild)
        compoundMFnAttr.addChild(r2zChild)
        Vectors2Matrix.addAttribute(Vectors2Matrix.row2)

        Vectors2Matrix.row2W = numericMFnAttr.create('row2W', 'row2W', mFnNumericData.kFloat, 0.0)
        mtxMFnAttr.readable = True
        mtxMFnAttr.writable = True
        mtxMFnAttr.storable = True
        Vectors2Matrix.addAttribute(Vectors2Matrix.row2W)

        Vectors2Matrix.row3 = compoundMFnAttr.create('row3', 'row3')
        r3xChild = numMFnAttr.create("r3X", "r3X", mFnNumericData.kFloat, 0.0)
        r3yChild = numMFnAttr.create("r3Y", "r3Y", mFnNumericData.kFloat, 0.0)
        r3zChild = numMFnAttr.create("r3Z", "r3Z", mFnNumericData.kFloat, 0.0)
        mtxMFnAttr.readable = True
        mtxMFnAttr.writable = True
        mtxMFnAttr.storable = True
        compoundMFnAttr.addChild(r3xChild)
        compoundMFnAttr.addChild(r3yChild)
        compoundMFnAttr.addChild(r3zChild)
        Vectors2Matrix.addAttribute(Vectors2Matrix.row3)

        Vectors2Matrix.row3W = numericMFnAttr.create('row3W', 'row3W', mFnNumericData.kFloat, 1.0)
        mtxMFnAttr.readable = True
        mtxMFnAttr.writable = True
        mtxMFnAttr.storable = True
        Vectors2Matrix.addAttribute(Vectors2Matrix.row3W)

        Vectors2Matrix.attributeAffects(Vectors2Matrix.row0, Vectors2Matrix.mtxOut)
        Vectors2Matrix.attributeAffects(Vectors2Matrix.row0W, Vectors2Matrix.mtxOut)

        Vectors2Matrix.attributeAffects(Vectors2Matrix.row1, Vectors2Matrix.mtxOut)
        Vectors2Matrix.attributeAffects(Vectors2Matrix.row1W, Vectors2Matrix.mtxOut)

        Vectors2Matrix.attributeAffects(Vectors2Matrix.row2, Vectors2Matrix.mtxOut)
        Vectors2Matrix.attributeAffects(Vectors2Matrix.row2W, Vectors2Matrix.mtxOut)

        Vectors2Matrix.attributeAffects(Vectors2Matrix.row3, Vectors2Matrix.mtxOut)
        Vectors2Matrix.attributeAffects(Vectors2Matrix.row3W, Vectors2Matrix.mtxOut)

    def compute(self, plug, data):
        mtxInDataHandle = data.outputValue(Vectors2Matrix.mtxOut)

        row0DataHandle = data.inputValue(Vectors2Matrix.row0).asFloat3()
        row0WDataHandle = data.inputValue(Vectors2Matrix.row0W).asFloat()

        row1DataHandle = data.inputValue(Vectors2Matrix.row1).asFloat3()
        row1WDataHandle = data.inputValue(Vectors2Matrix.row1W).asFloat()

        row2DataHandle = data.inputValue(Vectors2Matrix.row2).asFloat3()
        row2WDataHandle = data.inputValue(Vectors2Matrix.row2W).asFloat()

        row3DataHandle = data.inputValue(Vectors2Matrix.row3).asFloat3()
        row3WDataHandle = data.inputValue(Vectors2Matrix.row3W).asFloat()

        mtxConstruct = [
            row0DataHandle[0], row0DataHandle[1], row0DataHandle[2], row0WDataHandle,
            row1DataHandle[0], row1DataHandle[1], row1DataHandle[2], row1WDataHandle,
            row2DataHandle[0], row2DataHandle[1], row2DataHandle[2], row2WDataHandle,
            row3DataHandle[0], row3DataHandle[1], row3DataHandle[2], row3WDataHandle
        ]
        mtx = om2.MMatrix(mtxConstruct)
        mtxInDataHandle.setMMatrix(mtx)

        data.setClean(plug)


def initializePlugin(obj):
    fnPlugin = om2.MFnPlugin(obj, 'Fangmin Chen', '1.0')
    fnPlugin.registerNode(Vectors2Matrix.node_name, Vectors2Matrix.node_id,
                           Vectors2Matrix.creator, Vectors2Matrix.initialize)


def uninitializePlugin(obj):
    fnPlugin = om2.MFnPlugin(obj)
    fnPlugin.deregisterNode(Vectors2Matrix.node_id)
