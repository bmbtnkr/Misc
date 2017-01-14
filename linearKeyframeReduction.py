# Example usage:
# linear_keyframe_reduction('character_rig:hip_ctrl', 'hip_ctrl_translateY', epsilon=0.01)

from collections import OrderedDict

def lerp(v0, v1, t):
    return ((1-t)*v0) + (t*v1)

def linear_keyframe_reduction(obj, anim_curve=None, epsilon=0.01):
    anim_curves = cmds.keyframe(obj, name=True, query=True) if not anim_curve else [anim_curve]

    for anim_curve in anim_curves:
        time_values = cmds.keyframe(anim_curve, timeChange=True, query=True)
        key_values = cmds.keyframe(anim_curve, valueChange=True, query=True)
        curve_dict = dict(zip(time_values, key_values))
        ordered_curve_dict = OrderedDict(curve_dict.items())
        delete_key_index = []

        for key, value in ordered_curve_dict.items():
            try:
                if key == min(ordered_curve_dict.keys()) or key == max(ordered_curve_dict.keys()):
                    continue

                curr_frame = ordered_curve_dict.keys()[ordered_curve_dict.keys().index(key)]
                prev_frame = ordered_curve_dict.keys()[ordered_curve_dict.keys().index(curr_frame)-1]
                next_frame = ordered_curve_dict.keys()[ordered_curve_dict.keys().index(curr_frame)+1]

                curr_value = curve_dict[curr_frame]
                prev_value = curve_dict[prev_frame]
                next_value = curve_dict[next_frame]

                alpha = (curr_frame - prev_frame) / (next_frame - prev_frame)

                if abs(curve_dict[curr_frame] - lerp(prev_value, next_value, alpha)) < epsilon:
                    delete_key_index.append((curr_frame,))

            except IndexError, KeyError:
                print 'Failed to remove keyframe from: %s on frame: %s' % (anim_curve, key)
                continue

        if delete_key_index:
            delete_key_index.remove(delete_key_index[0])
            attr = cmds.listConnections(anim_curve, s=1, d=1, p=1)
            cmds.cutKey(obj, attribute=attr[0].rpartition('.')[-1], time=delete_key_index)
