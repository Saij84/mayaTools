# encoding: utf8

import maya.api.OpenMaya as om2
import math


def maya_useNewAPI():
    pass


class SimpleNode(om2.MPxNode):
    node_name = 'simpleNode'
    node_id = om2.MTypeId(0x84002)
    a_arg = om2.MMatrix()
    a_amp = None
    a_val = None

    def __init__(self):
        om2.MPxNode.__init__(self)

    @staticmethod
    def creator():
        return SimpleNode()

    @staticmethod
    def initialize():
        num_attr = om2.MFnNumericAttribute()
        mtx_attr = om2.MFnMatrixAttribute()

        SimpleNode.a_arg = mtx_attr.create('matrixIn', 'mtxIn', om2.MFnNumericData.kFloat)
        mtx_attr.writable = True
        mtx_attr.storable = True
        om2.MPxNode.addAttribute(SimpleNode.a_arg)

        SimpleNode.a_amp = num_attr.create('amp', 'amp', om2.MFnNumericData.kFloat, 1.0)
        num_attr.storable = True
        om2.MPxNode.addAttribute(SimpleNode.a_amp)

        SimpleNode.a_val = num_attr.create('val', 'val', om2.MFnNumericData.kFloat, 0.0)
        num_attr.storable = True
        num_attr.writable = True
        om2.MPxNode.addAttribute(SimpleNode.a_val)

        om2.MPxNode.attributeAffects(SimpleNode.a_arg, SimpleNode.a_val)
        om2.MPxNode.attributeAffects(SimpleNode.a_amp, SimpleNode.a_val)

    def compute(self, plug, data):
        # type: (om.MPlug, om.MDataBlock) -> None

        state = om2.MFnDependencyNode(self.thisMObject()).findPlug('nodeState', False).asInt()
        if state == 1:
            data.outputValue(SimpleNode.a_val).setFloat(data.inputValue(SimpleNode.a_arg).asFloat())
            return

        if plug == SimpleNode.a_val:
            arg = data.inputValue(SimpleNode.a_arg).asFloat()
            amp = data.inputValue(SimpleNode.a_amp).asFloat()

            val_handle = data.outputValue(SimpleNode.a_val)  # type: om.MDataHandle
            val_handle.setFloat(amp * math.sin(arg))
            data.setClean(plug)


def initializePlugin(obj):
    fn_plugin = om2.MFnPlugin(obj, 'ilya radovilsky', '1.0')
    fn_plugin.registerNode(SimpleNode.node_name, SimpleNode.node_id, SimpleNode.creator, SimpleNode.initialize)


def uninitializePlugin(obj):
    fn_plugin = om2.MFnPlugin(obj)
    fn_plugin.deregisterNode(SimpleNode.node_id)
