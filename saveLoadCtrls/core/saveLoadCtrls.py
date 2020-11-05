'''
Author:Fangmin Chen
Version: 1.0

Save: selected ctrl/s worldmatrix to a json file
load: json file value and multiply with ctrls inverseParentMatrix
USAGE save: Select Ctrl/s run save method to save
USAGE load: run load method to try load select ctrl/s

toDo list: Enable load everything in json file
toDo list: Currently ctrls needs to be uniquely named
toDo list: loading a negative XYZ value on selected object, will not work correctly. another item for my
'''
import os
import re
import json
import maya.cmds as cmds
import maya.api.OpenMaya as om2



dagPath = om2.MDagPath()

class SaveLoadCtrls():
    def __init__(self):
        self.filename = 'ctrlWorldMtx_v001.json'
        self.USERHOMEPATH = r'C:\tools\mayaTools\saveLoadCtrls\json'
        self.FINDDIGITS = re.compile(r'\d+')
        self.fileList = sorted(os.listdir(self.USERHOMEPATH))

        self.treeList = list()
        self.jsonDataDict = dict()

    def toFile(self, jsonDataDump, filename):
        '''
        Write to json file
        :param jsonDataDump: json data
        :return: None
        '''
        with open(os.path.join(self.USERHOMEPATH, filename), 'w') as jDump2File:
            json.dump(jsonDataDump, jDump2File)


    def fromFile(self, filename):
        '''
        Read json file
        :param filename: str
        :return: json dictionary
        '''
        with open(os.path.join(self.USERHOMEPATH, filename), 'r') as jsonFile:
            jsonData = json.load(jsonFile)
            return jsonData


    def stripNameSpace(self, objName):
        '''
        Check to see if there is a namespace on the incoming name, if yes, strip and return name with no namespace
        :param name: str
        :return: str, name with no namespace
        '''
        name = objName
        if ':' in name:
            name = name.split(':')[-1]
        return name


    def jsonNode(self, ctrlName, parentNode, matrix):
        '''
        create json node
        :param ctrlName: str, fullDagPath with namespace replaced with wildcard sign
        :param matrix
        :return: json
        '''
        nodeDict = {
            ctrlName:
                {
                    'parent': parentNode,
                    'matrix': matrix
                }
        }
        return nodeDict


    def setFloatWithConditions(self, srtMTransMtx, mPlugList):
        '''
        Setting values on unlocked attributes
        :param srtMTransMtx: MTransformationMatrix (translation, rotation or scale)
        :param mPlugList: MPlug
        :return: None
        '''
        for idx, srtPlug in enumerate(mPlugList):
            if not srtPlug.isLocked and not srtPlug.isFreeToChange():
                srtPlug.setFloat(srtMTransMtx[idx])
            else:
                continue


    def setAtters(self, mObjectHandle, mtx, matchScl=True):
        '''
        Sets translation/rotation
        :param mObjectHandle: MObjectHandle
        :param mtx: MMatrix
        :param matchScl: bool, default False, match scale
        :return: None
        '''
        if mObjectHandle.isValid():
            mObj = mObjectHandle.object()
            mFn = om2.MFnDependencyNode(mObj)
            mTransMtx = om2.MTransformationMatrix(mtx)

            trans = mTransMtx.translation(om2.MSpace.kWorld)
            rot = mTransMtx.rotation()

            transX = mFn.findPlug('translateX', False)
            transY = mFn.findPlug('translateY', False)
            transZ = mFn.findPlug('translateZ', False)
            self.setFloatWithConditions(trans, [transX, transY, transZ])

            rotX = mFn.findPlug('rotateX', False)
            rotY = mFn.findPlug('rotateY', False)
            rotZ = mFn.findPlug('rotateZ', False)
            self.setFloatWithConditions(rot, [rotX, rotY, rotZ])

            if matchScl:
                scl = mTransMtx.scale(om2.MSpace.kObject)
                sclX = mFn.findPlug('scaleX', False)
                sclY = mFn.findPlug('scaleY', False)
                sclZ = mFn.findPlug('scaleZ', False)
                self.setFloatWithConditions(scl, [sclX, sclY, sclZ])


    def getNextCtrlNode(self, mObjHandle):
        '''
        Recursively find parent node and stops at the given blacklist
        :param mObjHandle: MObjectHandle
        :return: None
        '''
        blackList = ['world', 'rig']
        if mObjHandle.isValid():
            mObj = mObjHandle.object()
            mFnDag = om2.MFnDagNode(mObj)
            nextCtrlNode = mFnDag.parent(0)
            parentMFnDag = om2.MFnDagNode(nextCtrlNode)

            mFnDepend = om2.MFnDependencyNode(nextCtrlNode)
            nextCtrlNodeMObjHandle = om2.MObjectHandle(nextCtrlNode)

            name = self.stripNameSpace(mFnDag.name())
            parentName = self.stripNameSpace(mFnDepend.name())
            mtx = self.getMatrix(mObjHandle)
            if parentMFnDag.child(0).apiType() == om2.MFn.kNurbsCurve or parentMFnDag.childCount() > 1 \
                    or parentName in blackList:
                self.jsonDataDict.update(self.jsonNode(name, '', mtx))
                return
            else:
                self.jsonDataDict.update(self.jsonNode(name, parentName, mtx))
                self.getNextCtrlNode(nextCtrlNodeMObjHandle)


    def getMatrix(self, mObjectHandle, matrixPlug='worldMatrix'):
        '''
        Get matrix, if plug is an array it will return index 0 of that plug
        :param mObjectHandle: MObjectHandle
        :return: matrix
        '''
        if mObjectHandle.isValid():
            mObj = mObjectHandle.object()
            mFn = om2.MFnDependencyNode(mObj)
            mtxPlug = mFn.findPlug(matrixPlug, False)

            if mtxPlug.isArray:
                mtxPlug = mtxPlug.elementByLogicalIndex(0)

            plugMObj = mtxPlug.asMObject()
            mFnMtxData = om2.MFnMatrixData(plugMObj)
            mtx = mFnMtxData.matrix()
            serializableMtx = tuple(mtx)
            return serializableMtx


    def getTreeList(self, jsonData, objName):
        '''
        Recursively add the parent srtBuffers to a parentList
        :param jsonData: json
        :param objName: str
        :return: None
        '''
        if jsonData[objName].get('parent') == '':
            return
        else:
            parent = jsonData[objName].get('parent')
            self.treeList.append(parent)
            self.getTreeList(jsonData, parent)


    def saveCtrlMtx(self):
        '''
        Save all selected ctrl and parents world matrix
        '''
        selList = om2.MGlobal.getActiveSelectionList()
        mObjs = [selList.getDependNode(idx) for idx in range(selList.length())]

        for mObj in mObjs:
            if mObj.apiType() == om2.MFn.kTransform:
                mObjHandle = om2.MObjectHandle(mObj)
                self.getNextCtrlNode(mObjHandle)

        if os.path.isdir(self.USERHOMEPATH):
            self.toFile(self.jsonDataDict, self.filename)
        else:
            os.makedirs(self.USERHOMEPATH)
            self.toFile(self.jsonDataDict, self.filename)
        print('Save Done!')


    def loadCtrlMtx(self, matchScl=False, loadBuffers=False):
        '''
        load ctrl mtx
        if: there is a selection the script will try to load the value on the selected ctrl
        else: try to load everything from file
        '''

        jsonData = self.fromFile(self.filename)
        selList = om2.MGlobal.getActiveSelectionList()
        mObjs = [selList.getDependNode(idx) for idx in range(selList.length())]
        for mobj in mObjs:
            mFn = om2.MFnDependencyNode(mobj)
            name = mFn.name()
            objName = self.stripNameSpace(name)

            self.treeList.append(objName)
            self.getTreeList(jsonData, objName)

            if objName in jsonData:
                objectList = [objName]
                if loadBuffers:
                    objectList = reversed(self.treeList)

                for obj in objectList:
                    myObjName = obj
                    if not cmds.objExists(myObjName):
                        myObjName = '*:{}'.format(obj)

                    objSelList = om2.MGlobal.getSelectionListByName(myObjName)
                    mObj = objSelList.getDependNode(0)
                    fromFileMtx = om2.MMatrix(jsonData[obj].get('matrix'))
                    drivenMObjHandle = om2.MObjectHandle(mObj)
                    parentInverseMtx = self.getMatrix(drivenMObjHandle, 'parentInverseMatrix')
                    parentInverseMMtx = om2.MMatrix(parentInverseMtx)

                    mtx = fromFileMtx * parentInverseMMtx

                    self.setAtters(drivenMObjHandle, mtx, matchScl=matchScl)
            else:
                print('{} is not in the saved json dictionary!'.format(objName))
        print('Load Done!')
