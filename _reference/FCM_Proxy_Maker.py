# FCM_Proxy_Maker
version = 'v1.2_OpenBeta'

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''

L i c e n s e 

v1.2:
- Non skinned meshes removed. Automatic proxy now always excluded the non skinned, 
and create proxy manually always do nothing and you need to choose which method
you want to apply


Permission is hereby granted, free of charge, to any person obtaining a copy of 
this software and associated documentation files (the "Software"), to deal in 
the Software without restriction, including without limitation the rights to use, 
copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the 
Software, and to permit persons to whom the Software is furnished to do so, 
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS 
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER 
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


I n s t a l l a t i o n 
    
1) Put the folder image "FCM_Proxy_Maker_Logo" in this location:
C:\Users\YourUser\Documents\maya\201x\prefs\icons

2)Drag and drop the file "Drag_and_drop_Install_FCM_Proxy_Maker" into the viewport. 
It will create a new shelf button.


C o n t a c t :
    
(If you have any feedback or want to bash me)
-Email: francm127@hotmail.com
-Facebook: facebook.com/Fran127
-LinkedIn: linkedin.com/in/francm3danimator/



'''''''''''''''''''''''''''''''''''''''''''''''''''''''''

import maya.cmds as cmds
import maya.mel as mel
import sys
import random
import math

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            Create Proxy Skin Also For Non Skinned Meshes def
            
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''


def createProxySkinAlsoNonSkinned():
    global FolderProxy, Set_Normal, Excluded_Nodes, Set_NoSkin_List, Set_Skin_List
    FolderProxy = 'Folder_Proxys'
    Set_Normal = 'Set_Normal'
    Excluded_Nodes = 'Excluded_Nodes'

    # Check if nothing is selected
    sel = cmds.ls(sl=True)
    if len(sel) > 0:
        # Check if there is a nurbsCurve selected
        nurbsCurves = cmds.filterExpand(sm=9)
        try:
            if (len(nurbsCurves)) > 0:
                cmds.warning('You must select only meshes')
        except:
            # Filter only Geos
            geos = cmds.filterExpand(sm=12, fullPath=True)
            cmds.pickWalk(geos, d="up")
            # Get the selections but avoiding the full path
            list = cmds.ls(sl=True)
            if len(list) > 0:
                # Create Empty lists
                Set_Skin_List = []
                Set_NoSkin_List = []
                # check if the items has skin or not and put them in temporary sets
                for item in list:
                    checkSkin = (mel.eval('findRelatedSkinCluster ' + item))
                    # if the result is less than 1 the mesh doesn't have skin
                    if len(checkSkin) > 1:
                        Set_Skin_List.append(item)
                    else:
                        Set_NoSkin_List.append(item)
                # Operation for skin meshes
                cmds.select(Set_Skin_List)
                createProxySkin()
                # Operatin for non skinned meshes
                cmds.select(Set_NoSkin_List)
                '''
                # Find wich radiobutton is selected for non skinned method
                if cmds.radioButtonGrp ("nonSkinnedMethod", q=True, sl=True) == 1:
                    def nonSkinnedMeshes():
                        createProxyExcluded()  
                if cmds.radioButtonGrp ("nonSkinnedMethod", q=True, sl=True) == 2:
                    def nonSkinnedMeshes():
                        createProxySkinOneJoint()
                if cmds.radioButtonGrp ("nonSkinnedMethod", q=True, sl=True) == 3:
                    def nonSkinnedMeshes():
                        createGroupsAndSets()
                        print ("Non_Skinned_Mesh_Nothing"),
                        cmds.select (clear=True) 
                '''
                createGroupsAndSets()
                showProxy()
                # If there is Non skinned meshes Show Proxy will turn off
                if len(Set_NoSkin_List) > 1:
                    hideorShowProxySet(value=0)
                    cmds.checkBoxGrp("ShowProxy", e=True, value1=False)
                # Print
                result = []
                for Obj in list:
                    if "_Proxy" in Obj:
                        pass
                    else:
                        result.append(Obj)
                        print(str(len(result)) + ' Proxy Skin Created\n'),
                        if len(Set_NoSkin_List) > 0:
                            currentSel = cmds.ls(sl=True)
                            if len(currentSel) > 1:
                                cmds.warning(
                                    "All the meshes you have selected don't have skincluster to copy from, choose what you want to do with them")
                            else:
                                cmds.warning(
                                    "The mesh you have selected doesn't have skincluster to copy from, choose what you want to do with it")

                # Show or Hide Set_Proxy depending of the state of "Show Proxy" checkbox
                if cmds.checkBoxGrp("ShowProxy", query=True, value1=True) == 1:
                    hideorShowProxySet(value=1)
                else:
                    hideorShowProxySet(value=0)
                checkProxyAvaibleToCreate()
                createHUD()
    else:
        cmds.warning('Nothing selected')


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            Create Proxy Skin def
            
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''


def createProxySkin():
    # Progress Bar
    if cmds.window("progressWindow", exists=True):
        cmds.deleteUI('progressWindow')
    if cmds.window("textTest", exists=True):
        cmds.deleteUI('textTest')

    window = cmds.window('progressWindow', title='Progress Window')
    cmds.columnLayout(adjustableColumn=True)

    cmds.text('textTest', align='center')
    progressControl = cmds.progressBar(maxValue=7, width=300, isInterruptable=True)

    cmds.showWindow(window)
    cmds.window("progressWindow", edit=True, w=300, h=35, topLeftCorner=[250, 760])

    # Create Proxy Skin
    OrigM = cmds.ls(sl=True, long=True)

    for Obj in OrigM:
        if "_Proxy" in Obj:
            cmds.warning("Proxy Already Exists!")
        else:
            # Get Array for all selection
            createGroupsAndSets()
            # Progress bar
            cmds.progressBar(progressControl, edit=True, step=1)

            # Duplicate and query the object
            ProxyM = cmds.duplicate(Obj)
            # Get all joints from selected Mesh
            cmds.select(Obj)
            getAllJointsFromSelection()
            jointsAll = cmds.ls(type='joint')
            # Bind Skin If the script looking joints from sel failed will apply for all the joints in the scene
            try:
                if len(joints) > 0:
                    cmds.skinCluster(joints, ProxyM, n='skinCluster_Proxy_1')
                else:
                    cmds.skinCluster(jointsAll, ProxyM, n='skinCluster_Proxy_1')
            except:
                cmds.select(cmds.skinCluster(jointsAll, ProxyM, n='skinCluster_Proxy_1'))

            # Progress bar
            cmds.text('textTest', edit=True, label='Assigning Skin from original mesh')
            cmds.progressBar(progressControl, edit=True, step=1)
            # Copy Skin
            cmds.copySkinWeights(Obj, ProxyM, noMirror=True, surfaceAssociation='closestPoint',
                                 influenceAssociation='closestJoint')
            cmds.text('textTest', edit=True, label='Copy skin')
            cmds.progressBar(progressControl, edit=True, step=1)

            # Clean up / More fast than the legacy thanks to glTools!
            cmds.text('textTest', edit=True, label='Remove unused influences')
            cmds.progressBar(progressControl, edit=True, step=1)
            remove_unused_influences(ProxyM)
            # Progress bar
            cmds.text('textTest', edit=True, label='Finishing operation')
            cmds.progressBar(progressControl, edit=True, step=1)

            # Put them into sets
            cmds.sets(Obj, edit=True, add='Set_Normal')
            cmds.sets(ProxyM, edit=True, add='Set_Proxy')
            # Group Proxy
            group = cmds.group(ProxyM, name='Proxy_Skin_1')
            # Change name of ProxyM
            cmds.rename(ProxyM, ProxyM[0] + '_Proxy')
            # Parent Group to Folder Proxys
            cmds.parent(group, 'Folder_Proxys')
            # End Progress bar
            cmds.progressBar(progressControl, edit=True, endProgress=1)

    # Delete UI Progress Window
    cmds.deleteUI('progressWindow')


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            Create Proxy Skin One Joint def
            
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''


def createProxySkinOneJoint():
    # Get Array for all selection
    OrigMeshes = cmds.ls(sl=True, long=True)

    for OrigM in OrigMeshes:
        if "_Proxy" in OrigM:
            cmds.warning("Proxy Already Exists!")
        else:

            # Get all joints from the scene
            joints = cmds.ls(type='joint')
            createGroupsAndSets()
            # Duplicate and Get an Array
            ProxyM = cmds.duplicate(OrigM)

            # Put them into sets
            cmds.sets(OrigM, edit=True, add='Set_Normal')
            cmds.sets(ProxyM[0], edit=True, add='Set_Proxy')
            # Group Proxy
            groupTemp = cmds.group(ProxyM[0], name='Proxy_Skin_OneJoint_1')
            # Parent Group to Folder Proxys
            cmds.parent(groupTemp, 'Folder_Proxys')
            # Find distance between all the joints in the scene and de Proxy meshes
            dist = []
            for j in joints:
                sp = cmds.xform(ProxyM[0], q=True, ws=True, scalePivot=True)
                ep = cmds.xform(j, q=True, ws=True, scalePivot=True)
                distance = math.sqrt(
                    math.pow(sp[0] - ep[0], 2) + math.pow(sp[1] - ep[1], 2) + math.pow(sp[2] - ep[2], 2))
                dist.append([distance, j])
                dist.sort()
                closest_jnt = dist[0][1]
            # Apply skin with the nearest joint
            cmds.skinCluster(closest_jnt, ProxyM[0], n='skinCluster_Proxy_1')
            # Change name of ProxyM
            cmds.rename(ProxyM[0], ProxyM[0] + '_Proxy')
            cmds.select(cl=True)


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            Create Proxy Constraint Automatic WIP
            
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''


def createProxyConstraintAutomatic():
    # Get Array for all selection
    OrigMeshes = cmds.ls(sl=True, long=True)
    # Get all joints from the scene
    joints = cmds.ls(type='nurbsCurve')
    cmds.select(joints)
    cmds.pickWalk(d="up")
    joints = cmds.ls(sl=True, long=True)

    createGroupsAndSets()

    for OrigM in OrigMeshes:
        # Duplicate and Get an Array
        ProxyM = cmds.duplicate(OrigM)

        # Put them into sets
        cmds.sets(OrigM, edit=True, add='Set_Normal')
        cmds.sets(ProxyM[0], edit=True, add='Set_Proxy')
        # Group Proxy
        groupTemp = cmds.group(ProxyM[0])
        # Parent Group to Folder Proxys
        cmds.parent(groupTemp, 'Folder_Proxys')
        # Find distance between all the joints in the scene and de Proxy meshes
        dist = []
        for j in joints:
            sp = cmds.xform(ProxyM[0], q=True, ws=True, scalePivot=True)
            ep = cmds.xform(j, q=True, ws=True, scalePivot=True)
            distance = math.sqrt(math.pow(sp[0] - ep[0], 2) + math.pow(sp[1] - ep[1], 2) + math.pow(sp[2] - ep[2], 2))
            dist.append([distance, j])
            dist.sort()
            closest_jnt = dist[0][1]
        # Apply skin with the nearest joint
        cmds.parentConstraint(closest_jnt, groupTemp, mo=True)
        # Change name of ProxyM
        cmds.rename(ProxyM[0], OrigM + '_Proxy')
        cmds.rename(groupTemp, 'Proxy_Skin_OneCtrl_1')
        cmds.select(clear=True)
        showProxy()


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            create Proxy Constraint def
            
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''


def createProxyConstraint():
    tempSel = cmds.ls(sl=True)
    # Sorry for using undo
    cmds.undo()
    # Get Geos
    Omesh = cmds.filterExpand(sm=12, fullPath=True)  # agregar full path
    # Create CtrlFather array using the last element select
    CtrlFather = tempSel[-1]

    # Cancel operation if your last selection is not a nurbsCurve
    cmds.select(CtrlFather)
    cmds.pickWalk(d='down')
    sel = cmds.ls(sl=True)
    if cmds.objectType(sel) != 'nurbsCurve':
        cmds.select(tempSel)
        sys.exit('You must select a control for the last selection')

    createGroupsAndSets()

    # Create Pmesh
    Pmesh = []
    for mesh in Omesh:
        sel = cmds.duplicate(mesh, name=(mesh + '_Proxy'))

        tempGroup = cmds.group(sel)
        Pmesh.append(tempGroup)

    # Create Group and constraint it
    groupProxy = cmds.group(Pmesh, name='Proxy_Constraint_1')
    cmds.parentConstraint(CtrlFather, groupProxy, mo=True)
    # Put them into sets
    cmds.sets(Omesh, edit=True, add='Set_Normal')
    cmds.sets(Pmesh, edit=True, add='Set_Proxy')
    # Parent groupProxy to Folder Proxys
    cmds.parent(groupProxy, 'Folder_Proxys')
    # Rename each PMesh as name_Proxy
    for item in Pmesh:
        cmds.rename(item, item + '_Proxy')

    showProxy()
    # Select Ctrl
    cmds.select(CtrlFather)

    # Show or Hide Set_Proxy depending of the state of "Show Proxy" checkbox
    if cmds.checkBoxGrp("ShowProxy", query=True, value1=True) == 1:
        hideorShowProxySet(value=1)
    else:
        hideorShowProxySet(value=0)
    checkProxyAvaibleToCreate()


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            Create Proxy Exclude def
            
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''


def createProxyExcluded():
    sel = cmds.ls(sl=True)
    createGroupsAndSets()

    for s in sel:
        if "_Proxy" in s:
            cmds.warning("Proxy Already Exists!")
        else:

            if cmds.objectType(s) == "transform":
                cmds.sets(s, edit=True, add='Set_Normal')

            if cmds.objectType(s) == "mesh":
                cmds.sets(s, edit=True, add='Set_Frozen')
            # if is not a transform or mesh type it goes to exclude
            if cmds.objectType(s) != "transform":
                if cmds.objectType(s) != "mesh":
                    cmds.sets(s, edit=True, add='Excluded_Nodes')

            # go to Proxy Mode
            cmds.setAttr("Folder_Proxys.visibility", 1)
            showProxy()

            print(str(len(sel)) + ' Proxy Excluded Created'),
            checkProxyAvaibleToCreate()


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            Process for skinning methods 
            
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''


def remove_unused_influences(skinCls, targetInfluences=[]):
    '''
    Snippet to removeUnusedInfluences in Autodesk Maya using Python.
    The MEL version runs slowly, over every influence one at a time.
    "targetInfluences" allows you to directly specify which influences to remove.
    This will only remove targets which are not currently being used.
    '''
    allInfluences = cmds.skinCluster(skinCls, q=True, inf=True)
    weightedInfluences = cmds.skinCluster(skinCls, q=True, wi=True)
    unusedInfluences = [inf for inf in allInfluences if inf not in weightedInfluences]
    if targetInfluences:
        unusedInfluences = [
            inf for inf in allInfluences
            if inf in targetInfluences
            if inf not in weightedInfluences
        ]
    cmds.skinCluster(skinCls, e=True, removeInfluence=unusedInfluences)


def getAllJointsFromSelection():
    global joints
    sel = cmds.ls(sl=True)
    history = cmds.listHistory(sel, leaf=True)
    result = []
    for item in history:
        if "skinCluster" in cmds.objectType(item):
            result.append(item)
    result2 = []
    for r in result:
        hola = cmds.skinCluster(r, query=True, inf=True)
        result2.append(hola)
    cmds.select(cl=True)
    for each in result2:
        cmds.select(each, add=True)
    joints = cmds.ls(sl=True)
    cmds.select(cl=True)


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            Delete Proxy def
            
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''


# Delete All
def deleteAllProxys():
    # set Show proxy to On
    cmds.checkBoxGrp("ShowProxy", e=True, value1=True)
    # Turn off frozen propagation
    cmds.freezeOptions(explicitPropagation=False)
    cmds.freezeOptions(downstream='none')

    # Turn on all the checkboxes
    cmds.checkBoxGrp('NodesCheckbox1', edit=True, value1=True, value2=True, value3=True)
    cmds.checkBoxGrp('NodesCheckbox2', edit=True, value1=True, value2=True, value3=True)
    cmds.checkBoxGrp('NodesCheckbox3', edit=True, value1=True, value2=True, value3=True)
    cmds.checkBoxGrp('NodesCheckbox4', edit=True, value1=True, value2=True, value3=True)
    cmds.checkBoxGrp('NodesCheckbox5', edit=True, value1=True, value2=True)

    if cmds.objExists("Folder_Proxys"):
        hideProxy()
        cmds.delete('Folder_Proxys')
    if cmds.objExists("Set_Normal"):
        cmds.delete('Set_Normal')
    if cmds.objExists("Set_Proxy"):
        cmds.delete('Set_Proxy')
    if cmds.objExists("Excluded_Nodes"):
        cmds.delete('Excluded_Nodes')
    if cmds.objExists("Set_Frozen"):
        cmds.delete('Set_Frozen')
    if cmds.objExists('FCM_Proxy_Maker_Settings'):
        cmds.delete('FCM_Proxy_Maker_Settings')
    if cmds.objExists("Set_Rig"):
        cmds.select("Set_Rig")
        try:
            cmds.setAttr(".visibility", 1)
        except:
            cmds.setAttr(".lodVisibility", 1)
        cmds.delete('Set_Rig')
        cmds.select(clear=True)
    try:
        cmds.headsUpDisplay("HUDProxy", edit=True, visible=0)
    except:
        pass

        print("All FCM_Performance Deleted"),
    if cmds.objExists('Folder_Proxys') == 0:
        print("All FCM_Performance Deleted"),


##########################################
def DeleteSelected():
    global sel, result, s
    # remove selected
    sel = cmds.ls(sl=True)
    result = []

    if len(sel) >= 1:
        for s in sel:
            if "_Proxy" in s:
                # show all the original meshes
                hideProxy()
                # Remove "_Proxy" for each selection
                result = ''.join([str(s)])
                result = result.replace('_Proxy', '')
                # Remove from Set
                try:
                    cmds.sets(("*:*" + result), edit=True, rm="Set_Normal")
                # if the object doesn't have a namespace is because is proxy node so let's try this
                except:
                    cmds.sets(s, edit=True, rm="Set_Normal")
                # if the original mesh is a shape (for proxy constraint)
                try:
                    cmds.sets(("*:*" + result + "Shape"), edit=True, rm="Set_Normal")
                except:
                    pass

                # Go back to Proxy mode
                showProxy()
                # Delete proxys
                cmds.pickWalk(s, d="up")
                cmds.delete()
                print(str(len(sel)) + " Proxy deleted"),
            else:
                # search for a node
                objType = cmds.objectType(s)
                if objType == 'transform':
                    # if is not a deform node
                    cmds.warning("This is not a proxy!")
                else:
                    # turn on nodeState
                    cmds.setAttr(s + '.nodeState', 0)
                    # remove them from the excluded set
                    cmds.sets(s, edit=True, rm="Excluded_Nodes")
                    print('nodes excluded successfully\n'),
    else:
        cmds.warning("You must have something selected")


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            Selection Tools
            
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''


# Get All Nodes Scene From Selection
def getAllNodesSceneFromSelection():
    currentSel = cmds.ls(sl=True)
    node = cmds.objectType(currentSel)
    allObjTypeSelected = cmds.ls(type=node)
    cmds.select(allObjTypeSelected)
    numberSel = len(allObjTypeSelected)
    print(str(numberSel) + " " + str(node) + " Selected"),


def selectAllVisibleMeshes():
    shapesAndShapesOrig = cmds.ls(v=True, type='mesh')
    meshes = cmds.filterExpand(shapesAndShapesOrig, sm=12)
    cmds.select(meshes)

    sel = cmds.ls(sl=True)
    for mesh in sel:
        # remove from the list if the mesh is hided trough layerDisplay
        if cmds.getAttr(mesh + '.overrideVisibility') == 0:
            meshes.remove(mesh)
        # remove from the list if the mesh is hided trough losVisibility
        if cmds.getAttr(mesh + '.lodVisibility') == 0:
            meshes.remove(mesh)

    cmds.select(meshes)


def removeObjectsWithoutNameSpaces():
    sel = cmds.ls(sl=True)
    result = []
    for s in sel:
        nameSpace = s.rpartition(':')[0]
        if len(nameSpace) == 0:
            result.append(s)
    cmds.select(sel)
    cmds.select(result, d=True)
    sel = cmds.ls(sl=True)


def unlockAllVismeshes():
    shapesAndShapesOrig = cmds.ls(v=True, type='mesh')
    meshes = cmds.filterExpand(shapesAndShapesOrig, sm=12)
    groups = cmds.ls(type='transform')
    groupsAndMeshes = groups + meshes
    try:
        for item in groupsAndMeshes:
            if cmds.getAttr(item + '.overrideDisplayType') == 2:
                cmds.setAttr(item + '.overrideDisplayType', 0)
                print('All visible meshes are selectable now'),
    except:
        cmds.warning(
            "Couldn't unlock all the meshes because they are in a layerDisplay, check if you can unlock them trough layer display")


# This is still wip, it needs to try with diferents names and
def selectallFaceGroups():
    cmds.select('*:*Face*')
    transform = cmds.ls(sl=True, type='transform')
    cmds.select(transform)


'''
WIP 
def filterSel():
    transform = cmds.ls (sl=True, type='transform')
    cmds.select (transform)

