"""
Author:Fangmin Chen
Version: 1.0

mass skinAs based on selected hrc

USAGE save: select source hrc then target hrc

NOTE: should
"""

import logging
from maya.api.OpenMaya import om2anim, om2, cmds

from AL.maya2.session import nodes as alm2s_nodes
from AL.rig.jobs.common.commands.maya.skin import utils as skUtils
from AL.rig.jobs.common import constants
from AL.maya2.session import contexts as alm2_ssContexts

logger = logging.getLogger(__name__)


class MassSkinAss:
    def __init__(self, srouceRoot, targetRoot):
        self.srcRoot = srouceRoot
        self.trgRoot = targetRoot

    def skinAs(self, source=None, target=None):
        logger.info("Transferring skinClusters now..")
        sc = [skin for skin in cmds.listHistory(source) if cmds.nodeType(skin) == 'skinCluster']
        logger.debug("skinCluster: {}".format(sc))
        if not sc:
            logger.warning("No skinCluser found on source mesh!")
            return

        inf = cmds.skinCluster(sc[0], q=True, inf=True)
        logger.debug("Influences: {}".format(inf))

        shn = str(target.split("|")[-1])
        logger.debug("Starting transfer from {} to target: {}".format(sc[0], target))

        scName = '{}_{}'.format(shn, constants.SKINCLUSTER_SUFFIX)
        logger.debug("Creating new skinCluster: {}".format(scName))

        targetMObject = alm2s_nodes.findNode(target)
        existing = skUtils.findSkinCluster(targetMObject)

        if existing:
            destExsistingSC = om2.MFnDependencyNode(existing[0])
            destSC = destExsistingSC.name()
        else:
            destSC = cmds.skinCluster(inf, target, n=scName, toSelectedBones=True)[0]
            logger.debug("destSC: {}".format(destSC))

        # Now transfer the weights from one to the other
        with alm2_ssContexts.SelectionKeeper():
            cmds.select(source, target)
            # selecting the meshes instead of the skin cluster becasue
            # it fix some failed copy skin
            cmds.copySkinWeights(noMirror=True,
                                 normalize=False,
                                 surfaceAssociation='closestPoint',
                                 influenceAssociation=['oneToOne', 'label', 'closestJoint']
                                 )

        logger.debug("Removing unused influences")
        mSel = om2.MSelectionList()
        mSel.add(target)
        dag = mSel.getDagPath(0)
        skinFn = om2anim.MFnSkinCluster()
        skinMob = alm2s_nodes.findNode(destSC)
        skinFn.setObject(skinMob)

        influencesDAGArray = skinFn.influenceObjects()
        logger.debug(dag.extendToShape().apiType())
        if dag.extendToShape().apiType() == om2.MFn.kNurbsCurve:
            logger.debug("Type kNurbsCurve found!")
            apiComponents = om2.MFnSingleIndexedComponent().create(om2.MFn.kCurveCVComponent)
            count = om2.MFnNurbsCurve(mSel.getDependNode(0)).numCVs
        else:
            apiComponents = om2.MFnSingleIndexedComponent().create(om2.MFn.kMeshVertComponent)
            count = om2.MItMeshVertex(mSel.getDependNode(0)).count()

        logger.debug("Count:  {}".format(count))

        ### ALSO YOU CAN PROB SET THE SKINCLUSTER FROM THE MSELCTION LIST
        apiVertices = om2.MIntArray(count, 0)
        for i in range(count):
            apiVertices.insert(i, i)
        om2.MFnSingleIndexedComponent(apiComponents).addElements(apiVertices)
        w = []
        for x in range(len(influencesDAGArray)):
            wghts = skinFn.getWeights(mSel.getDagPath(0), apiComponents, x)
            w.extend([(influencesDAGArray[x], wghts)])

        for j in w:
            if len(list(set(j[1]))) == 1 and list(set(j[1]))[0] == 0.0:
                skDG = om2.MFnDependencyNode(skinMob)
                cmds.skinCluster(skDG.name(), e=True, removeInfluence=j[0].fullPathName())

    def delteDagNodes(self):
        """
        delte all dagPose node in scene
        :return: None
        """
        selList = cmds.ls(type="dagPose")

        for dagP in selList:
            if dagP:
                print "deleted dagPose:", dagP
                cmds.delete(dagP)

    def filterName(self, hrc):
        """
        filter names to remove '|' and ':' then return a dic with the filtered name and
        return a dict with filtered name as key and original full path as value
        :param hrc: selList
        :return: dict
        """
        returnList = dict()

        if hrc:
            for item in hrc:
                shortName = item.split('|')[-1]
                if ':' in shortName:
                    shortName = shortName.split(':')[-1]
                returnList.update({shortName: item})

        return returnList

    def compairDict(self, srcDict, trgDict):
        """
        compair two dicts, if items in srcDict exits in trgDict then return the full path src value and
        full path of target value
        :param srcDict: dict
        :param trgDict: dict
        :return: tuple
        """
        filteredList = list()

        if srcDict and trgDict:
            for srcKey, srcValue in srcDict.items():
                if srcKey in trgDict.keys():
                    filteredList.append((srcValue, trgDict.get(srcKey)))
        return filteredList

    def run(self):
        srcDecendants = cmds.listRelatives(self.srcRoot, ad=True, f=True, type='transform')
        trgDecendants = cmds.listRelatives(self.trgRoot, ad=True, f=True, type='transform')
        srcDict = self.filterName(srcDecendants)
        trgDict = self.filterName(trgDecendants)

        srcTargetList = self.compairDict(srcDict, trgDict)

        for src, trg in srcTargetList:
            self.skinAs(src, trg)

        self.delteDagNodes()
        logger.info("Transfer complete.")
