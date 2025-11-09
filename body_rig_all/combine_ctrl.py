# -*- coding: UTF-8 -*-

'''
ボディとそのほかのコントローラを組み合わせる。
'''

'''
import sys

absolute_path = "C:/Users/meidm/Desktop/body_rig_all/combine_ctrl_all"
sys.path.append(absolute_path)

import combine_ctrl
import importlib
importlib.reload(combine_ctrl)
combine_ctrl.main()
'''

import maya.cmds as cmds
import math


import maya.cmds as cmds

def create_switch(target, first, second, switch, flag, default):
    """
    複数のターゲット間でスイッチを作成し、特定の属性を用いて切り替えを管理する。
    
    Parameters:
        target (list): ターゲットオブジェクトのリスト
        first (str): 最初の対象オブジェクト
        second (str): 第二の対象オブジェクト
        switch (str): スイッチ用の文字列 (例: 'Head:Chest:Root')
        flag (int): コンストレインの種類 (0: すべて, 1: 回転のみ)
        default (int): デフォルトのスイッチ値
    """
    if not target or len(target) < 1:
        raise ValueError("Target list must contain at least one valid object.")
    if not cmds.objExists(first) or not cmds.objExists(second):
        raise ValueError("Objects '{}' or '{}' do not exist in the scene.".format(first, second))

    # 初期ワールドスペース位置を保存
    initial_matrix = cmds.xform(first, q=True, ws=True, m=True)

    # 属性を追加
    if not cmds.attributeQuery('follow', node=first, exists=True):
        cmds.addAttr(first, ln='follow', at='long', defaultValue=0)
        cmds.setAttr("{}.follow".format(first), e=True, keyable=True)
    if not cmds.attributeQuery('orient', node=second, exists=True):
        cmds.addAttr(second, ln='orient', at='enum', en=switch)
        cmds.setAttr("{}.orient".format(second), e=True, keyable=True)

    # 属性を接続
    cmds.connectAttr("{}.orient".format(second), "{}.follow".format(first))

    # ペアレントコンストレイン作成
    if flag == 0:
        pc = cmds.parentConstraint(target[0], first, mo=True)[0]
    elif flag == 1:
        pc = cmds.parentConstraint(target[0], first, st=['x', 'y', 'z'], mo=True)[0]

    # 残りのターゲットをペアレントコンストレインに追加し、ウェイトを均等化
    weight_per_target = 1.0 / len(target)  # 均等なウェイト計算
    for t in target[1:]:
        cmds.parentConstraint(t, first, e=True, weight=weight_per_target, mo=True)

    # スイッチ用の condition ノードを作成し、ターゲットごとに接続
    for i, t in enumerate(target):
        z_cd = cmds.createNode('condition', n='Zcondition_{}'.format(i))
        cmds.setAttr("{}.secondTerm".format(z_cd), i)
        cmds.setAttr("{}.colorIfTrueR".format(z_cd), 1)
        cmds.setAttr("{}.colorIfFalseR".format(z_cd), 0)
        cmds.connectAttr("{}.follow".format(first), "{}.firstTerm".format(z_cd))
        cmds.connectAttr("{}.outColorR".format(z_cd), "{}.{}W{}".format(pc, t, i))

    # デフォルト値を設定
    cmds.setAttr("{}.orient".format(second), default)

    # 初期ワールドスペースの位置と回転を復元
    cmds.xform(first, ws=True, m=initial_matrix)

    # 選択をクリア
    cmds.select(cl=True)





def arm_connection(num):
    part = num #L is 76. R is 82.
    
    ###腕
    arm_p_n = ['shoulder_' + chr(part) + '_ctrl', 'spine_micro_4_ctrl', 'center_sub_ctrl', 'root_ctrl']
    
    #cmds.parentConstraint(arm_p_n[1], 'IK_hand_' + chr(part) + '_offset', mo=True)
    #cmds.parentConstraint(arm_p_n[1], 'IK_hand_twist_' + chr(part) + '_offset', mo=True)
    
    cmds.parentConstraint(arm_p_n[1], 'shoulder_' + chr(part) + '_offset', mo=True)
    
    
    #FK
    arm_first = 'arm_' + chr(part) + '_ctrlSpace'
    arm_second = 'arm_' + chr(part) + '_ctrl'
    arm_target = 'Shoulder:Chest:CS:Root'
    create_switch(arm_p_n, arm_first, arm_second, arm_target, 1, 1)
        
    #IK
    IK_hand_p_n = ['head_ctrl', 'shoulder_' + chr(part) + '_ctrl', 'spine_micro_4_ctrl', 'center_sub_ctrl', 'root_ctrl', 'rig_grp']
    IK_hand_first = 'IK_hand_' + chr(part) + '_offset'
    IK_hand_second = 'IK_hand_' + chr(part) + '_ctrl'
    IK_hand_target = 'Head:Shoulder:Chest:CS:Root:World'
    create_switch(IK_hand_p_n, IK_hand_first, IK_hand_second, IK_hand_target, 0, 2)
    
    IK_twist_p_n = ['shoulder_' + chr(part) + '_ctrl', 'spine_micro_4_ctrl', 'center_sub_ctrl', 'root_ctrl']
    IK_twist_first = 'IK_hand_twist_' + chr(part) + '_offset'
    IK_twist_second = 'IK_hand_twist_' + chr(part) + '_ctrl'
    IK_twist_target = 'Shoulder:Chest:CS:Root'
    create_switch(IK_twist_p_n, IK_twist_first, IK_twist_second, IK_twist_target, 0, 2)
    
    cmds.select(cl=True)
        
    
def leg_ready():
    l_h_upLOC = cmds.createNode('transform', n='leg_hip_upLOC')
    cmds.parent(l_h_upLOC, 'leg_ctrl_grp')
    cmds.parentConstraint('spine_micro_1_ctrl', l_h_upLOC)