def findWord():
    try:
        cmds.select (word)
    except:
        cmds.warning('Nothing could been selected')


word = '*:*Head*'; findWord()
word = '*:*Facial*'; findWord()


'''
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            Smooth preview def
            
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''


def smoothPreviewAll():
    allShapeMeshes = cmds.ls(type="mesh")
    for mesh in allShapeMeshes:
        try:
            cmds.setAttr(mesh + ".displaySmoothMesh", value1)
        except:
            pass
        try:
            cmds.setAttr(mesh + ".smoothLevel", value2)
        except:
            pass


def smoothPreviewSelected():
    allShapeMeshes = cmds.ls(sl=True)
    for mesh in allShapeMeshes:
        try:
            cmds.setAttr(mesh + ".displaySmoothMesh", value1)
        except:
            pass
        try:
            cmds.setAttr(mesh + ".smoothLevel", value2)
        except:
            pass


def applyButtonSPM():
    global value1
    global value2

    test2 = cmds.radioButtonGrp("Radio2", q=True, select=True)
    if test2 == 1:
        value1 = 0
        value2 = 2

    if test2 == 2:
        value1 = 2
        value2 = 1

    if test2 == 3:
        value1 = 2
        value2 = 2

    test1 = cmds.radioButtonGrp("Radio1", q=True, select=True)
    if test1 == 1:
        smoothPreviewSelected()
        print("Selected")

    if test1 == 2:
        smoothPreviewAll()
        print("all")


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            Simple buttons window def
            
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''


def checkProxyAvaibleToCreate():
    # detect if there isn't more proxy to do
    currentSel = cmds.ls(sl=True)
    selectAllVisibleMeshes()
    removeObjectsWithoutNameSpaces()
    sel = cmds.ls(sl=True)
    if len(sel) == 0:
        hideorShowProxySet(value=1)
        cmds.checkBoxGrp("ShowProxy", e=True, value1=True)
        print('There is no more Proxies to create in the scene'),
    else:
        hideorShowProxySet(value=0)
        cmds.checkBoxGrp("ShowProxy", e=True, value1=False)
    cmds.select(currentSel)
    createHUD()


def frozenAllSelected():
    sel = cmds.ls(sl=True)
    for s in sel:
        cmds.setAttr(s + '.frozen', 1)


def unFrozenAllSelected():
    sel = cmds.ls(sl=True)
    for s in sel:
        cmds.setAttr(s + '.frozen', 0)


def selectMostComplexMesh():
    meshes = []
    meshes = cmds.ls(type='mesh')
    meshes = cmds.filterExpand(meshes, sm=12)
    filteredMeshes = []
    for mesh in meshes:
        # query all the nodes
        history = cmds.listHistory(mesh)
        # transform nodes into numbers
        numHistory = len(history)
        # Pair numbers with single mesh
        filteredMeshes.append([numHistory, mesh])
        # order minor to major
        filteredMeshes.sort()

    for mesh in filteredMeshes:
        cmds.select(mesh[1])
    cmds.pickWalk(d='down')


def printBlockingNodes():
    blockingTypes = cmds.evaluator(q=True, name="dynamics", valueName="disabledNodes")
    if len(blockingTypes) > 0:
        print(blockingTypes),
    else:
        cmds.warning('Nothing is blocking parallel')


def deleteOriginalRig():
    delete_SetNormal_FromMinorToHighHistory();
    cmds.delete('Set_Proxy', 'Excluded_Nodes')
    if cmds.objExists('Set_Normal'):
        cmds.delete('Set_Normal')


##### Poly Reduce multiple selection
def reducePoly(percentage=50):
    meshes = cmds.ls(sl=True)
    for mesh in meshes:
        if "_Proxy" in mesh:
            cmds.polyReduce(mesh, ver=1, trm=0, shp=0, keepBorder=1, keepMapBorder=1, keepColorBorder=1,
                            keepFaceGroupBorder=1, keepHardEdge=1, keepCreaseEdge=1, keepBorderWeight=0.5,
                            keepMapBorderWeight=0.5, keepColorBorderWeight=0.5, keepFaceGroupBorderWeight=0.5,
                            keepHardEdgeWeight=0.5, keepCreaseEdgeWeight=0.5, useVirtualSymmetry=0,
                            symmetryTolerance=0.01, sx=0, sy=1, sz=0, sw=0, preserveTopology=1, keepQuadsWeight=1,
                            vertexMapName="", cachingReduce=1, ch=1, p=percentage, vct=0, tct=0, replaceOriginal=1)
            cmds.BakeNonDefHistory(mesh)
        else:
            cmds.warning("This is not a proxy mesh")


##### Toggle node State
def toggleNodeState():
    nodes = cmds.ls(sl=True)
    if cmds.getAttr(nodes[0] + ".nodeState") == 1:
        value = 0
        for node in nodes:
            cmds.setAttr(node + ".nodeState", value)
            # cmds.setAttr (node + ".frozen", value)
            print(str(node) + " Turned On\n"),
    else:
        value = 1
        for node in nodes:
            cmds.setAttr(node + ".nodeState", value)
            # cmds.setAttr (node + ".frozen", value)
            print(str(node) + " Turned Off\n"),


##### Give me the Type
def giveMeTheType():
    selection = cmds.ls(sl=True)

    for obj in selection:
        objType = cmds.objectType(obj)

        print(str(obj) + " " + str(objType) + "\n"),


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
                    Toggle Proxy def
            
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''


# hide Or Show Proxy Set / 0 = visibile / 1 = unvisible
def hideorShowProxySet(value=0):
    if cmds.objExists("Folder_Proxys"):

        sel = cmds.ls(sl=True)
        cmds.select("Set_Proxy")
        allContentSetProxy = cmds.ls(sl=True)
        for proxy in allContentSetProxy:
            try:
                cmds.setAttr(proxy + ".visibility", value)
            except:
                cmds.setAttr(proxy + ".lodVisibility", value)

        createHUD()

        cmds.select(sel)
    else:
        cmds.warning("No proxys found")

        # Create HUD


def createHUD():
    try:
        if cmds.objExists('Folder_Proxys'):
            if cmds.headsUpDisplay("HUDProxy", exists=True, q=True) == 0:
                cmds.headsUpDisplay("HUDProxy", label="Proxy", labelFontSize="large", section=2, block=4)
            if cmds.getAttr("Folder_Proxys.visibility") == 1:
                cmds.headsUpDisplay("HUDProxy", edit=True, visible=1)
            else:
                cmds.headsUpDisplay("HUDProxy", edit=True, visible=0)

            # Check if Show proxy is on or off
            if cmds.checkBoxGrp("ShowProxy", query=True, value1=True):
                cmds.headsUpDisplay("HUDProxy", edit=True, label='Proxy')
            else:
                cmds.headsUpDisplay("HUDProxy", edit=True, label='Proxy (Hidden)')

        else:
            cmds.headsUpDisplay("HUDProxy", edit=True, visible=0)
    except:
        cmds.warning("Couldn't create HUD")

        # ShowProxy def


def showProxy():
    global Set_Normal, Excluded_Nodes, Set_Frozen
    sel = cmds.ls(sl=True)
    ###############
    if cmds.objExists(Set_Normal):
        cmds.select(Set_Normal)
    allContentSetNormal = cmds.ls(sl=True)

    for obj in allContentSetNormal:
        try:
            cmds.setAttr(obj + ".visibility", 0)
        except:
            cmds.setAttr(obj + ".lodVisibility", 0)
    ###############
    if cmds.objExists(Excluded_Nodes):
        cmds.select(Excluded_Nodes)
    allContentExcludedNodes = cmds.ls(sl=True)

    for obj in allContentExcludedNodes:
        try:
            cmds.setAttr(obj + ".nodeState", 1)
        except:
            pass

    ###############
    if cmds.objExists(Set_Frozen):
        cmds.select(Set_Frozen)
        allContentSetFrozen = cmds.ls(sl=True)

    if len(allContentSetFrozen) > 0:

        for obj in allContentSetFrozen:
            try:
                cmds.setAttr(obj + ".frozen", 1)
            except:
                pass
        # Downstream Freeze Mode = 'Always'
        cmds.freezeOptions(explicitPropagation=True)
        cmds.freezeOptions(downstream='force')
    ###############
    createHUD()
    cmds.select(sel)

    # HideProxy def


def hideProxy():
    global Set_Normal, Excluded_Nodes, Set_Frozen
    sel = cmds.ls(sl=True)
    ###############
    if cmds.objExists(Set_Normal):
        cmds.select(Set_Normal)

    allContentSetNormal = cmds.ls(sl=True)

    for obj in allContentSetNormal:
        try:
            cmds.setAttr(obj + ".visibility", 1)
        except:
            cmds.setAttr(obj + ".lodVisibility", 1)
    ###############
    if cmds.objExists(Excluded_Nodes):
        cmds.select(Excluded_Nodes)
    allContentExcludedNodes = cmds.ls(sl=True)

    for obj in allContentExcludedNodes:
        try:
            cmds.setAttr(obj + ".nodeState", 0)
        except:
            pass
    ###############
    if cmds.objExists(Set_Frozen):
        cmds.select(Set_Frozen)
        allContentSetFrozen = cmds.ls(sl=True)

        if len(allContentSetFrozen) > 0:

            for obj in allContentSetFrozen:
                try:
                    cmds.setAttr(obj + ".frozen", 0)
                except:
                    pass
            # Downstream Freeze Mode = 'Always'
            cmds.freezeOptions(explicitPropagation=False)
            cmds.freezeOptions(downstream='none')

    ###############
    createHUD()
    cmds.select(sel)


def toggleButton():
    global Set_Normal, Excluded_Nodes, FolderProxy, currentSelProxy, Set_Frozen
    # if there a Folder Proxy
    try:
        currentSelProxy = cmds.ls(sl=True)
        # if there is a proxy in the scene prioritize that one
        if cmds.objExists("Folder_Proxys"):
            FolderProxy = 'Folder_Proxys'
            Set_Normal = 'Set_Normal'
            Excluded_Nodes = 'Excluded_Nodes'
            Set_Frozen = 'Set_Frozen'
            toggleProxy()
            cmds.select(currentSelProxy)
        else:
            cmds.select("*:*Folder_Proxys")
            nFolderP = cmds.ls(sl=True)
            cmds.select(cl=True)
            # if there is more Folder proxys than one
            if len(nFolderP) > 1:
                getProxySelected()
                toggleProxy()
                cmds.select(currentSelProxy)
            else:
                FolderProxy = '*:*Folder_Proxys'
                Set_Normal = '*:*Set_Normal'
                Excluded_Nodes = '*:*Excluded_Nodes'
                Set_Frozen = '*:*Set_Frozen'
                toggleProxy()
                cmds.select(currentSelProxy)

    # If there isn't a Folder Proxy
    except:
        cmds.warning("No Proxys found\n")
        try:
            cmds.headsUpDisplay("HUDProxy", edit=True, visible=0)
        except:
            cmds.warning("No Proxys found\n"),


####################

def toggleProxy():
    global Set_Normal, Excluded_Nodes, Set_Frozen, FolderProxy
    createHUD()
    if cmds.getAttr(FolderProxy + ".visibility") == 1:
        # Normal mode

        cmds.refresh(suspend=True)

        cmds.setAttr(FolderProxy + ".visibility", 0)
        hideProxy()
        # Step foward and backward to avoid viewport bugs
        mel.eval('playButtonStepForward')
        mel.eval('playButtonStepBackward')

        cmds.refresh(suspend=False)

        print('Normal Mode'),
    else:
        # Proxymode

        cmds.refresh(suspend=True)

        cmds.setAttr(FolderProxy + ".visibility", 1)
        showProxy()
        # Step foward and backward to avoid viewport bugs
        mel.eval('playButtonStepForward')
        mel.eval('playButtonStepBackward')

        cmds.refresh(suspend=False)

        print('Proxy Mode'),


####################


def getProxySelected():
    global Set_Normal, Excluded_Nodes, FolderProxy, namespaceRef, Set_Frozen

    # If the current selection is more than one it look for a new proxy, if is not
    # it will switching between your last selection
    if len(currentSelProxy) > 0:
        # Query namespace
        namespaceRef = cmds.referenceQuery(currentSelProxy[0], referenceNode=True)
    # Transform to String
    namespaceRef = ''.join([str(elem) for elem in namespaceRef])
    # Remove RN and replace for :
    namespaceRef = namespaceRef.replace('RN', ':')
    # assigning new FolderProxy string
    FolderProxy = (namespaceRef + 'Folder_Proxys')
    # Assign Folder_Proxy, Set_Normal and Excluded_Nodes with the current Namespace Selected
    Set_Normal = (namespaceRef + 'Set_Normal')
    Excluded_Nodes = (namespaceRef + 'Excluded_Nodes')
    Set_Frozen = (namespaceRef + 'Set_Frozen')
    cmds.select(cl=True)


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
                    Tintero def
            
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
'''
# Turn off all animated expresion
for node in cmds.ls( type='expression' ):
    cmds.setAttr( '{}.animated'.format(node), 0 )

# Turn on invisibility evaluator
cmds.evaluator(enable=True, name='invisibility')

 

            # Create Set_Rig
def createSetRig(value = 0):
             
    if cmds.objExists ("Set_Rig"):
        cmds.select ("Set_Rig")
        try:
            cmds.setAttr (".visibility", value)
        except:
            cmds.setAttr (".lodVisibility", value)
        cmds.select (clear=True)
    else:
        test1 = cmds.ls (sl=True)
        if len(test1) >= 1:
                # This is a slow command that's why only create the set if the user wants it
                import pymel.core as pm
                root = pm.selected()[0].root()
                print root.name()
                pm.select (root)
                cmds.sets (name="Set_Rig")
                try:
                    cmds.setAttr (".visibility", value)
                except:
                    cmds.setAttr (".lodVisibility", value)
                cmds.select (clear=True)
        else:
            cmds.warning ("Select random element of the Rig")

