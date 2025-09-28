# -*- coding: UTF-8 -*-

'''
生成したバインド用のジョイントをまとめている。
'''

'''
import sys

absolute_path = "C:/Users/meidm/Desktop/body_rig_all/AutoRigHierarchySetup"
sys.path.append(absolute_path)

import AutoRigHierarchySetup
import importlib
importlib.reload(AutoRigHierarchySetup)
AutoRigHierarchySetup.main()
'''

import maya.cmds as cmds

def arm_leg_parent(num):
    part = num
    cmds.parent('bin_thoumb_A_jt_' + chr(part), 'bin_hand_jt_' + chr(part))
    cmds.parent('bin_finger_A_jt_' + chr(part), 'bin_hand_jt_' + chr(part))
    cmds.parent('bin_middle_A_jt_' + chr(part), 'bin_hand_jt_' + chr(part))
    cmds.parent('bin_ring_A_jt_' + chr(part), 'bin_hand_jt_' + chr(part))
    cmds.parent('bin_little_A_jt_' + chr(part), 'bin_hand_jt_' + chr(part))
    cmds.parent('bin_hand_jt_' + chr(part), 'bin_loArm4_jt_' + chr(part))
    cmds.parent('bin_upArm1_jt_' + chr(part), 'bin_shoulder_jt_' + chr(part))
    cmds.parent('bin_shoulder_jt_' + chr(part), 'bin_spine_4_jt')
    cmds.parent('bin_ankle_jt_' + chr(part), 'bin_loLeg4_jt_' + chr(part))
    cmds.parent('bin_upLeg1_jt_' + chr(part), 'bin_spine_1_jt')

def main():
    arm_leg_parent(76)
    arm_leg_parent(82)
    cmds.parent('bin_head_0_jt', 'bin_neck_1_jt')
    cmds.parent('bin_neck_0_jt', 'bin_spine_4_jt')
    
    cmds.select(cl=True)
    cmds.joint(n = 'bind_scale')
    cmds.parent('bin_spine_0_jt', 'bind_scale')
    cmds.parent('bind_scale', 'rig_grp')
    
    sel = cmds.listRelatives('bind_scale', ad=True, type='joint')
    for s in sel:
        cmds.setAttr(s + ".segmentScaleCompensate", 0)
    
#main()