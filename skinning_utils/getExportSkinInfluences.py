import os
import json
import re
import logging
import maya.api.OpenMaya as om2
import maya.api.OpenMayaAnim as om2anim
import maya.cmds as cmds

logger = logging.ERROR

FINDDIGITS = re.compile(r"\d+")
USERHOMEPATH = r"/depts/cg_treehouse/fangc/mayaCtrlJsons"
filename = "skinInfluences_v001.json"
fileList = sorted(os.listdir(USERHOMEPATH))

selList = om2.MGlobal.getActiveSelectionList()
mObjs = [selList.getDependNode(idx) for idx in range(selList.length())]


class GetExportSkinInfluences():

    def findSC(self, mObjHandle):
        """

        :param mObjHandle:
        :return:
        """
        if mObjHandle.isValid():
            mObj = mObjHandle.object()
            mfn = om2.MFnDagNode(mObj)
            history = cmds.listHistory(mfn.fullPathName(), pdo=True) or list()
            deformers = [deformer for deformer in history if 'geometryFilter' in cmds.nodeType(deformer, i=True)]

            outputList = list()
            sel = om2.MSelectionList()
            if not deformers:
                logger.warning("unable to find any deformers in {}".format(str(mObj)))
                return outputList
            for deformer in deformers:
                if cmds.nodeType(deformer) == "skinCluster":
                    sel.add(deformer)

            outputList = [sel.getDependNode(idx) for idx in range(sel.length())]
            return outputList


    def getSkinInfluences(self, scList):
        """

        :param scList:
        :return:
        """
        if scList:
            outputDict = dict()

            for sc in scList:
                mFnSkin = om2anim.MFnSkinCluster(sc)
                infObj = mFnSkin.influenceObjects()
                scName = mFnSkin.name()
                scNameNoNS = scName.split(':')[-1]
                jntList = list()

                for jnt in infObj:
                    jntName = om2.MDagPath(jnt).fullPathName().split(':')[-1]
                    if not jntName in jntList:
                        jntList.append(jntName)
                    else:
                        continue
                outputDict.update({scNameNoNS: jntList})

            return outputDict


    def toFile(self, jsonDataDump, filename):
        """
        Write to json file
        :param jsonDataDump: json data
        :return: None
        """
        with open(os.path.join(USERHOMEPATH, filename), "w") as jDump2File:
            json.dump(jsonDataDump, jDump2File)


    def fromFile(self, filename):
        """
        Read json file
        :param filename: str
        :return: json dictionary
        """
        with open(os.path.join(USERHOMEPATH, filename), "r") as jsonFile:
            jsonData = json.load(jsonFile)
            return jsonData


    def saveInfluences(self, mObjHandle, filename):
        """

        :param mObjHandle:
        :param filename:
        :return:
        """
        scList = self.findSC(mObjHandle)
        jsonDump = self.getSkinInfluences(scList)
        self.toFile(jsonDump, filename)


    def applySkin(self, ns, nameRaw, skinName, inf):
        """

        :param ns:
        :param nameRaw:
        :param skinName:
        :param inf:
        :return:
        """
        if not cmds.objExists('{}'.format(skinName)):
            cmds.skinCluster(inf, nameRaw.format(ns), n=skinName)
        else:
            try:
                cmds.skinCluster(nameRaw, edit=True, ai=inf)
            except:
                print(inf, 'error')


    def findInfluencesInScene(self, mObjHandle, loadFile):
        """

        :param mObjHandle:
        :param loadFile:
        :return:
        """
        if mObjHandle.isValid():
            mObj = mObjHandle.object()

            nameSpace = om2.MFnDependencyNode(mObj).namespace
            nameRaw = om2.MFnDependencyNode(mObj).name()

            data = dict(self.fromFile(loadFile))

            for key, value in data.items():
                for item in value:
                    fullName = '{}:{}'.format(nameSpace, item)
                    if cmds.objExists(fullName):
                        self.applySkin(nameSpace, nameRaw, key, fullName)
                    else:
                        print(fullName)
            print('Skin Applied!')


getESCI = GetExportSkinInfluences()

for mObj in mObjs:
    mObjHandle = om2.MObjectHandle(mObj)
    getESCI.findInfluencesInScene(mObjHandle, filename)
