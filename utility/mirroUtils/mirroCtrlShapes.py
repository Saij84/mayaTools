import maya.cmds as cmds

def mirrorCtrlShapes():
    """
    Creates a mirror image of selected ctrl shape, if corresponding ctrl exists it
    will replace shape else create new ctrl.
    script is L/R agnostic.

    REQUIREMENT:
    - '_L_' or '_R_' must be part of the name

    :return: None
    """
    negXPos = []

    for crv in cmds.ls(sl=True):
        crvRelative = [crvShape for crvShape in cmds.listRelatives(crv) if cmds.objectType(crvShape)][0]

        toReplace = "_L_"
        replacedTo = "_R_"
        if "_R_" in crvRelative:
            toReplace = "_R_"
            replacedTo = "_L_"

        targetCrv = crvRelative.replace(toReplace, replacedTo)

        numSpans = cmds.getAttr(crv + ".spans")
        degree = cmds.getAttr(crv + ".degree")

        for idx in range(numSpans+1):
            oriPos = cmds.getAttr(crv + ".cv[{}]".format(idx))[0]

            xPos_list = [oriPos[0] * -1]
            yzPos_list = list(oriPos[1:])

            negXPos.append(tuple(xPos_list + yzPos_list))

        if not cmds.objExists(targetCrv):
            crvName = crv.replace(toReplace, replacedTo)
            newCrv = cmds.curve(d=degree, p=negXPos)
            cmds.rename(newCrv, crvName)
            print("New Curve has been created: {}".format(crvName))
        else:
            cmds.curve(targetCrv, d=degree, r=True, p=negXPos)
            print("Exsisting Curve has been replaced: {}".format(targetCrv))