'''

#########################
# Select the most complex mesh of the scene
'''
# get meshes
cmds.select('Set_Normal')
cmds.pickWalk (d='down')
meshes = cmds.ls ( sl=True)
# empty List
filteredMeshes = []

for mesh in meshes:
    
    # query all the nodes
    history = cmds.listHistory(mesh)
    # transform nodes into numbers
    numHistory = len(history)
    # Pair numbers with single mesh
    filteredMeshes.append([numHistory, mesh])
    # order minor to major
    filteredMeshes.sort()


# pick the last 5
for item in filteredMeshes:
    try:
        cmds.select(item[1])
    except:
        pass

'''

#########################
'''
# Freeze all content of a layerDisplay
# Es probable q tenga q activar el downstream force
cmds.freezeOptions( displayLayers=True )
# Freeze all content of a layerDisplay
cmds.freezeOptions( displayLayers=False )
'''

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            Shelf Buttons def
            
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''


def createShelfButton():
    mel.eval(
        "string $srcWindows=`asInstallScriptLocation`;\nstring $destWindows = `internalVar -userScriptDir`;\nstring $scriptIconFile = \"FCM_Proxy_Maker_Logo.png\";\n\n\nglobal string $gShelfTopLevel;\nstring $currentShelf = `tabLayout -query -selectTab $gShelfTopLevel`;\nsetParent $currentShelf;\nstring $icon=$destWindows+$scriptIconFile;\n\nsysFile -makeDir ($destWindows);\nsysFile -copy $icon ($srcWindows);\n\n    shelfButton\n        -enableCommandRepeat 1\n        -enable 1\n        -width 35\n        -height 35\n        -manage 1\n        -visible 1\n        -preventOverride 0\n        -annotation \"FCM_Proxy_Maker\" \n        -enableBackground 0\n        -highlightColor 0.321569 0.521569 0.65098 \n        -align \"center\" \n        -labelOffset 0\n        -rotation 0\n        -flipX 0\n        -flipY 0\n        -imageOverlayLabel \"Toggle\"\n        -useAlpha 1\n        -font \"plainLabelFont\" \n        -overlayLabelColor 0.8 0.8 0.8 \n        -overlayLabelBackColor 0 0 0 0.5 \n        -image \"absolute.png\" \n        -image1 \"absolute.png\" \n        -style \"iconOnly\" \n        -marginWidth 1\n        -marginHeight 1\n        -command \"try:\\n    toggleButton()\\nexcept:\\n    cmds.python(\\\"\\\\ndef toggleButton():\\\\n    global Set_Normal, Excluded_Nodes, FolderProxy, currentSelProxy, Set_Frozen\\\\n    # if there a Folder Proxy    \\\\n    try:\\\\n        currentSelProxy = cmds.ls (sl=True)\\\\n        # if there is a proxy in the scene prioritize that one\\\\n        if cmds.objExists (\\\\\\\"Folder_Proxys\\\\\\\"):\\\\n            FolderProxy = 'Folder_Proxys'\\\\n            Set_Normal = 'Set_Normal'\\\\n            Excluded_Nodes = 'Excluded_Nodes'\\\\n            Set_Frozen = 'Set_Frozen'\\\\n            toggleProxy()\\\\n            cmds.select (currentSelProxy) \\\\n        else:\\\\n            cmds.select (\\\\\\\"*:*Folder_Proxys\\\\\\\")\\\\n            nFolderP = cmds.ls (sl=True)\\\\n            cmds.select (cl=True)\\\\n            # if there is more Folder proxys than one \\\\n            if len(nFolderP) > 1:\\\\n                getProxySelected()\\\\n                toggleProxy()\\\\n                cmds.select (currentSelProxy)\\\\n            else:\\\\n                FolderProxy = '*:*Folder_Proxys'\\\\n                Set_Normal = '*:*Set_Normal'\\\\n                Excluded_Nodes = '*:*Excluded_Nodes'\\\\n                Set_Frozen = '*:*Set_Frozen'\\\\n                toggleProxy()\\\\n                cmds.select (currentSelProxy)\\\\n                \\\\n    # If there isn't a Folder Proxy      \\\\n    except:\\\\n        cmds.warning(\\\\\\\"No Proxys found\\\\\\\\n\\\\\\\")\\\\n        try:\\\\n            cmds.headsUpDisplay (\\\\\\\"HUDProxy\\\\\\\", edit=True, visible=0)\\\\n        except:\\\\n            cmds.warning(\\\\\\\"No Proxys found\\\\\\\\n\\\\\\\"),\\\\n            \\\\n            # ShowProxy def\\\\ndef showProxy():\\\\n    global Set_Normal, Excluded_Nodes, Set_Frozen\\\\n    sel = cmds.ls (sl=True)\\\\n    ###############\\\\n    if cmds.objExists (Set_Normal):\\\\n        cmds.select (Set_Normal)\\\\n    allContentSetNormal = cmds.ls (sl=True)\\\\n    \\\\n    for obj in allContentSetNormal:\\\\n        try:\\\\n            cmds.setAttr (obj + \\\\\\\".visibility\\\\\\\", 0)\\\\n        except:\\\\n            cmds.setAttr (obj + \\\\\\\".lodVisibility\\\\\\\", 0)\\\\n    ###############\\\\n    if cmds.objExists (Excluded_Nodes):\\\\n        cmds.select (Excluded_Nodes)\\\\n    allContentExcludedNodes = cmds.ls (sl=True)\\\\n    \\\\n    for obj in allContentExcludedNodes:\\\\n        try:\\\\n            cmds.setAttr (obj + \\\\\\\".nodeState\\\\\\\", 1)\\\\n        except:\\\\n            pass\\\\n\\\\n    ###############\\\\n    if cmds.objExists (Set_Frozen):\\\\n        cmds.select (Set_Frozen)\\\\n        allContentSetFrozen = cmds.ls(sl=True)\\\\n        \\\\n    if len(allContentSetFrozen) > 0:\\\\n    \\\\n        for obj in allContentSetFrozen:\\\\n            try:\\\\n                cmds.setAttr (obj + \\\\\\\".frozen\\\\\\\", 1)\\\\n            except:\\\\n                pass\\\\n        # Downstream Freeze Mode = 'Always'\\\\n        cmds.freezeOptions( explicitPropagation=True )\\\\n        cmds.freezeOptions( downstream='force' )\\\\n    ###############             \\\\n    createHUD()\\\\n    cmds.select (sel)\\\\n\\\\n            # HideProxy def\\\\ndef hideProxy():\\\\n    global Set_Normal, Excluded_Nodes, Set_Frozen\\\\n    sel = cmds.ls (sl=True)\\\\n    ###############\\\\n    if cmds.objExists (Set_Normal):\\\\n        cmds.select (Set_Normal)\\\\n    \\\\n    allContentSetNormal = cmds.ls (sl=True)\\\\n    \\\\n    for obj in allContentSetNormal:\\\\n        try:\\\\n            cmds.setAttr (obj + \\\\\\\".visibility\\\\\\\", 1)\\\\n        except:\\\\n            cmds.setAttr (obj + \\\\\\\".lodVisibility\\\\\\\", 1)\\\\n    ###############\\\\n    if cmds.objExists (Excluded_Nodes):\\\\n        cmds.select (Excluded_Nodes)\\\\n    allContentExcludedNodes = cmds.ls (sl=True)\\\\n    \\\\n    for obj in allContentExcludedNodes:\\\\n        try:\\\\n            cmds.setAttr (obj + \\\\\\\".nodeState\\\\\\\", 0)\\\\n        except:\\\\n            pass\\\\n    ###############\\\\n    if cmds.objExists (Set_Frozen):\\\\n        cmds.select (Set_Frozen)\\\\n        allContentSetFrozen = cmds.ls(sl=True)\\\\n        \\\\n        if len(allContentSetFrozen) > 0:\\\\n        \\\\n            for obj in allContentSetFrozen:\\\\n                try:\\\\n                    cmds.setAttr (obj + \\\\\\\".frozen\\\\\\\", 0)\\\\n                except:\\\\n                    pass\\\\n            # Downstream Freeze Mode = 'Always'\\\\n            cmds.freezeOptions( explicitPropagation=False )\\\\n            cmds.freezeOptions( downstream='none' )\\\\n\\\\n    ###############      \\\\n    createHUD()\\\\n    cmds.select (sel)\\\\n\\\\n####################\\\\n\\\\ndef toggleProxy():\\\\n    global Set_Normal, Excluded_Nodes, Set_Frozen, FolderProxy\\\\n    createHUD()\\\\n    if cmds.getAttr ( FolderProxy + \\\\\\\".visibility\\\\\\\") == 1:  \\\\n                    # Normal mode\\\\n        \\\\n        cmds.refresh(suspend=True)\\\\n        \\\\n        cmds.setAttr ( FolderProxy + \\\\\\\".visibility\\\\\\\", 0)\\\\n        hideProxy()\\\\n        # Step foward and backward to avoid viewport bugs\\\\n        mel.eval ('playButtonStepForward')\\\\n        mel.eval ('playButtonStepBackward')\\\\n        \\\\n        cmds.refresh(suspend=False)\\\\n        \\\\n        print ('Normal Mode'),\\\\n    else:\\\\n                    # Proxymode\\\\n        \\\\n        cmds.refresh(suspend=True)\\\\n        \\\\n        cmds.setAttr (FolderProxy + \\\\\\\".visibility\\\\\\\", 1)\\\\n        showProxy()\\\\n        # Step foward and backward to avoid viewport bugs\\\\n        mel.eval ('playButtonStepForward')\\\\n        mel.eval ('playButtonStepBackward')\\\\n        \\\\n        cmds.refresh(suspend=False)\\\\n        \\\\n        print ('Proxy Mode'),\\\\n           \\\\n####################\\\\n     \\\\ndef getProxySelected():\\\\n    global Set_Normal, Excluded_Nodes, FolderProxy, namespaceRef, Set_Frozen\\\\n    \\\\n    # If the current selection is more than one it look for a new proxy, if is not\\\\n    # it will switching between your last selection\\\\n    if len(currentSelProxy) > 0:\\\\n        # Query namespace\\\\n        namespaceRef = cmds.referenceQuery( currentSelProxy[0], referenceNode=True )\\\\n    # Transform to String\\\\n    namespaceRef = ''.join([str(elem) for elem in namespaceRef]) \\\\n    # Remove RN and replace for :\\\\n    namespaceRef = namespaceRef.replace('RN', ':')\\\\n    # assigning new FolderProxy string\\\\n    FolderProxy = (namespaceRef + 'Folder_Proxys')\\\\n    # Assign Folder_Proxy, Set_Normal and Excluded_Nodes with the current Namespace Selected\\\\n    Set_Normal = ( namespaceRef + 'Set_Normal')\\\\n    Excluded_Nodes = ( namespaceRef + 'Excluded_Nodes')\\\\n    Set_Frozen = ( namespaceRef + 'Set_Frozen')\\\\n    cmds.select (cl=True)\\\\n    \\\\n####################\\\\n\\\\ndef createHUD():\\\\n    try:\\\\n        if cmds.objExists('Folder_Proxys'):\\\\n            if cmds.headsUpDisplay (\\\\\\\"HUDProxy\\\\\\\", exists=True, q=True) == 0:\\\\n                cmds.headsUpDisplay (\\\\\\\"HUDProxy\\\\\\\", label=\\\\\\\"Proxy\\\\\\\", labelFontSize=\\\\\\\"large\\\\\\\", section=2, block=4)\\\\n            if cmds.getAttr (\\\\\\\"Folder_Proxys.visibility\\\\\\\") == 1:\\\\n                cmds.headsUpDisplay (\\\\\\\"HUDProxy\\\\\\\", edit=True, visible=1)\\\\n            else:\\\\n                cmds.headsUpDisplay (\\\\\\\"HUDProxy\\\\\\\", edit=True, visible=0)\\\\n        else:\\\\n            cmds.headsUpDisplay (\\\\\\\"HUDProxy\\\\\\\", edit=True, visible=0)        \\\\n    except:\\\\n        cmds.warning (\\\\\\\"Couldn't create HUD\\\\\\\")\\\")\\n    toggleButton()\"  \n        -sourceType \"python\" \n        -commandRepeatable 1\n        -flat 1\n    ;\n\nglobal proc asInstallScriptFCMHider(){}\n\nglobal proc string asInstallScriptLocation ()\n{\nstring $whatIs=`whatIs asInstallScriptFCMHider`;\nstring $fullPath=`substring $whatIs 25 999`;\nstring $buffer[];\nint $numTok=`tokenize $fullPath \"/\" $buffer`;\nint $numLetters=size($fullPath);\nint $numLettersLastFolder=size($buffer[$numTok-1]);\nstring $scriptLocation=`substring $fullPath 1 ($numLetters-$numLettersLastFolder)`;\nreturn $scriptLocation;\n}\n\n\n\n")
    print('Shelf Button Added'),


''' # Current Method: It needs to be written in Python
string $srcWindows=`asInstallScriptLocation`;
string $destWindows = `internalVar -userScriptDir`;
string $scriptIconFile = "FCM_Proxy_Maker_Logo.png";


global string $gShelfTopLevel;
string $currentShelf = `tabLayout -query -selectTab $gShelfTopLevel`;
setParent $currentShelf;
string $icon=$destWindows+$scriptIconFile;

