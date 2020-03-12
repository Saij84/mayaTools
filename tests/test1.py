import maya.api.OpenMaya as om2

mtx = [
    1, 2, 3, 4,
    5, 6, 7, 8,
    9, 10, 11, 12,
    13, 14, 15, 16
]
mMtx = om2.MMatrix(mtx)


test = [0.0, 0.0, 0.1]

if not sum(test) + 0.0:
   print("YES")