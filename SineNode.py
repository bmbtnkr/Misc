# import maya.cmds as cmds
# cmds.unloadPlugin("SineNode.py")
# cmds.loadPlugin("SineNode.py")

# sineNode = cmds.createNode("tbSineNode")
# sphere = cmds.polySphere()
# cmds.connectAttr("time1.outTime", "%s.input" % sineNode)
# cmds.connectAttr("%s.output" % sineNode, "%s.translateY" % sphere[0])

import math
import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeTypeName = "tbSineNode"
kPluginNodeTypeId = OpenMaya.MTypeId(0x870001)


class sineNode(OpenMayaMPx.MPxNode):
    # Class attributes
    aInput = OpenMaya.MObject()
    aOutput = OpenMaya.MObject()
    aAmplitude = OpenMaya.MObject()
    aFrequency = OpenMaya.MObject()

    # Constructor
    def __init__(self):
            OpenMayaMPx.MPxNode.__init__(self)

    # Compute method
    def compute(self, plug, block):
        if (plug == sineNode.aOutput):
            inputValue = block.inputValue(sineNode.aInput).asFloat()

            amplitudeValue = block.inputValue(sineNode.aAmplitude).asFloat()
            frequencyValue = block.inputValue(sineNode.aFrequency).asFloat()

            # Our actual compute
            result = math.sin(inputValue * frequencyValue) * amplitudeValue

            outputHandle = block.outputValue(sineNode.aOutput)
            outputHandle.setFloat(result)

            block.setClean(plug)
        return OpenMaya.kUnknownParameter


def nodeCreator():
    """ Create an instance of our command """
    return OpenMayaMPx.asMPxPtr(sineNode())


def nodeInitializer():
    nAttr = OpenMaya.MFnNumericAttribute()
    sineNode.aInput = nAttr.create("input", "in", OpenMaya.MFnNumericData.kFloat, 1.0)
    nAttr.setStorable(True)
    nAttr.setHidden(False)
    nAttr.setKeyable(False)

    sineNode.aAmplitude = nAttr.create("amplitude", "amp", OpenMaya.MFnNumericData.kFloat, 1.0)
    nAttr.setStorable(True)
    nAttr.setHidden(False)
    nAttr.setKeyable(True)

    sineNode.aFrequency = nAttr.create("frequency", "fre", OpenMaya.MFnNumericData.kFloat, 1.0)
    nAttr.setStorable(True)
    nAttr.setHidden(False)
    nAttr.setKeyable(True)

    sineNode.aOutput = nAttr.create("output", "out", OpenMaya.MFnNumericData.kFloat, 0.0)
    nAttr.setStorable(True)
    nAttr.setWritable(True)

    try:
        # Add attributes
        sineNode.addAttribute(sineNode.aInput)
        sineNode.addAttribute(sineNode.aAmplitude)
        sineNode.addAttribute(sineNode.aFrequency)
        sineNode.addAttribute(sineNode.aOutput)

        # Add attribute affects
        sineNode.attributeAffects(sineNode.aInput, sineNode.aOutput)
        sineNode.attributeAffects(sineNode.aAmplitude, sineNode.aOutput)
        sineNode.attributeAffects(sineNode.aFrequency, sineNode.aOutput)
    except Exception, e:
        sys.stderr.write("Failed to create attributes of %s node\n" % kPluginNodeTypeName)
        sys.stderr.write('%s\n' % e)


def initializePlugin(mobject):
    """ Load the plugin and register defined classes """
    mplugin = OpenMayaMPx.MFnPlugin(mobject, "Tom Banker", "1.0", "Any")
    try:
        mplugin.registerNode(kPluginNodeTypeName, kPluginNodeTypeId, nodeCreator, nodeInitializer)
    except Exception, e:
        sys.stderr.write("Failed to register node: %s\n" % kPluginNodeTypeName)
        sys.stderr.write("%s\n" % e)


def uninitializePlugin(mobject):
    """ Unload the plugin and unregister defined classes """
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode(kPluginNodeTypeId)
    except Exception, e:
        sys.stderr.write("Failed to unregister node: %s\n" % kPluginNodeTypeName)
        sys.stderr.write("%s\n" % e)