sysFile -makeDir ($destWindows);
sysFile -copy $icon ($srcWindows);

    shelfButton
        -enableCommandRepeat 1
        -enable 1
        -width 35
        -height 35
        -manage 1
        -visible 1
        -preventOverride 0
        -annotation "FCM_Proxy_Maker" 
        -enableBackground 0
        -highlightColor 0.321569 0.521569 0.65098 
        -align "center" 
        -labelOffset 0
        -rotation 0
        -flipX 0
        -flipY 0
        -imageOverlayLabel "Toggle"
        -useAlpha 1
        -font "plainLabelFont" 
        -overlayLabelColor 0.8 0.8 0.8 
        -overlayLabelBackColor 0 0 0 0.5 
        -image "absolute.png" 
        -image1 "absolute.png" 
        -style "iconOnly" 
        -marginWidth 1
        -marginHeight 1
        -command "try:\n    toggleButton()\nexcept:\n    cmds.python(\"\\ndef toggleButton():\\n    global Set_Normal, Excluded_Nodes, FolderProxy, currentSelProxy, Set_Frozen\\n    # if there a Folder Proxy    \\n    try:\\n        currentSelProxy = cmds.ls (sl=True)\\n        # if there is a proxy in the scene prioritize that one\\n        if cmds.objExists (\\\"Folder_Proxys\\\"):\\n            FolderProxy = 'Folder_Proxys'\\n            Set_Normal = 'Set_Normal'\\n            Excluded_Nodes = 'Excluded_Nodes'\\n            Set_Frozen = 'Set_Frozen'\\n            toggleProxy()\\n            cmds.select (currentSelProxy) \\n        else:\\n            cmds.select (\\\"*:*Folder_Proxys\\\")\\n            nFolderP = cmds.ls (sl=True)\\n            cmds.select (cl=True)\\n            # if there is more Folder proxys than one \\n            if len(nFolderP) > 1:\\n                getProxySelected()\\n                toggleProxy()\\n                cmds.select (currentSelProxy)\\n            else:\\n                FolderProxy = '*:*Folder_Proxys'\\n                Set_Normal = '*:*Set_Normal'\\n                Excluded_Nodes = '*:*Excluded_Nodes'\\n                Set_Frozen = '*:*Set_Frozen'\\n                toggleProxy()\\n                cmds.select (currentSelProxy)\\n                \\n    # If there isn't a Folder Proxy      \\n    except:\\n        cmds.warning(\\\"No Proxys found\\\\n\\\")\\n        try:\\n            cmds.headsUpDisplay (\\\"HUDProxy\\\", edit=True, visible=0)\\n        except:\\n            cmds.warning(\\\"No Proxys found\\\\n\\\"),\\n            \\n            # ShowProxy def\\ndef showProxy():\\n    global Set_Normal, Excluded_Nodes, Set_Frozen\\n    sel = cmds.ls (sl=True)\\n    ###############\\n    if cmds.objExists (Set_Normal):\\n        cmds.select (Set_Normal)\\n    allContentSetNormal = cmds.ls (sl=True)\\n    \\n    for obj in allContentSetNormal:\\n        try:\\n            cmds.setAttr (obj + \\\".visibility\\\", 0)\\n        except:\\n            cmds.setAttr (obj + \\\".lodVisibility\\\", 0)\\n    ###############\\n    if cmds.objExists (Excluded_Nodes):\\n        cmds.select (Excluded_Nodes)\\n    allContentExcludedNodes = cmds.ls (sl=True)\\n    \\n    for obj in allContentExcludedNodes:\\n        try:\\n            cmds.setAttr (obj + \\\".nodeState\\\", 1)\\n        except:\\n            pass\\n\\n    ###############\\n    if cmds.objExists (Set_Frozen):\\n        cmds.select (Set_Frozen)\\n        allContentSetFrozen = cmds.ls(sl=True)\\n        \\n    if len(allContentSetFrozen) > 0:\\n    \\n        for obj in allContentSetFrozen:\\n            try:\\n                cmds.setAttr (obj + \\\".frozen\\\", 1)\\n            except:\\n                pass\\n        # Downstream Freeze Mode = 'Always'\\n        cmds.freezeOptions( explicitPropagation=True )\\n        cmds.freezeOptions( downstream='force' )\\n    ###############             \\n    createHUD()\\n    cmds.select (sel)\\n\\n            # HideProxy def\\ndef hideProxy():\\n    global Set_Normal, Excluded_Nodes, Set_Frozen\\n    sel = cmds.ls (sl=True)\\n    ###############\\n    if cmds.objExists (Set_Normal):\\n        cmds.select (Set_Normal)\\n    \\n    allContentSetNormal = cmds.ls (sl=True)\\n    \\n    for obj in allContentSetNormal:\\n        try:\\n            cmds.setAttr (obj + \\\".visibility\\\", 1)\\n        except:\\n            cmds.setAttr (obj + \\\".lodVisibility\\\", 1)\\n    ###############\\n    if cmds.objExists (Excluded_Nodes):\\n        cmds.select (Excluded_Nodes)\\n    allContentExcludedNodes = cmds.ls (sl=True)\\n    \\n    for obj in allContentExcludedNodes:\\n        try:\\n            cmds.setAttr (obj + \\\".nodeState\\\", 0)\\n        except:\\n            pass\\n    ###############\\n    if cmds.objExists (Set_Frozen):\\n        cmds.select (Set_Frozen)\\n        allContentSetFrozen = cmds.ls(sl=True)\\n        \\n        if len(allContentSetFrozen) > 0:\\n        \\n            for obj in allContentSetFrozen:\\n                try:\\n                    cmds.setAttr (obj + \\\".frozen\\\", 0)\\n                except:\\n                    pass\\n            # Downstream Freeze Mode = 'Always'\\n            cmds.freezeOptions( explicitPropagation=False )\\n            cmds.freezeOptions( downstream='none' )\\n\\n    ###############      \\n    createHUD()\\n    cmds.select (sel)\\n\\n####################\\n\\ndef toggleProxy():\\n    global Set_Normal, Excluded_Nodes, Set_Frozen, FolderProxy\\n    createHUD()\\n    if cmds.getAttr ( FolderProxy + \\\".visibility\\\") == 1:  \\n                    # Normal mode\\n        \\n        cmds.refresh(suspend=True)\\n        \\n        cmds.setAttr ( FolderProxy + \\\".visibility\\\", 0)\\n        hideProxy()\\n        # Step foward and backward to avoid viewport bugs\\n        mel.eval ('playButtonStepForward')\\n        mel.eval ('playButtonStepBackward')\\n        \\n        cmds.refresh(suspend=False)\\n        \\n        print ('Normal Mode'),\\n    else:\\n                    # Proxymode\\n        \\n        cmds.refresh(suspend=True)\\n        \\n        cmds.setAttr (FolderProxy + \\\".visibility\\\", 1)\\n        showProxy()\\n        # Step foward and backward to avoid viewport bugs\\n        mel.eval ('playButtonStepForward')\\n        mel.eval ('playButtonStepBackward')\\n        \\n        cmds.refresh(suspend=False)\\n        \\n        print ('Proxy Mode'),\\n           \\n####################\\n     \\ndef getProxySelected():\\n    global Set_Normal, Excluded_Nodes, FolderProxy, namespaceRef, Set_Frozen\\n    \\n    # If the current selection is more than one it look for a new proxy, if is not\\n    # it will switching between your last selection\\n    if len(currentSelProxy) > 0:\\n        # Query namespace\\n        namespaceRef = cmds.referenceQuery( currentSelProxy[0], referenceNode=True )\\n    # Transform to String\\n    namespaceRef = ''.join([str(elem) for elem in namespaceRef]) \\n    # Remove RN and replace for :\\n    namespaceRef = namespaceRef.replace('RN', ':')\\n    # assigning new FolderProxy string\\n    FolderProxy = (namespaceRef + 'Folder_Proxys')\\n    # Assign Folder_Proxy, Set_Normal and Excluded_Nodes with the current Namespace Selected\\n    Set_Normal = ( namespaceRef + 'Set_Normal')\\n    Excluded_Nodes = ( namespaceRef + 'Excluded_Nodes')\\n    Set_Frozen = ( namespaceRef + 'Set_Frozen')\\n    cmds.select (cl=True)\\n    \\n####################\\n\\ndef createHUD():\\n    try:\\n        if cmds.objExists('Folder_Proxys'):\\n            if cmds.headsUpDisplay (\\\"HUDProxy\\\", exists=True, q=True) == 0:\\n                cmds.headsUpDisplay (\\\"HUDProxy\\\", label=\\\"Proxy\\\", labelFontSize=\\\"large\\\", section=2, block=4)\\n            if cmds.getAttr (\\\"Folder_Proxys.visibility\\\") == 1:\\n                cmds.headsUpDisplay (\\\"HUDProxy\\\", edit=True, visible=1)\\n            else:\\n                cmds.headsUpDisplay (\\\"HUDProxy\\\", edit=True, visible=0)\\n        else:\\n            cmds.headsUpDisplay (\\\"HUDProxy\\\", edit=True, visible=0)        \\n    except:\\n        cmds.warning (\\\"Couldn't create HUD\\\")\")\n    toggleButton()"  
        -sourceType "python" 
        -commandRepeatable 1
        -flat 1
    ;

global proc asInstallScriptFCMHider(){}

global proc string asInstallScriptLocation ()
{
string $whatIs=`whatIs asInstallScriptFCMHider`;
string $fullPath=`substring $whatIs 25 999`;
string $buffer[];
int $numTok=`tokenize $fullPath "/" $buffer`;
int $numLetters=size($fullPath);
int $numLettersLastFolder=size($buffer[$numTok-1]);
string $scriptLocation=`substring $fullPath 1 ($numLetters-$numLettersLastFolder)`;
return $scriptLocation;
}
'''
##############################
''' # Old Method: is in python but create a new shelf tab instead of adding it in the current shelf
shelfName='Proxy_Maker'
mel.eval('global string $gShelfTopLevel;')
mainShelfLayout=mel.eval('$tmp=$gShelfTopLevel;')
if cmds.shelfLayout(shelfName,exists=True):
    mel.eval('deleteShelfTab "%s";' % shelfName)
#add new tab
createdShelf=mel.eval('addNewShelfTab "%s";'%shelfName)
cmds.shelfButton(
    image1='commandButton.png', imageOverlayLabel='Toggle',
    c="try:\n    toggleButton()\nexcept:\n    cmds.python(\"\\ndef toggleButton():\\n    global Set_Normal, Excluded_Nodes, FolderProxy, currentSelProxy, Set_Frozen\\n    # if there a Folder Proxy    \\n    try:\\n        currentSelProxy = cmds.ls (sl=True)\\n        # if there is a proxy in the scene prioritize that one\\n        if cmds.objExists (\\\"Folder_Proxys\\\"):\\n            FolderProxy = 'Folder_Proxys'\\n            Set_Normal = 'Set_Normal'\\n            Excluded_Nodes = 'Excluded_Nodes'\\n            Set_Frozen = 'Set_Frozen'\\n            toggleProxy()\\n            cmds.select (currentSelProxy) \\n        else:\\n            cmds.select (\\\"*:*Folder_Proxys\\\")\\n            nFolderP = cmds.ls (sl=True)\\n            cmds.select (cl=True)\\n            # if there is more Folder proxys than one \\n            if len(nFolderP) > 1:\\n                getProxySelected()\\n                toggleProxy()\\n                cmds.select (currentSelProxy)\\n            else:\\n                FolderProxy = '*:*Folder_Proxys'\\n                Set_Normal = '*:*Set_Normal'\\n                Excluded_Nodes = '*:*Excluded_Nodes'\\n                Set_Frozen = '*:*Set_Frozen'\\n                toggleProxy()\\n                cmds.select (currentSelProxy)\\n                \\n    # If there isn't a Folder Proxy      \\n    except:\\n        cmds.warning(\\\"No Proxys found\\\\n\\\")\\n        try:\\n            cmds.headsUpDisplay (\\\"HUDProxy\\\", edit=True, visible=0)\\n        except:\\n            cmds.warning(\\\"No Proxys found\\\\n\\\"),\\n            \\n            # ShowProxy def\\ndef showProxy():\\n    global Set_Normal, Excluded_Nodes, Set_Frozen\\n    sel = cmds.ls (sl=True)\\n    ###############\\n    if cmds.objExists (Set_Normal):\\n        cmds.select (Set_Normal)\\n    allContentSetNormal = cmds.ls (sl=True)\\n    \\n    for obj in allContentSetNormal:\\n        try:\\n            cmds.setAttr (obj + \\\".visibility\\\", 0)\\n        except:\\n            cmds.setAttr (obj + \\\".lodVisibility\\\", 0)\\n    ###############\\n    if cmds.objExists (Excluded_Nodes):\\n        cmds.select (Excluded_Nodes)\\n    allContentExcludedNodes = cmds.ls (sl=True)\\n    \\n    for obj in allContentExcludedNodes:\\n        try:\\n            cmds.setAttr (obj + \\\".nodeState\\\", 1)\\n        except:\\n            pass\\n\\n    ###############\\n    if cmds.objExists (Set_Frozen):\\n        cmds.select (Set_Frozen)\\n        allContentSetFrozen = cmds.ls(sl=True)\\n        \\n    if len(allContentSetFrozen) > 0:\\n    \\n        for obj in allContentSetFrozen:\\n            try:\\n                cmds.setAttr (obj + \\\".frozen\\\", 1)\\n            except:\\n                pass\\n        # Downstream Freeze Mode = 'Always'\\n        cmds.freezeOptions( explicitPropagation=True )\\n        cmds.freezeOptions( downstream='force' )\\n    ###############             \\n    createHUD()\\n    cmds.select (sel)\\n\\n            # HideProxy def\\ndef hideProxy():\\n    global Set_Normal, Excluded_Nodes, Set_Frozen\\n    sel = cmds.ls (sl=True)\\n    ###############\\n    if cmds.objExists (Set_Normal):\\n        cmds.select (Set_Normal)\\n    \\n    allContentSetNormal = cmds.ls (sl=True)\\n    \\n    for obj in allContentSetNormal:\\n        try:\\n            cmds.setAttr (obj + \\\".visibility\\\", 1)\\n        except:\\n            cmds.setAttr (obj + \\\".lodVisibility\\\", 1)\\n    ###############\\n    if cmds.objExists (Excluded_Nodes):\\n        cmds.select (Excluded_Nodes)\\n    allContentExcludedNodes = cmds.ls (sl=True)\\n    \\n    for obj in allContentExcludedNodes:\\n        try:\\n            cmds.setAttr (obj + \\\".nodeState\\\", 0)\\n        except:\\n            pass\\n    ###############\\n    if cmds.objExists (Set_Frozen):\\n        cmds.select (Set_Frozen)\\n        allContentSetFrozen = cmds.ls(sl=True)\\n        \\n        if len(allContentSetFrozen) > 0:\\n        \\n            for obj in allContentSetFrozen:\\n                try:\\n                    cmds.setAttr (obj + \\\".frozen\\\", 0)\\n                except:\\n                    pass\\n            # Downstream Freeze Mode = 'Always'\\n            cmds.freezeOptions( explicitPropagation=False )\\n            cmds.freezeOptions( downstream='none' )\\n\\n    ###############      \\n    createHUD()\\n    cmds.select (sel)\\n\\n####################\\n\\ndef toggleProxy():\\n    global Set_Normal, Excluded_Nodes, Set_Frozen, FolderProxy\\n    createHUD()\\n    if cmds.getAttr ( FolderProxy + \\\".visibility\\\") == 1:  \\n                    # Normal mode\\n        \\n        cmds.refresh(suspend=True)\\n        \\n        cmds.setAttr ( FolderProxy + \\\".visibility\\\", 0)\\n        hideProxy()\\n        # Step foward and backward to avoid viewport bugs\\n        mel.eval ('playButtonStepForward')\\n        mel.eval ('playButtonStepBackward')\\n        \\n        cmds.refresh(suspend=False)\\n        \\n        print ('Normal Mode'),\\n    else:\\n                    # Proxymode\\n        \\n        cmds.refresh(suspend=True)\\n        \\n        cmds.setAttr (FolderProxy + \\\".visibility\\\", 1)\\n        showProxy()\\n        # Step foward and backward to avoid viewport bugs\\n        mel.eval ('playButtonStepForward')\\n        mel.eval ('playButtonStepBackward')\\n        \\n        cmds.refresh(suspend=False)\\n        \\n        print ('Proxy Mode'),\\n           \\n####################\\n     \\ndef getProxySelected():\\n    global Set_Normal, Excluded_Nodes, FolderProxy, namespaceRef, Set_Frozen\\n    \\n    # If the current selection is more than one it look for a new proxy, if is not\\n    # it will switching between your last selection\\n    if len(currentSelProxy) > 0:\\n        # Query namespace\\n        namespaceRef = cmds.referenceQuery( currentSelProxy[0], referenceNode=True )\\n    # Transform to String\\n    namespaceRef = ''.join([str(elem) for elem in namespaceRef]) \\n    # Remove RN and replace for :\\n    namespaceRef = namespaceRef.replace('RN', ':')\\n    # assigning new FolderProxy string\\n    FolderProxy = (namespaceRef + 'Folder_Proxys')\\n    # Assign Folder_Proxy, Set_Normal and Excluded_Nodes with the current Namespace Selected\\n    Set_Normal = ( namespaceRef + 'Set_Normal')\\n    Excluded_Nodes = ( namespaceRef + 'Excluded_Nodes')\\n    Set_Frozen = ( namespaceRef + 'Set_Frozen')\\n    cmds.select (cl=True)\\n    \\n####################\\n\\ndef createHUD():\\n    try:\\n        if cmds.objExists('Folder_Proxys'):\\n            if cmds.headsUpDisplay (\\\"HUDProxy\\\", exists=True, q=True) == 0:\\n                cmds.headsUpDisplay (\\\"HUDProxy\\\", label=\\\"Proxy\\\", labelFontSize=\\\"large\\\", section=2, block=4)\\n            if cmds.getAttr (\\\"Folder_Proxys.visibility\\\") == 1:\\n                cmds.headsUpDisplay (\\\"HUDProxy\\\", edit=True, visible=1)\\n            else:\\n                cmds.headsUpDisplay (\\\"HUDProxy\\\", edit=True, visible=0)\\n        else:\\n            cmds.headsUpDisplay (\\\"HUDProxy\\\", edit=True, visible=0)        \\n    except:\\n        cmds.warning (\\\"Couldn't create HUD\\\")\")\n    toggleButton()"  ,
    parent=createdShelf 
    )