def leg_connection(num):
    part = num #L is 76. R is 82.
    
    ###足
    LR_l_h_upLOC = cmds.createNode('transform', n=chr(part)+'_leg_hip_upLOC')
    cmds.matchTransform(LR_l_h_upLOC, chr(part)+'_leg_bendy_ctrl_A_grp')
    cmds.parent(LR_l_h_upLOC, 'leg_hip_upLOC')
    cmds.parent(chr(part) + '_upLeg_bendy_space_LOC', LR_l_h_upLOC)
    
    cmds.parentConstraint('spine_micro_0_ctrl', 'IK_' + chr(part) + '_leg_hip_offset', mo=True)
    
    cmds.parentConstraint('spine_micro_0_ctrl', 'leg_' + chr(part) + '_offset', sr=['x','y','z'], mo=True)
    
    
    #FK
    leg_p_n = ['spine_micro_0_ctrl', 'center_sub_ctrl', 'root_ctrl', 'rig_grp']
    leg_first = 'leg_' + chr(part) + '_ctrlSpace'
    leg_second = 'leg_' + chr(part) + '_ctrl'
    leg_target = 'Hip:CS:Root:World'
    create_switch(leg_p_n, leg_first, leg_second, leg_target, 1, 0)  
    
    #IK
    IK_ankle_p_n = ['spine_micro_0_ctrl', 'center_sub_ctrl', 'root_ctrl', 'rig_grp']
    IK_ankle_first = 'IK_' + chr(part) + '_ankle_offset'
    IK_ankle_second = 'IK_' + chr(part) + '_ankle_ctrl'
    IK_ankle_target = 'Hip:CS:Root:World'
    create_switch(IK_ankle_p_n, IK_ankle_first, IK_ankle_second, IK_ankle_target, 0, 2)
    
    IK_poleVector_p_n = ['IK_' + chr(part) + '_ankle_ctrl', 'spine_micro_0_ctrl', 'center_sub_ctrl', 'root_ctrl', 'rig_grp']
    IK_poleVector_first = 'IK_' + chr(part) + '_leg_poleVector_offset'
    IK_poleVector_second = 'IK_' + chr(part) + '_leg_poleVector_ctrl'
    IK_poleVector_target = 'Foot:Hip:CS:Root:World'
    create_switch(IK_poleVector_p_n, IK_poleVector_first, IK_poleVector_second, IK_poleVector_target, 0, 2)
    
def neck_connection():
    #首
    neck_p_n = ['spine_micro_4_ctrl', 'center_sub_ctrl', 'root_ctrl', 'rig_grp']
    cmds.parentConstraint(neck_p_n[0], 'neck_0_offset', mo=True) #
    neck_first = 'neck_0_ctrlSpace'
    neck_second = 'neck_0_ctrl'
    neck_target = 'Chest:CS:Root:World'
    create_switch(neck_p_n, neck_first, neck_second, neck_target, 1, 0)  
        
def head_connection():
    #頭
    head_p_n = ['neck_0_ctrl', 'center_sub_ctrl', 'root_ctrl', 'rig_grp']
    cmds.parentConstraint(head_p_n[0], 'head_offset', mo=True)#
    head_first = 'head_ctrlSpace'
    head_second = 'head_ctrl'
    head_target = 'Chest:CS:Root:World'
    create_switch(head_p_n, head_first, head_second, head_target, 1, 0)
    
def IKFK_condition(num):
    #IKFKの切り替え時のコントローラの表示非表示
    part = num #L is 76. R is 82

    a = 'IKFK_arm_' + chr(part)+ '_ctrl'   
    cd = cmds.shadingNode('condition', name='IKFK_arm_' + chr(part) + '_cd', asUtility=True)
    cmds.connectAttr(a + '.blend', cd + '.firstTerm')
    cmds.setAttr(cd + '.secondTerm', 0.5)
    cmds.setAttr(cd + '.operation', 4)
    cmds.setAttr(cd + '.colorIfTrueR', 1)
    cmds.setAttr(cd + '.colorIfFalseR', 0)
    cmds.connectAttr(cd + '.outColor.outColorR', a + '.arm_' + chr(part)+ '_IKFK')

    #FKコントローラの非表示
    #foot
    ikfk_foot_A = 'IKFK_leg_' + chr(part)+ '_ctrl' + '.leg_' + chr(part) + '_IKFK'
    foot_v = chr(part) + '_FK_leg_ctrl_grp' + '.visibility'
    cmds.setAttr(ikfk_foot_A, 1)
    cmds.setDrivenKeyframe(foot_v, cd = ikfk_foot_A)
    cmds.setAttr(ikfk_foot_A, 0)
    cmds.setAttr(foot_v, 0)
    cmds.setDrivenKeyframe(foot_v, cd = ikfk_foot_A)
    
    b = 'IKFK_leg_' + chr(part)+ '_ctrl'   
    cd = cmds.shadingNode('condition', name='IKFK_leg_' + chr(part) + '_cd', asUtility=True)
    cmds.connectAttr(b + '.blend', cd + '.firstTerm')
    cmds.setAttr(cd + '.secondTerm', 0.5)
    cmds.setAttr(cd + '.operation', 4)
    cmds.setAttr(cd + '.colorIfTrueR', 1)
    cmds.setAttr(cd + '.colorIfFalseR', 0)
    cmds.connectAttr(cd + '.outColor.outColorR', b + '.leg_' + chr(part)+ '_IKFK')
        
def main():
    arm_connection(76)
    arm_connection(82)
    leg_ready()
    leg_connection(76)
    leg_connection(82)
    neck_connection()
    head_connection()
    IKFK_condition(76)
    IKFK_condition(82)