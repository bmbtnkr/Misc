"""
Aim Constraint DG Node
Author: Tom Banker
Contact: tombanker@gmail.com
Date: September 27, 2014

Useage:

import maya.cmds as cmds
cmds.loadPlugin('tbAimConstraint.py')

cmds.file(new=1, force=1)
con = cmds.spaceLocator(n='con')
cmds.xform(con, t=[1,1,3])

aim = cmds.spaceLocator(n='aim')
cmds.xform(aim, t=[2,1,1])

up = cmds.spaceLocator(n='up')
cmds.xform(up, t=[2,10,1])

aimNode = cmds.createNode('tbAimConstraint')

cmds.connectAttr(con[0]+'.worldMatrix[0]', aimNode+'.constraintMatrix')
cmds.connectAttr(aim[0]+'.worldMatrix[0]', aimNode+'.aimMatrix')
cmds.connectAttr(up[0]+'.worldMatrix[0]', aimNode+'.worldUpMatrix')
cmds.connectAttr(aimNode+'.constraintRotate', con[0]+'.rotate')
"""

import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import math


class AimNode(OpenMayaMPx.MPxNode):
    # Command variables
    kPluginNodeName = 'tbAimConstraint'
    kPluginNodeId = OpenMaya.MTypeId(0x112233)

    aInputCon = OpenMaya.MObject()
    aInputAim = OpenMaya.MObject()
    aInputUp = OpenMaya.MObject()
    aOutput = OpenMaya.MObject()

    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    def compute(self, plug, data):
        if plug != AimNode.aOutput:
            return OpenMaya.kUnknownParameter

        conMatrixInput = data.inputValue(AimNode.aInputCon).asMatrix()
        aimMatrixInput = data.inputValue(AimNode.aInputAim).asMatrix()
        upMatrixInput = data.inputValue(AimNode.aInputUp).asMatrix()

        conMatrixValue = OpenMaya.MTransformationMatrix(conMatrixInput)
        aimMatrixValue = OpenMaya.MTransformationMatrix(aimMatrixInput)
        upMatrixValue = OpenMaya.MTransformationMatrix(upMatrixInput)

        # Get the translation component from world matrix as a vector
        conWorldTransVector = conMatrixValue.getTranslation(OpenMaya.MSpace.kWorld)
        aimWorldTransVector = aimMatrixValue.getTranslation(OpenMaya.MSpace.kWorld)
        upWorldTransVector = upMatrixValue.getTranslation(OpenMaya.MSpace.kWorld)

        # Get the aim vector
        aimVector = OpenMaya.MFloatVector(aimWorldTransVector - conWorldTransVector)
        aimVector.normalize()

        # Get the up vector
        upVector = OpenMaya.MFloatVector(upWorldTransVector - conWorldTransVector)
        upDot = aimVector * upVector
        upVector = upVector - aimVector * upDot
        upVector.normalize()

        # Get the side vector
        sideVector = aimVector ^ upVector
        sideVector.normalize()

        # Create a matrix, set the rows to result vectors
        resultMatrix = OpenMaya.MMatrix()
        setRow(resultMatrix, aimVector, 0)
        setRow(resultMatrix, upVector, 1)
        setRow(resultMatrix, sideVector, 2)

        # Get result rotation in radians
        matrixTrans = OpenMaya.MTransformationMatrix(resultMatrix)
        eulerRot = matrixTrans.eulerRotation()
        
        # Convert to degrees
        angles = [math.degrees(angle) for angle in (eulerRot.x, eulerRot.y, eulerRot.z)]

        # Connect result rotation to output plug
        hOutput = data.outputValue(AimNode.aOutput)
        hOutput.set3Float(angles[0], angles[1], angles[2])
        data.setClean(plug)

# Utility function
def setRow(matrix, newVector, row):
    OpenMaya.MScriptUtil.setDoubleArray(matrix[row], 0, newVector.x)
    OpenMaya.MScriptUtil.setDoubleArray(matrix[row], 1, newVector.y)
    OpenMaya.MScriptUtil.setDoubleArray(matrix[row], 2, newVector.z)

def creator():
    return OpenMayaMPx.asMPxPtr(AimNode())

def initialize():
    nAttr = OpenMaya.MFnNumericAttribute()
    mAttr = OpenMaya.MFnMatrixAttribute()
    uAttr = OpenMaya.MFnUnitAttribute()

    AimNode.aInputCon = mAttr.create('constraintMatrix', 'constraintMatrix', OpenMaya.MFnMatrixAttribute.kDouble)
    mAttr.setWritable(True)
    mAttr.setStorable(True)
    mAttr.setReadable(True)
    mAttr.setKeyable(True)
    mAttr.setHidden(False)

    AimNode.aInputAim = mAttr.create('aimMatrix', 'aimMatrix', OpenMaya.MFnMatrixAttribute.kDouble)
    mAttr.setWritable(True)
    mAttr.setStorable(True)
    mAttr.setReadable(True)
    mAttr.setKeyable(True)
    mAttr.setHidden(False)

    AimNode.aInputUp = mAttr.create('worldUpMatrix', 'worldUpMatrix', OpenMaya.MFnMatrixAttribute.kDouble)
    mAttr.setWritable(True)
    mAttr.setStorable(True)
    mAttr.setReadable(True)
    mAttr.setKeyable(True)
    mAttr.setHidden(False)

    AimNode.aOutput = nAttr.createPoint("constraintRotate", "constraintRotate")
    mAttr.setWritable(True)
    mAttr.setStorable(True)
    mAttr.setReadable(True)
    mAttr.setKeyable(True)
    mAttr.setHidden(False)

    AimNode.addAttribute(AimNode.aInputCon)
    AimNode.addAttribute(AimNode.aInputAim)
    AimNode.addAttribute(AimNode.aInputUp)
    AimNode.addAttribute(AimNode.aOutput)

    AimNode.attributeAffects(AimNode.aInputCon, AimNode.aOutput)
    AimNode.attributeAffects(AimNode.aInputAim, AimNode.aOutput)
    AimNode.attributeAffects(AimNode.aInputUp, AimNode.aOutput)

def initializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj, 'Tom Banker', '1.5', 'Any')
    try:
        plugin.registerNode('tbAimConstraint', AimNode.kPluginNodeId, creator, initialize)
    except:
        raise RuntimeError, 'Failed to register node'

def uninitializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj)
    try:
        plugin.deregisterNode(AimNode.kPluginNodeId)
    except:
        raise RuntimeError, 'Failed to register node'