'''

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            Settings def
            
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''


# Create Group with settings by default
def createSettings():
    if cmds.objExists('FCM_Proxy_Maker_Settings') == 0:
        sel = cmds.ls(sl=True)
        cmds.group(em=True, n='FCM_Proxy_Maker_Settings')
        cmds.setAttr(".tx", lock=True, keyable=False, channelBox=False)
        cmds.setAttr(".ty", lock=True, keyable=False, channelBox=False)
        cmds.setAttr(".tz", lock=True, keyable=False, channelBox=False)
        cmds.setAttr(".rx", lock=True, keyable=False, channelBox=False)
        cmds.setAttr(".ry", lock=True, keyable=False, channelBox=False)
        cmds.setAttr(".rz", lock=True, keyable=False, channelBox=False)
        cmds.setAttr(".sx", lock=True, keyable=False, channelBox=False)
        cmds.setAttr(".sy", lock=True, keyable=False, channelBox=False)
        cmds.setAttr(".sz", lock=True, keyable=False, channelBox=False)
        cmds.setAttr(".v", lock=True, keyable=False, channelBox=False)
        # Create Option 1 Vis
        cmds.addAttr('FCM_Proxy_Maker_Settings', ln='Option_1_Vis', at='bool', dv=True, keyable=True)
        # Create Option 2 Vis
        cmds.addAttr('FCM_Proxy_Maker_Settings', ln='Option_2_Vis', at='bool', dv=False, keyable=True)
        # Create Deform Manager Vis
        cmds.addAttr('FCM_Proxy_Maker_Settings', ln='deformManager_Vis', at='bool', dv=False, keyable=True)
        # Create Save After Loading
        cmds.addAttr('FCM_Proxy_Maker_Settings', ln='Save_After_Loading', at='bool', dv=False, keyable=True)

        # Sanity Check
        cmds.addAttr('FCM_Proxy_Maker_Settings', ln='sanityCheck_FrameRate', at='enum', en="Waiting:Answered",
                     keyable=True)
        cmds.addAttr('FCM_Proxy_Maker_Settings', ln='sanityCheck_SmoothMeshPreview', at='enum', en="Waiting:Answered",
                     keyable=True)
        cmds.addAttr('FCM_Proxy_Maker_Settings', ln='sanityCheck_UpdateView', at='enum', en="Waiting:Answered",
                     keyable=True)
        # Deform manager
        cmds.addAttr('FCM_Proxy_Maker_Settings', ln='HeavyMeshConnected_State', at='bool', dv=True, keyable=True)
        cmds.addAttr('FCM_Proxy_Maker_Settings', ln='blendShape_State', at='bool', dv=True, keyable=True)
        cmds.addAttr('FCM_Proxy_Maker_Settings', ln='wire_State', at='bool', dv=True, keyable=True)
        cmds.addAttr('FCM_Proxy_Maker_Settings', ln='wrap_State', at='bool', dv=True, keyable=True)
        cmds.addAttr('FCM_Proxy_Maker_Settings', ln='polySmoothFace_State', at='bool', dv=True, keyable=True)
        cmds.addAttr('FCM_Proxy_Maker_Settings', ln='deltaMush_State', at='bool', dv=True, keyable=True)
        cmds.addAttr('FCM_Proxy_Maker_Settings', ln='ffd_State', at='bool', dv=True, keyable=True)
        cmds.addAttr('FCM_Proxy_Maker_Settings', ln='tension_State', at='bool', dv=True, keyable=True)
        cmds.addAttr('FCM_Proxy_Maker_Settings', ln='polySoftEdge_State', at='bool', dv=True, keyable=True)
        cmds.addAttr('FCM_Proxy_Maker_Settings', ln='polyMapCut_State', at='bool', dv=True, keyable=True)
        cmds.addAttr('FCM_Proxy_Maker_Settings', ln='polyTweakUV_State', at='bool', dv=True, keyable=True)
        cmds.addAttr('FCM_Proxy_Maker_Settings', ln='polyPlanarProj_State', at='bool', dv=True, keyable=True)
        cmds.addAttr('FCM_Proxy_Maker_Settings', ln='skinCluster_State', at='bool', dv=True, keyable=True)
        cmds.addAttr('FCM_Proxy_Maker_Settings', ln='cluster_State', at='bool', dv=True, keyable=True)

        cmds.select(sel)


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            Create Groups and Sets def
            
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''


def createGroupsAndSets():
    if cmds.objExists("Folder_Proxys") == 0:
        cmds.group(em=True, name="Folder_Proxys")
        cmds.select(cl=True)
    if cmds.objExists("Set_Normal") == 0:
        cmds.sets(em=True, name="Set_Normal")
        cmds.select(cl=True)
    if cmds.objExists("Excluded_Nodes") == 0:
        cmds.sets(em=True, name="Excluded_Nodes")
        cmds.select(cl=True)
    if cmds.objExists("Set_Proxy") == 0:
        cmds.sets(em=True, name="Set_Proxy")
        cmds.select(cl=True)
    if cmds.objExists("Set_Frozen") == 0:
        cmds.sets(em=True, name="Set_Frozen")
        cmds.select(cl=True)


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            Sanity Check def
            
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''


def sanityCheck():
    sanityCheckFrameRate()
    sanityCheckEvaluationMode()
    sanityCheckSmoothMeshPreview()
    sanityCheckUpdateView()


# ====##====##====##====#
def sanityCheckUpdateView():
    # If is waiting
    if cmds.getAttr("FCM_Proxy_Maker_Settings.sanityCheck_UpdateView") == 0:
        if cmds.playbackOptions(q=True, v=True) == "all":
            result = cmds.confirmDialog(title='Sanity check Update View',
                                        message="Update View is set as \"All\"\n\nI have two reason for setting it as \"Active\":\n-You can earn more FPS\n-You will fix an awful bug for the FPS HUD\n\nThis will only update your current viewport\n\nDo you want to switch to \"Active\"?",
                                        button=['Yes', 'No'], cancelButton='No')

            if result == 'Yes':
                cmds.playbackOptions(v='active')
                cmds.checkBoxGrp("HUDFrameRate", edit=True, value2=True)
                print('Update view set to "Active"'),
            # Save response
            cmds.setAttr("FCM_Proxy_Maker_Settings.sanityCheck_UpdateView", 1)


# ====##====##====##====#
# WIP!
# haciendo un segundo checkeo si no pudo switchear a parallel
# todavia necesita crear un atributo que checkee si esto fue asi tiene q hacer por cada session
# el cambio a evaluation mode everything


def sanityCheckEvaluationMode():
    # if is true is in DG
    if cmds.evaluationManager(q=True, enabled=True) == 0:
        result = cmds.confirmDialog(title='Sanity check Evaluation Mode',
                                    message='Evaluation mode is in "DG"\nAll the rigs usually works much faster with this tool in "Parallel" Evaluation\nDo you want to switch to Parallel?',
                                    button=['Yes', 'No'], cancelButton='No')

        if result == 'Yes':
            cmds.evaluationManager(mode='parallel')
            print('Evaluation mode set to "Parallel"'),
            ################################################
            # If there is something that disable parallel it will pop up another confirm dialog
            if cmds.evaluationManager(q=True, enabled=True) == 0:
                result = cmds.confirmDialog(title="Evaluation Mode can't change to parallel",
                                            message='Probably some node or expresion is blocking parallel evaluation\nThis setting can make unstable the maya session. But give it a try!\nDo you want to switch to parallel?\n',
                                            button=['Yes!', 'Nop, I am not that kind of adventurous person'],
                                            cancelButton='No')

                if result == 'Yes!':
                    setDynamicsMode_To_Everything()
                    # Save response
                if result == 'Nop, I am not that kind of adventurous person':
                    pass
                    # Save response


def setDynamicsMode_To_Everything():
    cmds.evaluator(name='dynamics', c="disablingNodes=none")
    cmds.evaluator(name='dynamics', c="handledNodes=dynamics")
    cmds.evaluator(name='dynamics', c="action=evaluate")


# ====##====##====##====#
# Check if some mesh in the scene has active the smooth mesh preview
def sanityCheckSmoothMeshPreview():
    if cmds.getAttr("FCM_Proxy_Maker_Settings.sanityCheck_SmoothMeshPreview") == 0:
        allShapeMeshes = cmds.ls(type="mesh")
        for mesh in allShapeMeshes:
            if cmds.getAttr(mesh + ".displaySmoothMesh") == 2:
                if cmds.getAttr(mesh + ".smoothLevel") == 1:
                    pass
                else:
                    result = cmds.confirmDialog(title='Sanity check Smooth Mesh Preview', message=(str(
                        mesh) + ' has smooth mesh preview on with subdivision level 2\nThis may slowdown your playback, do you want to turn it off?'),
                                                button=['Yes to all', 'No to all', 'Yes', 'No'], cancelButton='No')

                    if result == 'Yes':
                        cmds.setAttr(mesh + ".displaySmoothMesh", 0)
                        print((str(mesh) + ' Smooth Mesh preview turned Off')),
                    if result == 'Yes to all':
                        # Aca necesita meter en lista todos los meshes q esten con sub level 2 o 3 pero no 1
                        for mesh in allShapeMeshes:
                            cmds.setAttr(mesh + ".displaySmoothMesh", 0)
                    if result == 'No to all':
                        # Save response
                        cmds.setAttr("FCM_Proxy_Maker_Settings.sanityCheck_SmoothMeshPreview", 1)
                        sys.exit('user cancelled')
                    # Save response
                    cmds.setAttr("FCM_Proxy_Maker_Settings.sanityCheck_SmoothMeshPreview", 1)


# ====##====##====##====#
# Check if FPS hud display is active
def sanityCheckFrameRate():
    if cmds.getAttr("FCM_Proxy_Maker_Settings.sanityCheck_FrameRate") == 0:
        if mel.eval('optionVar -q frameRateVisibility') == 0:
            result = cmds.confirmDialog(title='Sanity check FCM_Proxy_Maker',
                                        message='FPS HUD visibility is OFF\nThis is a useful function for testing the speed plaback of your rig\nDo you want to turn it on?',
                                        button=['Yes', 'No'], cancelButton='No')

            if result == 'Yes':
                mel.eval('setFrameRateVisibility 1')
                cmds.checkBoxGrp("HUDFrameRate", edit=True, value1=True)
                print('FPS HUD active'),
                # Save response
            cmds.setAttr("FCM_Proxy_Maker_Settings.sanityCheck_FrameRate", 1)


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
                    Deform Manager Functions
            
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''


# This function needs declare variables before run, they declare in the button just before run the function
def turnonOrOffAllDeform():
    global nodeName
    # Checkboxes
    cmds.checkBoxGrp('NodesCheckbox1', edit=True, value1=TrueOrFalse, value2=TrueOrFalse, value3=TrueOrFalse)
    cmds.checkBoxGrp('NodesCheckbox2', edit=True, value1=TrueOrFalse, value2=TrueOrFalse, value3=TrueOrFalse)
    cmds.checkBoxGrp('NodesCheckbox3', edit=True, value1=TrueOrFalse, value2=TrueOrFalse, value3=TrueOrFalse)
    cmds.checkBoxGrp('NodesCheckbox4', edit=True, value1=TrueOrFalse, value2=TrueOrFalse, value3=TrueOrFalse)
    # cmds.checkBoxGrp ('NodesCheckbox5', edit=True, value1=TrueOrFalse)
    # Heavy Meshes

    # Turn off nodes
    nodeName = 'blendShape';
    nodesOnorOff()
    nodeName = 'wrap';
    nodesOnorOff()
    nodeName = 'polySmoothFace';
    nodesOnorOff()
    nodeName = 'deltaMush';
    nodesOnorOff()
    nodeName = 'ffd';
    nodesOnorOff()
    nodeName = 'tension';
    nodesOnorOff()
    nodeName = 'polySoftEdge';
    nodesOnorOff()
    nodeName = 'wire';
    nodesOnorOff()
    nodeName = 'polyMapCut';
    nodesOnorOff()
    nodeName = 'polyTweakUV';
    nodesOnorOff()
    nodeName = 'polyPlanarProj';
    nodesOnorOff()
    # nodeName = 'skinCluster'; nodesOnorOff(); removeSkinClusterProxy_FromExcludedNodes()
    # print
    # print (printResult),


def turnOffNodesManager():
    global value, excludedValue, addedOrRemoved, nodeName
    value = 1
    excludedValue = 'add'
    addedOrRemoved = ' Excluded\n'
    deformManagerFunction()


def turnOnNodesManager():
    global value, excludedValue, addedOrRemoved, nodeName
    value = 0
    excludedValue = 'rm'
    addedOrRemoved = ' Removed from exclusion\n'
    deformManagerFunction()


################################################
# If is in normal mode when you add the nodes they still are all on
# If you add the nodes in proxy mode they will turn off
# If you remove the nodes will always turn them on in both modes

def deformManagerFunction():
    global nodeName, node
    # Query Current sel, keep in mind if it wasn't nothing selected
    currentSel = cmds.ls(sl=True)
    # Create groups and sets
    createGroupsAndSets()
    # Query node
    node = cmds.ls(type=nodeName)
    # Add or remove nodeName to excluded set
    if excludedValue == 'add':
        cmds.sets(node, e=True, add='Excluded_Nodes')
    # Create Settings
    createSettings()
    # Update node states and settings
    if cmds.getAttr('Folder_Proxys.visibility') == 1:
        cmds.setAttr("FCM_Proxy_Maker_Settings" + ("." + str(nodeName) + '_State'), 0)
        for obj in node:
            try:
                cmds.setAttr(obj + ".nodeState", value)
            except:
                pass

    else:
        cmds.setAttr("FCM_Proxy_Maker_Settings" + ("." + str(nodeName) + '_State'), 1)
        for obj in node:
            try:
                cmds.setAttr(obj + ".nodeState", 0)
            except:
                pass

    # If is en remove mode it will remove after turn them on
    if excludedValue == 'rm':
        cmds.sets(node, e=True, rm='Excluded_Nodes')
        cmds.setAttr("FCM_Proxy_Maker_Settings" + ("." + str(nodeName) + '_State'), 1)
        # Create HUD
    createHUD()
    # Get number selection and print
    print(str(len(node)) + " " + str(nodeName) + str(addedOrRemoved)),
    if len(currentSel) > 0:
        cmds.select(currentSel)
    else:
        cmds.select(cl=True)


################################################
def removeSkinClusterProxy_FromExcludedNodes():
    # List all skinCluster
    skinClusters = cmds.ls(type='skinCluster')
    # Create Empty list
    skinClusterProxys = []
    # Add any mesh with '_Proxy' in the name in a new list
    for mesh in skinClusters:
        if "_Proxy" in mesh:
            skinClusterProxys.append(mesh)
    # Turn nodeState on
    for mesh in skinClusterProxys:
        cmds.setAttr(mesh + '.nodeState', 0)
    # Remove from Exclude set
    cmds.sets(skinClusterProxys, edit=True, rm='Excluded_Nodes')
    # print
    print(str(len(node)) + " " + nodeName + " Excluded"),


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            Heavy Meshes def
            
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''


def addHeavyMesh_Set_Frozen():
    global filteredMeshes, meshesShape
    # Get current Sel
    currentSel = cmds.ls(sl=True)
    # Create groups, sets and settings
    createGroupsAndSets()
    createSettings()
    # get shapes meshes from Set_Normal
    if cmds.objExists('Set_Normal'):
        shapesAndShapesOrig = cmds.ls(type='mesh')
        meshes = cmds.filterExpand(shapesAndShapesOrig, sm=12)
        cmds.select(meshes)
        cmds.pickWalk(d='down')
        meshesShape = cmds.ls(sl=True)
        cmds.select(cl=True)
        ''' Option for only search in Set_Normal
        cmds.select('Set_Normal')
        cmds.pickWalk (d='down')
        meshesShape = cmds.ls ( sl=True)
        cmds.select(cl=True)
        '''
    else:
        sys.exit('First you need to create all the proxys')
    # Filter meshes
    filterMeshes()

    # If filteredMeshes is empty just go for all the meshes in the scene
    if len(filteredMeshes) == 0:
        shapesAndShapesOrig = cmds.ls(type='mesh')
        meshes = cmds.filterExpand(shapesAndShapesOrig, sm=12)
        cmds.select(meshes)
        cmds.pickWalk(d='down')
        meshesShape = cmds.ls(sl=True)
        # Filter meshes
        filterMeshes()

    # Add the filteredes meshes to Set_Frozen
    cmds.sets(filteredMeshes, edit=True, add='Set_Frozen')
    # Turn off checkbox
    cmds.checkBoxGrp('NodesCheckbox1', edit=True, value1=False)

    # Set attr for settings
    cmds.setAttr('FCM_Proxy_Maker_Settings.HeavyMeshConnected_State', 0)

    if cmds.getAttr(FolderProxy + '.visibility') == 1:
        # Go to Proxy mode
        cmds.setAttr(FolderProxy + ".visibility", 1)
        showProxy()

    # Current sel
    cmds.select(currentSel)
    # Print
    print(str(len(filteredMeshes)) + ' Excluded'),


def filterMeshes():
    global filteredMeshes, meshesShape
    # Create list
    filteredMeshes = []
    # Filter
    for mesh in meshesShape:
        connections_oM = cmds.listConnections(mesh + '.outMesh')
        connections_wM = cmds.listConnections(mesh + '.worldMesh[0]')
        try:
            if len(connections_wM) > 0:
                filteredMeshes.append(mesh)
            else:
                if len(connections_oM) > 0:
                    filteredMeshes.append(mesh)
        except:
            pass


def removeHeavyMesh_Set_Frozen():
    # Get Current Sel
    currentSel = cmds.ls(sl=True)
    # Set attr for settings
    cmds.setAttr('FCM_Proxy_Maker_Settings.HeavyMeshConnected_State', 1)
    # Turn on checkbox
    cmds.checkBoxGrp('NodesCheckbox1', edit=True, value1=True)
    # Select all content of Set_Frozen, turn off frozen attribute
    cmds.select(Set_Frozen)
    frozenElements = cmds.ls(sl=True)
    for f in frozenElements:
        cmds.setAttr(f + '.frozen', 0)
    # Downstream Freeze Mode = 'None'
    cmds.freezeOptions(explicitPropagation=False)
    cmds.freezeOptions(downstream='none')

    cmds.sets(filteredMeshes, edit=True, remove='Set_Frozen')
    # current Sel
    cmds.select(currentSel)
    # Print
    print(str(len(filteredMeshes)) + ' Removed from exclusion'),


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            Keep Original Rig Create Automatic Proxy def
            
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''


def createAutomaticProxy_KeepRig():
    createSettings()
    global TrueOrFalse, nodesOnorOff
    # Select all visible Mesh
    selectAllVisibleMeshes()
    removeObjectsWithoutNameSpaces()

    # Create Proxy
    createProxySkinAlsoNonSkinned()
    # Create proxy Exclude for all the non skinned meshes
    cmds.select(Set_NoSkin_List)
    createProxyExcluded()
    # Set Proxy visible
    hideorShowProxySet(value=1)
    cmds.checkBoxGrp("ShowProxy", e=True, value1=True)
    # If sel is equal to 0 means probably you are in the rig file
    # cmds.ls(sl=True)
    '''
    if len(sel) == 0:
        cmds.warning('Creating proxy for every visible mesh in the scene')
        selectAllVisibleMeshes()
        createProxy()
    '''
    # For deform manager only deactive HeavyMeshes
    addHeavyMesh_Set_Frozen()
    # Select clear
    cmds.select(cl=True)

    # Print
    if len(Set_NoSkin_List) > 0:
        print(str(len(Set_NoSkin_List)) + " meshes were excluded because they don't have skinCluster to copy from"),
    else:
        print("Automatic proxy was created successfully"),


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            Delete Original Rig
            
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''


def removeAnnoyingWindows():
    gMainWindow = []
    allOpenWindows = cmds.lsUI(wnd=True)
    # Remove two elements from the list
    allOpenWindows.remove('MayaWindow')
    allOpenWindows.remove('FCM_Proxy_Maker_Window')
    try:
        allOpenWindows.remove('progressWindowDelRig')
    except:
        pass

    for items in allOpenWindows:
        if items != gMainWindow:
            cmds.window(items, e=True, vis=0)


def createAutomaticProxy():
    global animationScene;
    global currentSel

    # Get Current Selection
    currentSel = cmds.ls(sl=True, long=True)
    # Query Namespace and Reference Source
    Query_Namespace_ReferenceSource()
    # Create Automatic Proxy Reference
    # Turn on suspend viewport
    # cmds.refresh(suspend=True)

    # Check if the file is saved

    if cmds.file(q=True, modified=True):

        result = cmds.confirmDialog(title='Window', message='You must save your file first',
                                    button=['Save', 'Cancel'], cancelButton='Cancel')
        try:
            if result == 'Save':
                try:
                    cmds.SaveScene()
                    animationScene = cmds.file(q=True, sn=True)
                except:
                    mel.eval("cleanUpScene 3")
                    cmds.SaveScene()
                    animationScene = cmds.file(q=True, sn=True)

            if result == 'Cancel':
                sys.exit('Operation cancelled by user')
        except:
            cmds.warning('Error trying to save')
            sys.exit('Error while saving, try deleting unknown nodes')
    else:
        # Query Animation Scene
        animationScene = cmds.file(q=True, sn=True)
    # Progress Bar
    if cmds.window("progressWindowDelRig", exists=True):
        cmds.deleteUI('progressWindowDelRig')

    window = cmds.window('progressWindowDelRig', title='Progress Window')
    cmds.columnLayout(adjustableColumn=True)

    cmds.text('textDelRig', align='center')
    progressControlDelRig = cmds.progressBar(maxValue=10, width=300, isInterruptable=True)

    cmds.showWindow(window)
    cmds.window("progressWindowDelRig", edit=True, w=300, h=35, topLeftCorner=[250, 760])
    # Progress bar Open Orig Rig
    cmds.text('textDelRig', edit=True, label='Opening Original rig')
    cmds.progressBar(progressControlDelRig, edit=True, step=2)
    # Open Orig rig
    cmds.file((sourceRef + extension), f=True, open=True, prompt=False)
    # Progress Applying automatic Proxy
    cmds.text('textDelRig', edit=True, label='Applying automatic Proxy')
    cmds.progressBar(progressControlDelRig, edit=True, step=2)
    # Remove prompt window
    removeAnnoyingWindows()
    # Select all visible meshes
    selectAllVisibleMeshes()
    # Create SkinCluster for all the meshes
    list = cmds.ls(sl=True)
    # Create Empty lists
    Set_Skin_List = []
    Set_NoSkin_List = []
    # check if the items has skin or not and put them in temporary sets
    for item in list:
        checkSkin = (mel.eval('findRelatedSkinCluster ' + item))
        # if the result is less than 1 the mesh doesn't have skin
        if len(checkSkin) > 1:
            Set_Skin_List.append(item)
        else:
            Set_NoSkin_List.append(item)

    cmds.select(Set_Skin_List)
    createProxySkin()

    cmds.select(Set_NoSkin_List)
    createProxyExcluded()

    # Progress Bar Applying automatic Proxy
    cmds.text('textDelRig', edit=True, label='Removing original Meshes')
    cmds.progressBar(progressControlDelRig, edit=True, step=2)
    # Remove all original meshes and remove both sets
    delete_SetNormal_FromMinorToHighHistory()
    cmds.delete('Set_Proxy', 'Excluded_Nodes')
    # Progress Bar
    cmds.text('textDelRig', edit=True, label='Saving project as "_Proxy"')
    cmds.progressBar(progressControlDelRig, edit=True, step=2)
    # Save Project as the same name plus "_Proxy"
    cmds.file(rename=(sourceRef + "_Proxy"))
    try:
        cmds.file(f=True, save=True)
        # If trying to save cause an error optimice the scene deleting unkwown nodes and try again
    except:
        mel.eval("cleanUpScene 3")
        cmds.file(f=True, save=True)
    # Go back to animation file with the reference
    # Progress Bar
    cmds.text('textDelRig', edit=True, label='Opening animation file')
    cmds.progressBar(progressControlDelRig, edit=True, step=1)
    cmds.file(animationScene, f=True, open=True, prompt=False)
    # Turn off suspend viewport
    # cmds.refresh(suspend=False)
    # Progress Bar
    cmds.text('textDelRig', edit=True, label='Loading Proxy Reference')
    cmds.progressBar(progressControlDelRig, edit=True, step=1)
    # Load Proxy Reference
    cmds.select(currentSel)
    cmds.file((sourceRef + '_Proxy' + extension), prompt=False, loadReference=namespaceRef)
    # Switch to dg and then parallel to avoid crashes
    cmds.evaluationManager(mode="off")
    cmds.evaluationManager(mode="parallel")
    # Turn off HUD Proxy
    # cmds.headsUpDisplay ("HUDProxy", edit=True, visible=0)
    # Progress Bar Closing
    cmds.deleteUI('progressWindowDelRig')
    # Close all floating panel
    removeAnnoyingWindows()
    # Confirm dialog wich open again the window and print successfully result
    result = cmds.confirmDialog(title='Window', message='Proxy File successfully created!', button=['Ok'])
    if result == 'Ok':
        print("Proxy file successfully created"),


############################################

def Query_Namespace_ReferenceSource():
    global sourceRef;
    global sourceRefList;
    global namespaceRef;
    global extension

    sel = cmds.ls(sl=True)
    if len(sel) == 0:
        sys.exit('You must have an element of the rig selected')
    # Query reference source
    sourceRefList = cmds.referenceQuery(sel, filename=True, withoutCopyNumber=True)
    # Query namespace
    namespaceRef = cmds.referenceQuery(sel, referenceNode=True)
    # Convert list to string
    sourceRef = ''.join([str(elem) for elem in sourceRefList])
    # Query extension
    extension = sourceRef[-3:]
    # Delete .ma/.mb and _Proxy (if exists) From the string
    sourceRef = sourceRef.replace('.ma', '')
    sourceRef = sourceRef.replace('.mb', '')
    sourceRef = sourceRef.replace('_Proxy', '')


##########
def loadProxyRef():
    Query_Namespace_ReferenceSource()
    currentSel = cmds.ls(sl=True)
    cmds.file((sourceRef + '_Proxy' + extension), prompt=False, loadReference=namespaceRef)
    # Check if Checkbox Save After Load is On
    if cmds.checkBoxGrp("SaveAfterLoading", query=True, value1=True) == 1:
        cmds.SaveScene()
    cmds.select(currentSel)
    # Close all floating panel excepting Maya and the tool
    removeAnnoyingWindows()
    # For avoiding crashes (DG, step foward and backward, go back to parallel)
    cmds.evaluationManager(mode="off")
    # mel.eval('playButtonStepForward')
    # mel.eval('playButtonStepBackward')
    cmds.evaluationManager(mode='parallel')
    print('Proxy Rig loaded'),


def loadNormalRef():
    currentSel = cmds.ls(sl=True)
    Query_Namespace_ReferenceSource()
    cmds.file((sourceRef + extension), prompt=False, loadReference=namespaceRef)
    # Check if Checkbox Save After Load is On
    if cmds.checkBoxGrp("SaveAfterLoading", query=True, value1=True) == 1:
        cmds.SaveScene()
    cmds.select(currentSel)
    # Close all floating panel
    removeAnnoyingWindows()
    # For avoiding crashes (DG, step foward and backward, go back to parallel)
    cmds.evaluationManager(mode="off")
    # mel.eval('playButtonStepForward')
    # mel.eval('playButtonStepBackward')
    cmds.evaluationManager(mode='parallel')
    # Print
    print('Normal Rig loaded'),


def goToProxyRig():
    Query_Namespace_ReferenceSource()
    cmds.file((sourceRef + '_Proxy' + extension), prompt=False, f=True, open=True)
    # Close all floating panel
    removeAnnoyingWindows()


def goToNormalRig():
    Query_Namespace_ReferenceSource()
    cmds.file((sourceRef + extension), prompt=False, f=True, open=True)
    # Close all floating panel
    removeAnnoyingWindows()


def delete_SetNormal_FromMinorToHighHistory():
    cmds.select('Set_Normal')
    meshes = cmds.ls(sl=True, long=True)
    meshes = cmds.filterExpand(meshes, sm=12)

    orderMeshes = []
    for mesh in meshes:
        # query all the nodes
        history = cmds.listHistory(mesh)
        # transform nodes into numbers
        numHistory = len(history)
        # Pair numbers with single mesh
        orderMeshes.append([numHistory, mesh])
        # order minor to major
        orderMeshes.sort()

    for item in orderMeshes:
        try:
            cmds.delete(item[1])
        except:
            pass


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            Performance Window Manager
            
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''


def contactWindow():
    # Contact Window
    if cmds.window("FCM_Proxy_Maker_Contact", exists=True):
        cmds.deleteUI("FCM_Proxy_Maker_Contact")
    windowProxyMaker = cmds.window("FCM_Proxy_Maker_Contact", title="Contact", s=False)

    cmds.rowColumnLayout(numberOfColumns=2, columnAttach=(1, 'right', 0), columnWidth=[(1, 100), (2, 250)])
    cmds.text(label='Name:  ')
    name = cmds.textField(text='Francisco Cerchiara Montero', editable=True)
    cmds.text(label='Email:  ')
    address = cmds.textField(text='FranCM127@hotmail.com', editable=True)
    cmds.text(label='Facebook:  ')
    phoneNumber = cmds.textField(text='www.facebook.com/Fran127', editable=True)
    cmds.text(label='Linked-In:  ')
    email = cmds.textField(text='www.linkedin.com/in/francm3danimator/', editable=True)

    #    Attach commands to pass focus to the next field if the Enter
    #    key is pressed. Hitting just the Return key will keep focus
    #    in the current field.
    #
    cmds.textField(name, edit=True, enterCommand=('cmds.setFocus(\"' + address + '\")'))
    cmds.textField(address, edit=True, enterCommand=('cmds.setFocus(\"' + phoneNumber + '\")'))
    cmds.textField(phoneNumber, edit=True, enterCommand=('cmds.setFocus(\"' + email + '\")'))
    cmds.textField(email, edit=True, enterCommand=('cmds.setFocus(\"' + name + '\")'))

    cmds.showWindow(windowProxyMaker)


##################
def Option_1_VisCollapse():
    cmds.window('FCM_Proxy_Maker_Window', edit=True, h=100)
    if cmds.objExists('FCM_Proxy_Maker_Settings'):
        cmds.setAttr('FCM_Proxy_Maker_Settings.Option_1_Vis', 0)


def Option_1_VisExpand():
    cmds.window('FCM_Proxy_Maker_Window', edit=True, h=100)
    if cmds.objExists('FCM_Proxy_Maker_Settings'):
        cmds.setAttr('FCM_Proxy_Maker_Settings.Option_1_Vis', 1)


def Option_2_VisCollapse():
    cmds.window('FCM_Proxy_Maker_Window', edit=True, h=100)
    if cmds.objExists('FCM_Proxy_Maker_Settings'):
        cmds.setAttr('FCM_Proxy_Maker_Settings.Option_2_Vis', 0)


def Option_2_VisExpand():
    cmds.window('FCM_Proxy_Maker_Window', edit=True, h=100)
    if cmds.objExists('FCM_Proxy_Maker_Settings'):
        cmds.setAttr('FCM_Proxy_Maker_Settings.Option_2_Vis', 1)


def deformManager_VisCollapse():
    cmds.window('FCM_Proxy_Maker_Window', edit=True, h=100)
    if cmds.objExists('FCM_Proxy_Maker_Settings'):
        cmds.setAttr('FCM_Proxy_Maker_Settings.deformManager_Vis', 0)


def deformManager_VisExpand():
    cmds.window('FCM_Proxy_Maker_Window', edit=True, h=100)
    if cmds.objExists('FCM_Proxy_Maker_Settings'):
        cmds.setAttr('FCM_Proxy_Maker_Settings.deformManager_Vis', 1)


##################
def DeleteProxy():
    if cmds.radioButtonGrp("DeleteProxy", q=True, sl=True) == 1:
        DeleteSelected()
    else:
        deleteAllProxys()


##################
def createProxy():
    if cmds.optionMenuGrp("CreateProxyMenu", q=True, v=True) == "SkinCluster":
        createProxySkinAlsoNonSkinned()
    if cmds.optionMenuGrp("CreateProxyMenu", q=True, v=True) == "Constraint":
        createProxyConstraint()
    if cmds.optionMenuGrp("CreateProxyMenu", q=True, v=True) == "Exclude":
        createProxyExcluded()
    ##################


def oncommand1DelRig():
    if cmds.objExists('Folder_Proxys'):
        cmds.setAttr('Folder_Proxys.visibility', 1)
        cmds.checkBoxGrp('ShowProxy', edit=True, value1=1)
    else:
        cmds.warning('Proxys not found')
        cmds.checkBoxGrp('ShowProxy', edit=True, value1=1)


def offcommand1DelRig():
    if cmds.objExists('Folder_Proxys'):
        cmds.setAttr('Folder_Proxys.visibility', 0)
        cmds.checkBoxGrp('ShowProxy', edit=True, value1=0)
    else:
        cmds.warning('Proxys not found')
        cmds.checkBoxGrp('ShowProxy', edit=True, value1=0)


##################
def CreateProxyMenu_ChangeCommand():
    if cmds.optionMenuGrp("CreateProxyMenu", q=True, v=True) == "SkinCluster":
        cmds.text('nonskinnedMethodText', edit=True, enable=True)
        cmds.radioButtonGrp('nonSkinnedMethod', edit=True, enable=True)
    cmds.button('createAutomaticProxyKeepRig', edit=True, enable=True)
    if cmds.optionMenuGrp("CreateProxyMenu", q=True, v=True) == "Constraint":
        cmds.text('nonskinnedMethodText', edit=True, enable=False)
        cmds.radioButtonGrp('nonSkinnedMethod', edit=True, enable=False)
        cmds.button('createAutomaticProxyKeepRig', edit=True, enable=False)
    if cmds.optionMenuGrp('CreateProxyMenu', q=True, v=True) == "Exclude":
        cmds.text('nonskinnedMethodText', edit=True, enable=False)
        cmds.radioButtonGrp('nonSkinnedMethod', edit=True, enable=False)
        cmds.button('createAutomaticProxyKeepRig', edit=True, enable=False)


######################################################

def ProxyMakerWindow():
    global Set_Normal, Excluded_Nodes, FolderProxy, currentSelProxy, Set_Frozen
    FolderProxy = 'Folder_Proxys'
    Set_Normal = 'Set_Normal'
    Excluded_Nodes = 'Excluded_Nodes'
    Set_Frozen = 'Set_Frozen'

    createSettings()
    if cmds.window("FCM_Proxy_Maker_Window", exists=True):
        cmds.deleteUI("FCM_Proxy_Maker_Window")

    windowProxyMaker = cmds.window("FCM_Proxy_Maker_Window", title="FCM_Proxy_Maker", s=True, menuBar=True)

    # File
    cmds.menu(label='File')
    cmds.menuItem(label='Save Proxy', c="cmds.warning('WIP! Sorry')")
    cmds.menuItem(label='Load Proxy', c="cmds.warning('WIP! Sorry')")
    # Help
    cmds.menu(label='Help')
    cmds.menuItem(l='Documentation',
                  c="cmds.launch (web='https://docs.google.com/document/d/1fLz6TFs7I9M3hadDZHkl9t6L39NxBZDQbpCBvzdkAyY/edit?usp=sharing')")
    cmds.menuItem(l='Video Tutorials',
                  c="cmds.launch (web='https://www.youtube.com/watch?v=LLtW3t1RfhI&list=PLME7GNNMRppKIg-1S2zB97kB3UzFFnFkc&index=2&t=0s')")
    cmds.menuItem(l='Contact', c="contactWindow()")

    # Version
    cmds.menu(label=('Version: ' + version), enable=False)
    # cmds.menu( image='FCM_Proxy_Maker_Logo')

    cmds.columnLayout(adjustableColumn=True)

    heightButton = 31
    columnAttach1 = 10
    columnAttach2 = -25
    widthButton = 116

    cmds.frameLayout('proxyManagerTab', label="Proxy Manager", marginHeight=7, marginWidth=7, collapse=False,
                     collapsable=True,
                     collapseCommand="cmds.window ('FCM_Proxy_Maker_Window', edit=True, h=100)",
                     expandCommand="cmds.window ('FCM_Proxy_Maker_Window', edit=True, h=100)")

    cmds.frameLayout('keepOriginalRig', label="Option 1 (Keep Original Rig)", marginHeight=7, marginWidth=7,
                     collapse=False, collapsable=True,
                     collapseCommand="Option_1_VisCollapse(); cmds.window ('FCM_Proxy_Maker_Window', edit=True, h=100)",
                     expandCommand="Option_1_VisExpand(); cmds.window ('FCM_Proxy_Maker_Window', edit=True, h=100)")

    # Toggle Proxy
    cmds.button(label="Toggle Proxy", c="toggleButton()", w=150, h=31)
    cmds.popupMenu()
    cmds.menuItem(l="Create Shelf button", c="createShelfButton()")

    cmds.separator()

    # =============================================
    # Proxy Manager
    # FrameLayout Option 1

    '''
    # Non skinned method 
    cmds.text('nonskinnedMethodText', label='Non skinned method:', align='center', ann="For all of those meshes who doesn't have SkinCluster")
    cmds.radioButtonGrp ("nonSkinnedMethod", numberOfRadioButtons=3, sl=1,
    label1="Exclude", label2="One Joint", label3="Do Nothing",
    an1='Exclude all meshes with no skinCluster', 
    an2='Look the closest joint to the mesh and apply skincluster', 
    an3='Do nothing to the non skinned meshes, use it when you want to create custom constraint and exclude proxys', 
    onCommand1 = "cmds.button ('createAutomaticProxyKeepRig', e=True, en=True)",
    onCommand2 = "cmds.button ('createAutomaticProxyKeepRig', e=True, en=True)",
    onCommand3 = "cmds.button ('createAutomaticProxyKeepRig', e=True, en=False)",
    columnWidth = [[1, 70], [2, 85], [3, 150]])
     # this is the connection between option 1 and 2
    #changeCommand1= "cmds.radioButtonGrp ('nonSkinnedMethodDelOrigRig', edit=True, sl=1)",
    #changeCommand2= "cmds.radioButtonGrp ('nonSkinnedMethodDelOrigRig', edit=True, sl=2)",
    #changeCommand3= "cmds.radioButtonGrp ('nonSkinnedMethodDelOrigRig', edit=True, sl=3)")
    
    '''

    # Create Automatic Proxy
    cmds.button('createAutomaticProxyKeepRig', l="Create Automatic Proxy", w=widthButton, h=heightButton,
                c="createAutomaticProxy_KeepRig()")

    cmds.rowLayout(numberOfColumns=2)

    # Create Proxy
    cmds.button(l="Create Proxy", w=widthButton, h=heightButton, c="createProxy()")

    # Skin / Constraint / Exclude
    cmds.optionMenuGrp("CreateProxyMenu", columnAttach=[1, "left", 20])
    # Turn value off for non skinned method when the control menutim "Skincluster is Off"
    # changeCommand = 'CreateProxyMenu_ChangeCommand()')
    cmds.menuItem(label='SkinCluster')
    cmds.menuItem(label='Constraint')
    cmds.menuItem(label='Exclude')

    cmds.setParent("..")

    cmds.rowLayout(numberOfColumns=2)
    # Remove Proxy
    cmds.button(l="Delete Proxy", w=widthButton, h=heightButton, c="DeleteProxy()")
    # Selected / All
    cmds.radioButtonGrp("DeleteProxy", numberOfRadioButtons=2, sl=2,
                        label1="Selected", label2="All", columnAttach=[
            [1, "left", 15],
            [2, "left", -20]])

    cmds.setParent("..")

    cmds.separator()
    # Show Proxy
    cmds.checkBoxGrp("ShowProxy", numberOfCheckBoxes=1, value1=1,
                     label1="Show Proxy", columnAttach=[1, 'right', 45],
                     onCommand1="hideorShowProxySet(value = 1)",
                     offCommand1="hideorShowProxySet(value = 0)")

    # =============================================
    # Deform Manager
    posHor1 = 95
    cmds.frameLayout('deformManagerTab', label="Deform Manager", collapse=True, collapsable=True,
                     collapseCommand="deformManager_VisCollapse(); cmds.window ('FCM_Proxy_Maker_Window', edit=True, h=100)",
                     expandCommand="deformManager_VisExpand(); cmds.window ('FCM_Proxy_Maker_Window', edit=True, h=100)")

    cmds.separator(h=1, style="none")
    # All / None
    cmds.rowLayout(numberOfColumns=2)
    cmds.button(l="All", w=140,
                c="def nodesOnorOff():\n    turnOnNodesManager()\nTrueOrFalse = 1 \nprintResult = 'Turn On all nodes from Deform Manager'\nturnonOrOffAllDeform()\nremoveHeavyMesh_Set_Frozen()")
    cmds.button(l="None", w=140,
                c="def nodesOnorOff():\n    turnOffNodesManager()\nTrueOrFalse = 0 \nprintResult = 'Turn Off all nodes from Deform Manager'\nturnonOrOffAllDeform()\naddHeavyMesh_Set_Frozen()")
    cmds.setParent("..")

    # Nodes Checkboxes Heavy Mesh connected / BlendShape / Wire
    cmds.checkBoxGrp("NodesCheckbox1", numberOfCheckBoxes=3,
                     label1="HeavyMeshes", value1=True,
                     columnWidth=[[1, posHor1], [2, 90]],
                     onCommand1="removeHeavyMesh_Set_Frozen()",
                     offCommand1="addHeavyMesh_Set_Frozen()",

                     label2="BlendShape", value2=True,
                     onCommand2="nodeName = 'blendShape'; turnOnNodesManager()",
                     offCommand2="nodeName = 'blendShape'; turnOffNodesManager()",

                     label3="Wire", value3=True,
                     onCommand3="nodeName = 'wire'; turnOnNodesManager()",
                     offCommand3="nodeName = 'wire'; turnOffNodesManager()", )
    # Nodes Checkboxes Wrap / PolySmooth / DeltaMush
    cmds.checkBoxGrp("NodesCheckbox2", numberOfCheckBoxes=3,
                     label1="Wrap", value1=True,
                     columnWidth=[[1, posHor1], [2, 90]],
                     onCommand1="nodeName = 'wrap'; turnOnNodesManager()",
                     offCommand1="nodeName = 'wrap'; turnOffNodesManager()",

                     label2="PolySmooth", value2=True,
                     onCommand2="nodeName = 'polySmoothFace'; turnOnNodesManager()",
                     offCommand2="nodeName = 'polySmoothFace'; turnOffNodesManager()",

                     label3="DeltaMush", value3=True,
                     onCommand3="nodeName = 'deltaMush'; turnOnNodesManager()",
                     offCommand3="nodeName = 'deltaMush'; turnOffNodesManager()", )
    # Nodes Checkboxes ffd / Tension / PolySoftEdge
    cmds.checkBoxGrp("NodesCheckbox3", numberOfCheckBoxes=3,
                     label1="ffd", value1=True,
                     columnWidth=[[1, posHor1], [2, 90]],
                     onCommand1="nodeName = 'ffd'; turnOnNodesManager()",
                     offCommand1="nodeName = 'ffd'; turnOffNodesManager()",

                     label2="Tension", value2=True,
                     onCommand2="nodeName = 'tension'; turnOnNodesManager()",
                     offCommand2="nodeName = 'tension'; turnOffNodesManager()",

                     label3="PolySoftEdge", value3=True,
                     onCommand3="nodeName = 'polySoftEdge'; turnOnNodesManager()",
                     offCommand3="nodeName = 'polySoftEdge'; turnOffNodesManager()", )

    # Nodes Checkboxes polyMapCut / PolyTweakUV / PolyPlanarProj
    cmds.checkBoxGrp("NodesCheckbox4", numberOfCheckBoxes=3,
                     label1="PolyMapCut", value1=True,
                     columnWidth=[[1, posHor1], [2, 90]],
                     onCommand1="nodeName = 'polyMapCut'; turnOnNodesManager()",
                     offCommand1="nodeName = 'polyMapCut'; turnOffNodesManager()",

                     label2="PolyTweakUV", value2=True,
                     onCommand2="nodeName = 'polyTweakUV'; turnOnNodesManager()",
                     offCommand2="nodeName = 'polyTweakUV'; turnOffNodesManager()",

                     label3="PolyPlanarProj", value3=True,
                     onCommand3="nodeName = 'polyPlanarProj'; turnOnNodesManager()",
                     offCommand3="nodeName = 'polyPlanarProj'; turnOffNodesManager()", )

    cmds.separator()
    # Nodes Checkboxes polyMapCut / PolyTweakUV / PolyPlanarProj
    cmds.checkBoxGrp("NodesCheckbox5", numberOfCheckBoxes=2,
                     label1="SkinCluster", value1=True,
                     columnWidth=[[1, posHor1], [2, 90]],
                     onCommand1="nodeName = 'skinCluster'; turnOnNodesManager()",
                     offCommand1="nodeName = 'skinCluster'; turnOffNodesManager(); removeSkinClusterProxy_FromExcludedNodes()",

                     label2="Cluster", value2=True,
                     onCommand2="nodeName = 'cluster'; turnOnNodesManager()",
                     offCommand2="nodeName = 'cluster'; turnOffNodesManager()")

    cmds.setParent("..")
    cmds.setParent("..")

    # ==================================================================
    # frameLayout Delete Original Rig
    cmds.frameLayout('DeleteOriginalRig', label="Option 2 (Delete Original Rig)", marginHeight=7, marginWidth=7,
                     collapse=False, collapsable=True,
                     collapseCommand="Option_2_VisCollapse(); cmds.window ('FCM_Proxy_Maker_Window', edit=True, h=100)",
                     expandCommand="Option_2_VisExpand(); cmds.window ('FCM_Proxy_Maker_Window', edit=True, h=100)")

    cmds.rowLayout(numberOfColumns=2, columnAttach=[2, "both", 8])

    cmds.button(l="Load Proxy", w=widthButton, h=heightButton, c="loadProxyRef()")
    cmds.popupMenu("ProxyPopUp")
    cmds.menuItem(l="Go to Proxy Rig", c="goToProxyRig()")

    cmds.button(l="Load Normal", w=widthButton, h=heightButton, c="loadNormalRef()")
    cmds.popupMenu("NormalPopUp")
    cmds.menuItem(l="Go to Normal Rig", c="goToNormalRig()")

    cmds.setParent("..")

    # Save After Load / Show Label Proxy
    cmds.checkBoxGrp("SaveAfterLoading", numberOfCheckBoxes=2, columnAttach=[2, "both", 20], enable2=False,
                     label1="Save After Loading", label2="Show Label Proxy", columnWidth=[1, 120],
                     ann='Save the file after load the reference, this function is for those rigs who always crash after be loaded',
                     onCommand1="createSettings(); cmds.setAttr ('FCM_Proxy_Maker_Settings.Save_After_Loading', 1)",
                     offCommand1="createSettings(); cmds.setAttr ('FCM_Proxy_Maker_Settings.Save_After_Loading', 0)")

    cmds.separator()

    # Create Automatic Proxy
    cmds.button(l="Create Automatic Proxy", w=widthButton, h=heightButton, c="createAutomaticProxy()")
    cmds.button(l="Delete Original Rig", w=widthButton, h=heightButton, c="deleteOriginalRig()")

    cmds.setParent("..")
    cmds.setParent("..")
    cmds.setParent("..")

    # ==================================================================
    # Modify Proxy
    cmds.frameLayout(label="Modify Proxy", marginHeight=5, marginWidth=5, collapse=True, collapsable=True,
                     collapseCommand="cmds.window (\"FCM_Proxy_Maker_Window\", edit=True, h=100)")
    # Checkboxes Group Isolate Selection / Mirror X
    cmds.checkBoxGrp("ChechboxGroup1", numberOfCheckBoxes=1, label1="Mirror X",
                     onCommand1="mel.eval('reflectionSetMode objectx')",
                     offCommand1="mel.eval('reflectionSetMode none')")

    separation = 0
    cmds.rowLayout(numberOfColumns=5,
                   cat=[[1, "both", separation], [2, "both", separation], [3, "both", separation],
                        [4, "both", separation], [5, "both", separation]])
    # Modelling Tool: MultiCut
    cmds.iconTextButton(style="iconAndTextHorizontal", image1="polySplitEdgeRing.png", c="cmds.SplitEdgeRingTool()")
    # Modelling Tool: polySplitEdgeRing
    cmds.iconTextButton(style="iconAndTextHorizontal", image1="multiCut_NEX32.png", c="cmds.dR_multiCutTool()")
    # Modelling Tool: GoToBindPose
    cmds.iconTextButton(style="iconAndTextHorizontal", image1="goToBindPose.png", c="cmds.GoToBindPose()")
    # Modelling Tool: polyGrowSelection
    cmds.iconTextButton(style="iconAndTextHorizontal", image1="polyGrowSelection.png",
                        c="cmds.polySelectConstraint (pp=1)")
    # Modelling Tool: polyShrinkSelection
    cmds.iconTextButton(style="iconAndTextHorizontal", image1="polyShrinkSelection.png",
                        c="cmds.polySelectConstraint (pp=2)")

    cmds.setParent("..")

    cmds.rowLayout(numberOfColumns=3, columnAttach=[2, "both", 8])
    # Quick Reduce:
    widthButton = 82
    # -50%
    cmds.button(l="-50%", w=widthButton, h=heightButton, c="reducePoly(percentage = 50)")
    # -25%
    cmds.button(l="-25%", w=widthButton, h=heightButton, c="reducePoly(percentage = 25)")
    # -10%
    cmds.button(l="-10%", w=widthButton, h=heightButton, c="reducePoly(percentage = 10)")
    cmds.setParent("..")
    cmds.setParent("..")

    # ==================================================================
    # Check Functions
    cmds.frameLayout(label="Check Functions", marginHeight=5, marginWidth=5, collapse=True, collapsable=True,
                     collapseCommand="cmds.window (\"FCM_Proxy_Maker_Window\", edit=True, h=100)")
    # Smooth Preview Manager
    cmds.frameLayout(label="Smooth Mesh Preview Manager", marginHeight=5, marginWidth=5, collapse=True,
                     collapsable=True,
                     collapseCommand="cmds.window (\"FCM_Proxy_Maker_Window\", edit=True, h=100)")

    sepHor = 15
    cmds.radioButtonGrp("Radio2", numberOfRadioButtons=3, sl=1,
                        label="Iterations:", label1="0", label2="1", label3="2",
                        columnAttach=[
                            [1, "left", (sepHor + 10)],
                            [2, "left", (sepHor + -55)],
                            [3, "left", (sepHor + -110)],
                            [4, "left", (sepHor + -165)]])

    cmds.rowLayout(numberOfColumns=3, adjustableColumn=True)
    cmds.button(label="Apply", w=widthButton, h=heightButton, c="applyButtonSPM()")
    cmds.popupMenu()
    cmds.menuItem(l="",
                  c="cmds.launch (web='https://thumbs.dreamstime.com/b/egg-rolling-across-table-slow-motion-filmed-fps-49495604.jpg')")
    cmds.radioButtonGrp("Radio1", numberOfRadioButtons=2, sl=2,
                        label1="Select", label2="All",
                        columnAttach=[[1, "left", columnAttach1], [2, "left", columnAttach2]])

    cmds.setParent("..")
    cmds.setParent("..")

    cmds.separator(h=1)
    # ===============
    # Profiler / Measure Performance
    cmds.rowLayout(numberOfColumns=2, columnAttach=[2, "both", 8])
    widthButton = 125
    # Measure performance
    cmds.button(label="Measure Performance", w=widthButton, h=heightButton,
                ann='Open measure performance, thank you Jorn-Harald Paulsen for creating this amazing tool!',
                c="mel.eval(\"//*************************************************************************************************************\\n// Title: jh_measurePerformance.mel\\n// Author: Jorn-Harald Paulsen\\n// Created: December 7, 2011\\n// Last Update: June 06, 2013\\n// Description: Utility to measure the speed of a scene, especially useful for rig-performance tweaks.\\n//*************************************************************************************************************\\n// MAIN WINDOW\\n//*************************************************************************************************************\\nglobal proc jh_measurePerformance ()\\n{\\n  //Delete window if it already exists\\n  if (`window -q -ex jh_measurePerformance`) deleteUI jh_measurePerformance;\\n\\n  //Main Window\\n  window -te 30 -t \\\"Measure Performance\\\" -mxb 0 -s 1 -rtf 0 -mb 0 -mbv 0 -w 350 -h 544 jh_measurePerformance;\\n\\n  //Window content\\n  columnLayout -adjustableColumn true;\\n  text -label \\\"\\\\nUtility to measure performance/evaluation of the scene\\\" -fn boldLabelFont;\\n  separator -w 300 -h 10;\\n  text -label \\\"It measures by playing off the scene, so you should\\\";\\n  text -label \\\"have animation on the obects you want to evaluate!\\\";\\n  text -label \\\"Note: Longer playback = More accurate results\\\";\\n  separator -w 300 -h 15;\\n  text -label \\\"Startframe:\\\";\\n  intField startFrame;\\n  text -label \\\"Endframe:\\\";\\n  intField endFrame;\\n  separator -w 300 -h 15;\\n  text -label \\\"Number of nodes to return:\\\";\\n  intField -v 20 numNodes;\\n  separator -w 300 -h 10;\\n  button -label \\\"Measure performance\\\" -c jh_evaluate;\\n  textField -text \\\"Time taken: \\\" -ed 0 timeField;\\n  textField -text \\\"FPS: \\\" -ed 0 fpsField;\\n  textScrollList -ams 0 -h 250 -sc jh_selNode evaluatedNodes;\\n  separator -w 300 -h 15;\\n  text -label \\\"Filter by nodetype\\\" -fn boldLabelFont;\\n  textField -text \\\"\\\" nodeField;\\n  button -label \\\"Filter\\\" -c jh_filterResult;\\n  separator -w 300 -h 15;\\n  button -label \\\"Choose where to save the file\\\" -c jh_getExportDir;\\n  textField -en 0 evalExportField;\\n  button -label \\\"Export the results\\\" -c jh_exportToFile;\\n  separator -w 300 -h 15;\\n  //Set the startFrame/endFrame min/max to the timeline's min/max\\n  intField -e -v `playbackOptions -q -min` startFrame;\\n  intField -e -v `playbackOptions -q -max` endFrame;\\n  //Create the window\\n  window -e -w 350 -h 544 jh_measurePerformance;\\n  showWindow jh_measurePerformance;\\n}\\n\\nglobal proc jh_evaluate()\\n{\\n  //Remove all items in the textScrollList\\n  textScrollList -e -ra evaluatedNodes;\\n  //Get the frames to playback\\n  int $min = `intField -q -v startFrame`;\\n  int $max = `intField -q -v endFrame`;\\n  //Set the timeSlider to the min/max values\\n  playbackOptions -min $min -max $max;\\n  //Get the number of frames to playback\\n  int $frames = $max - $min;\\n  //Get the number of nodes to return\\n  int $nodesCount = `intField -q -v numNodes`;\\n\\n  //Set the playBack to Free/Play Every Frame\\n  playbackOptions -e -playbackSpeed 0 -maxPlaybackSpeed 0;\\n  //Set the timeSlider to the startFrame\\n  currentTime `playbackOptions -q -min`;\\n  //Reset the dgtimer\\n  dgtimer -on -reset;\\n  //Play the scene (don't loop)\\n  play -wait;\\n  //Turn off the dgtimer\\n  dgtimer -off;\\n  //Stor the result of the dgTimer\\n  string $evalResult[] = `dgtimer -outputFile \\\"MEL\\\" -maxDisplay $nodesCount -query`;\\n  //Extract the elapsed time and the FPS\\n  string $tempToken[];\\n  tokenize $evalResult[12] \\\": \\\" $tempToken;\\n  float $time = $tempToken[3];\\n  float $fps = ($frames / $time);\\n  //Update the textField for time and FPS\\n  textField -e -text (\\\"Time taken: \\\" + $tempToken[3] + \\\" seconds\\\") timeField;\\n  textField -e -text (\\\"FPS: \\\" + $fps) fpsField;\\n  //For each returned node\\n  for($a = 40; $a < (40 + $nodesCount); $a++)\\n  {\\n    //Remove all of the spaces between each element\\n    string $el[];\\n    tokenize $evalResult[$a] \\\" \\\" $el;\\n    //If the result has a % at index 3\\n    if (`gmatch $el[3] \\\"*%\\\"` == 1)\\n    {\\n      //Create a separator string\\n      string $sep = \\\"    |    \\\";\\n      //Generate the string to put into the textScrollList\\n      string $string = ($el[0] + $sep + $el[3] + $sep + $el[7] + $sep + $el[8]);\\n      //Update the textScrollList\\n      textScrollList -e -append $string evaluatedNodes;\\n    }\\n  }\\n  //Get the actual number of elements returned\\n  int $returnedElements = size(`textScrollList -q -ai evaluatedNodes`);\\n  //Update the node count to the actual number\\n  intField -e -v $returnedElements numNodes;\\n  //Print the result\\n  print $evalResult;\\n  print \\\"\\\\n\\\\n\\\\nSee the script editor for details!\\\\n\\\";\\n}\\n\\nglobal proc jh_selNode()\\n{\\n  //Get the selected item in the textScrollList\\n  string $selItem[] = `textScrollList -q -si evaluatedNodes`;\\n  //Extract the elapsed time and the FPS\\n  string $tempToken[];\\n  tokenize $selItem[0] \\\"|\\\" $tempToken;\\n  //If the object exists\\n  if(objExists($tempToken[3]) == 1)\\n  {\\n    //Select the item\\n    select -r $tempToken[3];\\n    //Print information\\n    print (\\\"\\\\nSelected: \\\" + $tempToken[3] + \\\"\\\\n\\\");\\n  }\\n}\\n\\nglobal proc jh_filterResult()\\n{\\n  //Get the text to filter from\\n  string $filter = `textField -q -text nodeField`;\\n  //Get all of the items in the textScrollList\\n  string $allItems[] = `textScrollList -q -ai evaluatedNodes`;\\n  //Remove all items in the textScrollList\\n  textScrollList -e -ra evaluatedNodes;\\n  //For each item in the textScrollList\\n  for($item in $allItems)\\n  {\\n    //Separate the string\\n    string $tempToken[];\\n    tokenize $item \\\" | \\\" $tempToken;\\n    //If the current element matches the filter-tekst, add it to the textScrollList\\n    if (`gmatch $tempToken[2] $filter` == 1) textScrollList -e -append $item evaluatedNodes;\\n  }\\n  //Get the actual number of elements returned\\n  int $returnedElements = size(`textScrollList -q -ai evaluatedNodes`);\\n  //If no elements was returned\\n  if($returnedElements == 0)\\n  {\\n    //Add the original elements back into the textScrollList\\n    for($element in $allItems) textScrollList -e -append $element evaluatedNodes;\\n    //Print warning message\\n    warning \\\"\\\\nCould not find any matching items!\\\\n\\\";\\n  }\\n  //Else, print information\\n  else print (\\\"A total of \\\" +  $returnedElements + \\\" nodes was found matching \\\\\\\"\\\" + $filter + \\\"\\\\\\\"\\\\n\\\");\\n}\\n\\nglobal proc jh_getExportDir()\\n{\\n  //Open the file-dialog, and get the results from it\\n  string $getExportDir = `fileDialog -m 1 -dm \\\"*.mel\\\"`;\\n  //Put the directory in the textField\\n  textField -e -text $getExportDir evalExportField;\\n}\\n\\nglobal proc jh_exportToFile()\\n{\\n  //Get all of the items in the textScrollList\\n  string $allItems[] = `textScrollList -q -ai evaluatedNodes`;\\n  //Get the directory for where to store the animation\\n  string $exportDir = `textField -q -text evalExportField`;\\n  //If a directory wasn't defined, print error\\n  if($exportDir == \\\"\\\") error \\\"\\\\nYou need to define a directory to store the animation in!\\\\n\\\";\\n\\n  //Create and open the storefile for writing\\n  int $fileId = `fopen $exportDir \\\"w\\\"`;\\n  //For each item in the textScrollList, print the item to the file\\n  for($item in $allItems) fprint $fileId ($item + \\\"\\\\n\\\");\\n  //Close the file for writing\\n  fclose $fileId;\\n  //Print information\\n  print \\\"\\\\nDone!\\\";\\n}\\n\\n\\njh_measurePerformance;\\n\" )\n")
    # Profiler
    cmds.button(label="Profiler", w=widthButton, h=heightButton, c="cmds.ProfilerTool()")

    cmds.setParent("..")

    # DG / Parallel
    cmds.rowLayout(numberOfColumns=2, columnAttach=[2, "both", 8])
    cmds.button(label="DG", w=widthButton, h=heightButton, c="cmds.evaluationManager (mode='off')")
    cmds.button(label="Parallel", w=widthButton, h=heightButton,
                c="cmds.evaluationManager (mode='off'); cmds.evaluationManager (mode='parallel')")
    cmds.popupMenu('GPUOverridePopUp')
    cmds.menuItem(l='GPU Override:', divider=True)
    cmds.menuItem(l='On', c="mel.eval('turnOnOpenCLEvaluatorActive')")
    cmds.menuItem(l='Off', c="mel.eval('turnOffOpenCLEvaluatorActive')")

    cmds.setParent("..")

    # Show Frame Rate / Update View Active
    cmds.checkBoxGrp("HUDFrameRate", numberOfCheckBoxes=2,
                     label1="HUD Frame Rate",
                     onCommand1="mel.eval ('setFrameRateVisibility 1')",
                     offCommand1="mel.eval ('setFrameRateVisibility 0')",

                     label2="Update View Active",
                     onCommand2="cmds.playbackOptions (v='active')",
                     offCommand2="cmds.playbackOptions (v='all')")
    cmds.setParent("..")

    # ==================================================================
    # Extra Utilities
    cmds.frameLayout("extraUtilitiesTab", l="Extra Utilities", marginHeight=5, marginWidth=5, collapse=True,
                     collapsable=True,
                     collapseCommand="cmds.window (\"FCM_Proxy_Maker_Window\", edit=True, h=2, w=2)")
    horizontal = 130
    horizontalColumn = 20
    cmds.rowLayout(numberOfColumns=2, columnAttach=[2, "both", horizontalColumn])
    cmds.text(l='Selection Tools', w=horizontal)
    cmds.text(l='Adv Tools', w=horizontal)

    cmds.setParent("..")

    # Unlock All Vis Meshes / toggle node state
    cmds.rowLayout(numberOfColumns=2, columnAttach=[2, "both", horizontalColumn])
    cmds.button(label="Select Vis Meshes", w=horizontal, c="selectAllVisibleMeshes()",
                ann='Select every visible mesh in the scene, if is hidded by layer display wont be selected, same if is hidded through ".lodVisibility"')
    cmds.button(l="Toggle Node State", w=horizontal, c="toggleNodeState()",
                ann='Toggle Node State from tab Node Behaviour between "Normal" and "Has no effect"')
    cmds.setParent("..")
    # Select all vis meshes / Give me the type node
    cmds.rowLayout(numberOfColumns=2, columnAttach=[2, "both", horizontalColumn])
    cmds.button(label="Unlock Vis Meshes", w=horizontal, c="unlockAllVismeshes()",
                ann='If the mesh you need to select is unselectable and not by layerdisplay you should try this button')
    cmds.button(l="Give Me The Type Node", w=horizontal, c="giveMeTheType()",
                ann='Select any object in the scene and will print the object type')
    cmds.setParent("..")
    # All nodes From Sel / Print blocking nodes
    cmds.rowLayout(numberOfColumns=2, columnAttach=[2, "both", horizontalColumn])
    cmds.button(label="All Nodes From Sel", w=horizontal, c="getAllNodesSceneFromSelection()",
                ann="Get All nodes From Selection")
    cmds.button(label="Print Blocking Nodes", w=horizontal, c="printBlockingNodes()",
                ann="Print all nodes are blocking parallel")
    cmds.setParent("..")
    # Select Most Complex Mesh / Empty
    cmds.rowLayout(numberOfColumns=2, columnAttach=[2, "both", horizontalColumn])
    cmds.button(label="Sel Most Complex Mesh", w=horizontal, c="selectMostComplexMesh()",
                ann='Select the mesh with more nodes attached in the scene, great for analize it or frozen it')
    cmds.rowLayout(numberOfColumns=2)
    anchito = 63
    cmds.button(label="Frozen", w=anchito, c="frozenAllSelected()",
                ann='Turn On the attribute Frozen for every selection')
    cmds.button(label="UnFrozen", w=anchito, c="unFrozenAllSelected()",
                ann='Turn OFF the attribute Frozen for every selection')
    cmds.setParent("..")

    cmds.setParent("..")
    # Select Frozen Nodes / Empty
    cmds.rowLayout(numberOfColumns=1, columnAttach=[2, "both", horizontalColumn])
    cmds.button(label="Sel Frozen Nodes", w=horizontal, c="cmds.warning('WIP, Sorry!')")

    cmds.setParent("..")

    cmds.setParent("..")
    cmds.setParent("..")

    # ==================================================================

    cmds.showWindow(windowProxyMaker)

    # Resize window
    cmds.window("FCM_Proxy_Maker_Window", edit=True, w=2, h=2)

    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''
                Check Functions
                
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    # Show Proxy
    if cmds.objExists("Set_Proxy"):
        try:
            cmds.select("Set_Proxy")
            sel = cmds.ls(sl=True)
            if cmds.getAttr(sel[0] + ".visibility") == 1:  # I need only the first index to have the correct return
                cmds.checkBoxGrp("ShowProxy", edit=True, value1=True)
            else:
                cmds.checkBoxGrp("ShowProxy", edit=True, value1=False)
            cmds.select(clear=True)
        except:
            pass
    # Show Proxy Del Rig
    '''
    if cmds.objExists ("Folder_Proxys"):
        if cmds.getAttr ('Folder_Proxys.visibility'):
            cmds.checkBoxGrp ("ShowProxyDelRig", edit=True, value1=True)
        else:
            cmds.checkBoxGrp ("ShowProxyDelRig", edit=True, value1=False)
    '''

    # Show Rig
    if cmds.objExists("Set_Rig"):
        cmds.select("Set_Rig")
        if cmds.getAttr(".visibility") == 1:
            cmds.checkBoxGrp("ShowProxy", edit=True, value2=True)
        else:
            cmds.checkBoxGrp("ShowProxy", edit=True, value2=False)
        cmds.select(clear=True)
    # Symmetry X
    if cmds.symmetricModelling(q=True, symmetry=True) == 1:
        cmds.checkBoxGrp("ChechboxGroup1", edit=True, value1=True)
    else:
        cmds.checkBoxGrp("ChechboxGroup1", edit=True, value1=False)
        # HUD FrameRate
    if mel.eval('optionVar -q frameRateVisibility') == 1:
        cmds.checkBoxGrp("HUDFrameRate", edit=True, value1=True)
    else:
        cmds.checkBoxGrp("HUDFrameRate", edit=True, value1=False)
        # Update View Active
    if cmds.playbackOptions(q=True, v=True) == "active":
        cmds.checkBoxGrp("HUDFrameRate", edit=True, value2=True)
    else:
        cmds.checkBoxGrp("HUDFrameRate", edit=True, value2=False)
        # Check Save After Loading

    if cmds.objExists("FCM_Proxy_Maker_Settings"):
        if cmds.getAttr("FCM_Proxy_Maker_Settings.Save_After_Loading") == 1:
            cmds.checkBoxGrp("SaveAfterLoading", edit=True, value1=True)
        else:
            cmds.checkBoxGrp("SaveAfterLoading", edit=True, value1=False)
            # Option 1 Vis
    if cmds.getAttr("FCM_Proxy_Maker_Settings.Option_1_Vis"):
        cmds.frameLayout('keepOriginalRig', e=True, collapse=False)
    else:
        cmds.frameLayout('keepOriginalRig', e=True, collapse=True)

    # Option 2 Vis
    if cmds.getAttr("FCM_Proxy_Maker_Settings.Option_2_Vis"):
        cmds.frameLayout('DeleteOriginalRig', e=True, collapse=False)
    else:
        cmds.frameLayout('DeleteOriginalRig', e=True, collapse=True)

    # Deform Manager Vis
    if cmds.getAttr("FCM_Proxy_Maker_Settings.deformManager_Vis"):
        cmds.frameLayout('deformManagerTab', e=True, collapse=False)
    else:
        cmds.frameLayout('deformManagerTab', e=True, collapse=True)
        ####### Node Manager #######
    # HeavyMeshes
    if cmds.getAttr('FCM_Proxy_Maker_Settings.HeavyMeshConnected_State') == 0:
        cmds.checkBoxGrp('NodesCheckbox1', edit=True, value1=False)
    # BlendShape
    if cmds.getAttr('FCM_Proxy_Maker_Settings.blendShape_State') == 0:
        cmds.checkBoxGrp('NodesCheckbox1', edit=True, value2=False)
    # Wire
    if cmds.getAttr('FCM_Proxy_Maker_Settings.wire_State') == 0:
        cmds.checkBoxGrp('NodesCheckbox1', edit=True, value3=False)

    # Wrap
    if cmds.getAttr('FCM_Proxy_Maker_Settings.wrap_State') == 0:
        cmds.checkBoxGrp('NodesCheckbox2', edit=True, value1=False)
    # PolySmoothFace
    if cmds.getAttr('FCM_Proxy_Maker_Settings.polySmoothFace_State') == 0:
        cmds.checkBoxGrp('NodesCheckbox2', edit=True, value2=False)
    # DeltaMush
    if cmds.getAttr('FCM_Proxy_Maker_Settings.deltaMush_State') == 0:
        cmds.checkBoxGrp('NodesCheckbox2', edit=True, value3=False)

    # Ffd
    if cmds.getAttr('FCM_Proxy_Maker_Settings.ffd_State') == 0:
        cmds.checkBoxGrp('NodesCheckbox3', edit=True, value1=False)
    # Tension
    if cmds.getAttr('FCM_Proxy_Maker_Settings.tension_State') == 0:
        cmds.checkBoxGrp('NodesCheckbox3', edit=True, value2=False)
    # PolySoftEdge
    if cmds.getAttr('FCM_Proxy_Maker_Settings.polySoftEdge_State') == 0:
        cmds.checkBoxGrp('NodesCheckbox3', edit=True, value3=False)

    # polyMapCut
    if cmds.getAttr('FCM_Proxy_Maker_Settings.polyMapCut_State') == 0:
        cmds.checkBoxGrp('NodesCheckbox4', edit=True, value1=False)
    # polyTweakUV
    if cmds.getAttr('FCM_Proxy_Maker_Settings.polyTweakUV_State') == 0:
        cmds.checkBoxGrp('NodesCheckbox4', edit=True, value2=False)
    # polyPlanarProj
    if cmds.getAttr('FCM_Proxy_Maker_Settings.polyPlanarProj_State') == 0:
        cmds.checkBoxGrp('NodesCheckbox4', edit=True, value3=False)

    # skinCluster
    if cmds.getAttr('FCM_Proxy_Maker_Settings.skinCluster_State') == 0:
        cmds.checkBoxGrp('NodesCheckbox5', edit=True, value1=False)
    # Cluster
    if cmds.getAttr('FCM_Proxy_Maker_Settings.cluster_State') == 0:
        cmds.checkBoxGrp('NodesCheckbox5', edit=True, value2=False)


# Open window twice to avoid annoying bug
ProxyMakerWindow()
ProxyMakerWindow()
# Sanity Check
sanityCheck()
