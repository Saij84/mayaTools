import maya.api.OpenMaya as om2
import math


def maya_useNewAPI():
    pass


class Matrix2Vectors(om2.MPxNode):
    node_name = 'matrix2Vectors'
    node_id = om2.MTypeId(0x83112)
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

        Matrix2Vectors.mtxIn = mtxMFnAttr.create('matrixIn', 'mtxIn', om2.MFnNumericData.kFloat)
        mtxMFnAttr.readable = True
        mtxMFnAttr.writable = True
        mtxMFnAttr.storable = True
        Matrix2Vectors.addAttribute(Matrix2Vectors.mtxIn)

        Matrix2Vectors.row0 = compoundMFnAttr.create('row0', 'row0')
        r0xChild = numMFnAttr.create("r0x", "r0x", om2.MFnNumericData.kFloat)
        r0yChild = numMFnAttr.create("r0y", "r0y", om2.MFnNumericData.kFloat)
        r0zChild = numMFnAttr.create("r0z", "r0z", om2.MFnNumericData.kFloat)
        compoundMFnAttr.addChild(r0xChild)
        compoundMFnAttr.addChild(r0yChild)
        compoundMFnAttr.addChild(r0zChild)
        compoundMFnAttr.readable = True
        Matrix2Vectors.addAttribute(Matrix2Vectors.row0)

        Matrix2Vectors.row1 = compoundMFnAttr.create('row1', 'row1')
        r1xChild = numMFnAttr.create("r1x", "r1x", om2.MFnNumericData.kFloat)
        r1yChild = numMFnAttr.create("r1y", "r1y", om2.MFnNumericData.kFloat)
        r1zChild = numMFnAttr.create("r1z", "r1z", om2.MFnNumericData.kFloat)
        compoundMFnAttr.addChild(r1xChild)
        compoundMFnAttr.addChild(r1yChild)
        compoundMFnAttr.addChild(r1zChild)
        compoundMFnAttr.readable = True
        Matrix2Vectors.addAttribute(Matrix2Vectors.row1)

        Matrix2Vectors.row2 = compoundMFnAttr.create('row2', 'row2')
        r2xChild = numMFnAttr.create("r2x", "r2x", om2.MFnNumericData.kFloat)
        r2yChild = numMFnAttr.create("r2y", "r2y", om2.MFnNumericData.kFloat)
        r2zChild = numMFnAttr.create("r2z", "r2z", om2.MFnNumericData.kFloat)
        compoundMFnAttr.addChild(r2xChild)
        compoundMFnAttr.addChild(r2yChild)
        compoundMFnAttr.addChild(r2zChild)
        compoundMFnAttr.readable = True
        Matrix2Vectors.addAttribute(Matrix2Vectors.row2)

        Matrix2Vectors.row3 = compoundMFnAttr.create('row3', 'row3')
        r3xChild = numMFnAttr.create("r3x", "r3x", om2.MFnNumericData.kFloat)
        r3yChild = numMFnAttr.create("r3y", "r3y", om2.MFnNumericData.kFloat)
        r3zChild = numMFnAttr.create("r3z", "r3z", om2.MFnNumericData.kFloat)
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
        print("---------------------COMPUTE---------------------")

        state = om2.MFnDependencyNode(self.thisMObject()).findPlug('nodeState', False).asInt()
        if state == 1:
            data.outputValue(Matrix2Vectors.mtxIn).setFloat(data.inputValue(Matrix2Vectors.row0).asFloat())
            return

        if plug == Matrix2Vectors.mtxIn:
            row0 = data.inputValue(Matrix2Vectors.row0).asFloat()
            row1 = data.inputValue(Matrix2Vectors.row1).asFloat()

            val_handle = data.outputValue(Matrix2Vectors.mtxIn)  # type: om.MDataHandle
            print(val_handle)
            # val_handle.setFloat(amp * math.sin(arg))
            data.setClean(plug)



def initializePlugin(obj):
    fn_plugin = om2.MFnPlugin(obj, 'Fangmin Chen', '1.0')
    fn_plugin.registerNode(Matrix2Vectors.node_name, Matrix2Vectors.node_id,
                           Matrix2Vectors.creator, Matrix2Vectors.initialize)


def uninitializePlugin(obj):
    fn_plugin = om2.MFnPlugin(obj)
    fn_plugin.deregisterNode(Matrix2Vectors.node_id)
