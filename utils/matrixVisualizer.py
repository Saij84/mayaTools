import sys
import maya.api.OpenMaya as om2
import maya.OpenMayaMPx as OpenMayaMPx

# ... additional imports here ...

kPluginCmdName = 'mtx2Vectors'


##########################################################
# Plug-in
##########################################################
class Mtx2Vector(OpenMayaMPx.MPxCommand):

    def __init__(self):
        ''' Constructor. '''
        OpenMayaMPx.MPxCommand.__init__(self)

    def doIt(self, args):
        ''' Command execution. '''

        testMtxInput = [
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1
        ]

        mtxInput = om2.MMatrix(testMtxInput)
        mTransMtx = om2.MTransformationMatrix(mtxInput)

        mtxRow1 = [mtxInput[idx] for idx in range(0, 4)]
        mtxRow2 = [mtxInput[idx] for idx in range(4, 8)]
        mtxRow3 = [mtxInput[idx] for idx in range(8, 12)]
        mtxRow4 = [mtxInput[idx] for idx in range(12, 16)]


##########################################################
# Plug-in initialization.
##########################################################
def cmdCreator():
    ''' Create an instance of our command. '''
    return OpenMayaMPx.asMPxPtr(Mtx2Vector())


def initializePlugin(mobject):
    ''' Initialize the plug-in when Maya loads it. '''
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerCommand(kPluginCmdName, cmdCreator)
    except:
        sys.stderr.write('Failed to register command: ' + kPluginCmdName)


def uninitializePlugin(mobject):
    ''' Uninitialize the plug-in when Maya un-loads it. '''
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand(kPluginCmdName)
    except:
        sys.stderr.write('Failed to unregister command: ' + kPluginCmdName)


##########################################################
# Sample usage.
##########################################################
''' 
# Copy the following lines and run them in Maya's Python Script Editor:

import maya.cmds as cmds
cmds.loadPlugin('Mtx2Vector.py')
cmds.Mtx2Vector()

'''

