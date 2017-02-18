import json
import maya.OpenMaya as OpenMaya


def get_mObject(obj):
    sel = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getSelectionListByName(obj, sel)
    mObj = OpenMaya.MObject()
    sel.getDependNode(0, mObj)
    return mObj

def get_mDagPath(obj):
    sel = OpenMaya.MSelectionList()
    sel.add(obj)
    mDag = OpenMaya.MDagPath()
    sel.getDagPath(0, mDag)
    return mDag

def write_curve_info(obj):
    mObj = get_mObject(obj)

    mDag = OpenMaya.MDagPath()
    mDagFn = OpenMaya.MFnDagNode(mObj)
    mDagFn.getPath(mDag)

    numShapesUtil = OpenMaya.MScriptUtil()
    numShapesUtil.createFromInt(0)
    numShapesPtr = numShapesUtil.asUintPtr()
    mDag.numberOfShapesDirectlyBelow(numShapesPtr)
    num_shape_nodes = OpenMaya.MScriptUtil(numShapesPtr).asUint()

    # ToDo: loop through all shape nodes under a transform
    mDag.extendToShapeDirectlyBelow(0)
    shape_mObj = mDag.node()

    if shape_mObj.apiTypeStr() == 'kNurbsCurve':
        pointArray = OpenMaya.MPointArray()
        curveFn = OpenMaya.MFnNurbsCurve(mDag)
        curveFn.getCVs(pointArray, OpenMaya.MSpace.kWorld)

        cv_pos_list = []
        override_color = OpenMaya.MFnDependencyNode(shape_mObj).findPlug('overrideColor').asInt()
        curve_info_dict = {mDag.partialPathName(): {'cv_position': cv_pos_list, 'override_color': override_color}}

        for i in range(pointArray.length()):
            cv_pos_list.append([pointArray[i].x, pointArray[i].y, pointArray[i].z])

    return curve_info_dict

def read_curve_info(data):
    for key, value in data.items():
        mDag = get_mDagPath(key)
        mObj = get_mObject(key)
        curveFn = OpenMaya.MFnNurbsCurve(mDag)
        pointArray = OpenMaya.MPointArray()

        # Set override color
        dependNodeFn = OpenMaya.MFnDependencyNode(mObj)
        colorPlug = dependNodeFn.findPlug('overrideColor')
        colorPlug.setInt(value['override_color'])

        # Set cv positions
        for index, i in enumerate(value['cvs']):
            pointArray.append(i[0], i[1], i[2], 1.0)

        curveFn.setCVs(pointArray, OpenMaya.MSpace.kWorld)
        curveFn.updateCurve()

def export_curve_data(objs, file_path):
    data = None
    for obj in objs:
        if data:
            data.update(write_curve_info(obj))
        else:
            data = write_curve_info(obj)

    with open(file_path, 'w') as out_file:
        json.dump(data, out_file)


def import_curve_data(file_path):
    with open(file_path, 'r') as in_file:
        data = json.load(in_file)

    read_curve_info(data)


#FILE_PATH = 'c:/users/Tom/Programming/curves.json'
#curves = ['nurbsCircle1', 'nurbsCircle2', 'nurbsCircle3', 'nurbsCircle4']
#export_curve_data(curves, FILE_PATH)
#import_curve_data(FILE_PATH)
