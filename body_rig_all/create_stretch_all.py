# -*- coding: UTF-8 -*-

'''
3つのジョイントを選ぶ。
start endのロケータと、カーブはグループにしてcenter_ctrlの子にしておく
そのさい、endはIK_hand_ctrlへペアレントする。
distanceDimensionはまとめてグループにいれて、root_offsetとは別にしておく。
ジョイントの子がX方向を向いていること前提
'''

import maya.cmds as cmds

def create_stretch(top, middle, end):
    
    top_j = top
    middle_j = middle
    end_j = end

    start = cmds.spaceLocator(n = top_j + "_start")
    end = cmds.spaceLocator(n = end_j + "_end")
    
    cmds.matchTransform(start, top_j)
    cmds.matchTransform(end, end_j)
    
    jointA_position = cmds.xform(top_j, query=True, worldSpace=True, translation=True)
    jointC_position = cmds.xform(end_j, query=True, worldSpace=True, translation=True)
    
    # Distance Dimensionノードを作成
    distance_dimension_shape = cmds.distanceDimension(sp=jointA_position, ep=jointC_position)
    dis_T = cmds.ls(sl=True)[1] #distanceDimensionが生成されたときに現状選択されているものを利用してトランスフォームノードを選択している。
    cmds.parent(dis_T, 'stretch_distance_gp')
    
    # jointAとjointCに沿ったカーブを作成
    curve = cmds.curve(p=[cmds.xform(start, query=True, worldSpace=True, translation=True), cmds.xform(end, query=True, worldSpace=True, translation=True)], degree=1)
    curve_T = cmds.ls(sl=True)[0]
    cmds.parent(curve_T, 'stretch_curve_gp')
    
    curve_info = cmds.createNode('curveInfo')
    cmds.connectAttr(curve + '.worldSpace[0]', curve_info + '.inputCurve')
    
    mult_divide_node = cmds.shadingNode("multiplyDivide", asUtility=True, name="mult_divide_node")
    
    cmds.connectAttr(curve_info + ".arcLength", mult_divide_node + ".input2X")
    
    cmds.connectAttr(distance_dimension_shape + ".distance", mult_divide_node + ".input1X")
    
    cmds.setAttr(mult_divide_node + ".operation", 2)  # 2 は割り算を表します
    
    condition_node = cmds.shadingNode("condition", asUtility=True)
    
    cmds.connectAttr(mult_divide_node + ".outputX", condition_node + ".colorIfTrueR")
    
    cmds.connectAttr(distance_dimension_shape + ".distance", condition_node + ".firstTerm")
    
    cmds.setAttr(condition_node + ".operation", 2)  # 2 はGreater Thanを表します
    
    cmds.connectAttr(curve_info + ".arcLength", condition_node + ".secondTerm")
    
    # ConditionノードのoutColorRをjointA, jointB, jointCのscaleXに接続
    cmds.connectAttr(condition_node + ".outColorR", top_j + ".scaleX")
    cmds.connectAttr(condition_node + ".outColorR", middle_j + ".scaleX")
    cmds.connectAttr(condition_node + ".outColorR", end_j + ".scaleX")
    
    # 結果を取得
    result = cmds.getAttr(condition_node + ".outColorR")
    print("Condition result:", result)


def other_parent():
    cmds.parent('IK_arm_jt_L_start', 'IK_shoulder_L_ctrl')
    cmds.parent('IK_wrist_jt_L_end', 'IK_hand_L_ctrl')
    cmds.parent('IK_arm_jt_R_start', 'IK_shoulder_R_ctrl')
    cmds.parent('IK_wrist_jt_R_end', 'IK_hand_R_ctrl')

def stretch_gp():
    cmds.createNode('transform', n='stretch_curve_gp', p='controls_grp')
    cmds.createNode('transform', n='stretch_distance_gp', p='rig_grp')
    
def main():
    stretch_gp()
    create_stretch('IK_arm_jt_L', 'IK_elbow_jt_L', 'IK_wrist_jt_L')
    create_stretch('IK_arm_jt_R', 'IK_elbow_jt_R', 'IK_wrist_jt_R')
    other_parent()
    
