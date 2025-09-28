# -*- coding: UTF-8 -*-

'''
FKとIKのコントローラを作成

import sys

absolute_path = "C:/Users/meidm/Desktop/body_rig_all/create_all_ctrl_all"
sys.path.append(absolute_path)

import create_all_ctrl
import importlib
importlib.reload(create_all_ctrl)
create_all_ctrl.leg_main()
'''
import maya.cmds as cmds
import math

def create_joint(src_joint, new_joint_name, rot):
    # ジョイントの位置を取得
    position = cmds.xform(src_joint, query=True, translation=True, worldSpace=True)
    
    # ジョイントのワールド座標での回転を取得
    rotation = cmds.xform(src_joint, query=True, rotation=True, worldSpace=True)

    # 同じ位置で新しいジョイントを作成
    new_joint = cmds.joint(name=new_joint_name, position=position)
    
    if rot == 1:
        # 新しいジョイントのワールド座標での回転を設定
        cmds.xform(new_joint, rotation=rotation, worldSpace=True)

    return new_joint

def freeze_rotation(joints):
    for joint in joints:
        cmds.makeIdentity(joint, apply=True, rotate=True)

def freeze_scale(joints):
    for joint in joints:
        cmds.makeIdentity(joint, apply=True, scale=True)

def createNodehijtA(n, parent):
    # ジョイントが非表示の場合、何もしない
    if not cmds.getAttr(n + ".visibility"):
        return

    o = cmds.createNode('transform', n=n+'_offset', p=parent)
    cp = cmds.createNode('transform', n=n+'_ctrlSpace', p=o)
    c = cmds.createNode('transform', n=n+'_ctrl', p=cp)
    cmds.matchTransform(o, n, piv=True, pos=True, rot=True)

    for child in cmds.listRelatives(
        n, c=True, pa=True, type='transform'
    ) or []:
        dupchild = createNodehijtA(child, c)
        
    return (o, cp, c)

def createNodehijtB(n, name, parent, num, flag):
    for i in range(num):
        o = cmds.createNode('transform', n=name + '_offset', p=parent)
        cp = cmds.createNode('transform', n=name + '_ctrlSpace', p=o)
        c = cmds.createNode('transform', n=name + '_ctrl', p=cp)
        cmds.matchTransform(o, n, piv=True, pos=True, rot=True)
        
        if flag==0:
            cmds.parent(n, c)
    return(o, cp, c)

def calculate_distance(joint1, joint2):
    # ジョイントのワールド座標を取得
    pos1 = cmds.xform(joint1, query=True, worldSpace=True, translation=True)
    pos2 = cmds.xform(joint2, query=True, worldSpace=True, translation=True)

    # ユークリッド距離を計算
    distance = math.sqrt((pos2[0] - pos1[0]) ** 2 + (pos2[1] - pos1[1]) ** 2 + (pos2[2] - pos1[2]) ** 2)
    return distance

def set_joint_color(joint_name, color):
    # ジョイントの表示オーバーライドを有効にする
    cmds.setAttr(joint_name + '.overrideEnabled', 1)
    cmds.setAttr(joint_name + '.overrideRGBColors', 1)
    cmds.setAttr(joint_name + '.useOutlinerColor', 1)

    # RGB値で色を設定（値は0から1の範囲）
    cmds.setAttr(joint_name + '.overrideColorRGB', color[0], color[1], color[2])
    cmds.setAttr(joint_name + '.outlinerColor', color[0], color[1], color[2])

def create_arm_ctrl(num):
    part = num #L is 76. R is 82.
    
    #FK用のコントローラ作成
    sh = createNodehijtA('shoulder' + '_' + chr(part), None)
    
    Armgp = cmds.createNode('transform', name = chr(part) + '_arm_ctrl_grp')
    set_joint_color(Armgp, [1, 1, 0.39])  # 薄い黄色
    
    cmds.parent(sh[0], chr(part) + '_arm_ctrl_grp')
    cmds.parent('arm_' + chr(part) + '_offset', chr(part) + '_arm_ctrl_grp')
    
    if part == 76:
        #IK用のコントローラを作成
        ik = createNodehijtB('wrist_' + chr(part), 'IK_hand_' + chr(part), None, 1, 1)
        twist = createNodehijtB('elbow_' + chr(part), 'IK_hand_twist_' + chr(part), None, 1, 1)
        shoulder = createNodehijtB('arm_' + chr(part), 'IK_shoulder_' + chr(part), None, 1, 1)
        dis = calculate_distance('elbow_' + chr(part), 'wrist_' + chr(part))
        cmds.setAttr(twist[0] + '.translateZ', -1 * dis)
        
        IKgp = cmds.createNode('transform', name = chr(part) + '_IK_arm_ctrl_grp')
        set_joint_color(IKgp, [0.25, 0.63, 1])  # 薄い蒼色
        #Armgp = cmds.createNode('transform', name = chr(part) + '_arm_ctrl_grp')
        #set_joint_color(Armgp, [1, 1, 0.39])  # 薄い黄色
        cmds.parent(ik[0], twist[0], shoulder[0],IKgp)
        #cmds.parent(IKgp, Armgp)
    

def finger_ctrl(num):
    part = num #L is 76. R is 82.
    
    finger_gp = cmds.createNode('transform', name = 'finger_ctrl_gp_' + chr(part))
    cmds.matchTransform(finger_gp, 'wrist_' + chr(part), piv=True, pos=True, rot=True)
    cmds.parent('finger_ctrl_gp_' + chr(part), chr(part) + '_arm_ctrl_grp')
    cmds.makeIdentity(finger_gp, apply=True, scale=True)
    
    cmds.parent('thoumb_A_' + chr(part) + '_offset', finger_gp)
    cmds.parent('finger_A_' + chr(part) + '_offset', finger_gp)
    cmds.parent('middle_A_' + chr(part) + '_offset', finger_gp)
    cmds.parent('ring_A_' + chr(part) + '_offset', finger_gp)
    cmds.parent('little_A_' + chr(part) + '_offset', finger_gp)
    
    
def create_leg_ctrl(num):
    part = num #L is 76. R is 82.
    
    #FK用のコントローラ作成
    sh = createNodehijtA('leg' + '_' + chr(part), None)
    cmds.delete('ankle_end_' + chr(part) + '_offset')
    cmds.delete('foot_toe_end_' + chr(part) + '_offset')
    
    fk_gp = cmds.createNode('transform', name = chr(part) + '_FK_leg_ctrl_grp')
    cmds.parent(sh[0], fk_gp)
    cmds.parent('knees_' + chr(part) + '_offset', fk_gp)
    cmds.parent('ankle_' + chr(part) + '_offset', fk_gp)
    
    Armgp = cmds.createNode('transform', name = chr(part) + '_leg_ctrl_grp')
    set_joint_color(Armgp, [1, 1, 0.39])  # 薄い黄色
    
    cmds.parent(fk_gp, Armgp)
    
    if part == 76:
        #IK用のコントローラを作成
        gp = cmds.createNode('transform', name = chr(num) + '_IK_leg_ctrl_grp')
        leg_hip = createNodehijtB('leg_' + chr(part), 'IK_' + chr(part) + '_leg_hip', None, 1, 1)
        leg_ctrl = createNodehijtB('ankle_' + chr(part), 'IK_' + chr(part) + '_ankle', None, 1, 1)
        cmds.setAttr(leg_ctrl[0] + '.rotate', 0, 0, 0)
        
        leg_option = createNodehijtB('ankle_' + chr(part), 'IK_' + chr(part) + '_foot_option', None, 1, 1)
        cmds.addAttr(leg_option[2], ln='FootRallAngle', at='float', defaultValue=0)
        cmds.addAttr(leg_option[2], ln='HeelTiltWeight', at='float', defaultValue=0)
        cmds.addAttr(leg_option[2], ln='HeelSwivel', at='float', defaultValue=0)
        cmds.addAttr(leg_option[2], ln='BallSwivel', at='float', defaultValue=0)
        cmds.addAttr(leg_option[2], ln='ToeSwivel', at='float', defaultValue=0)
        cmds.addAttr(leg_option[2], ln='ToeBend', at='float', defaultValue=0)
        cmds.addAttr(leg_option[2], ln='ToeTwist', at='float', defaultValue=0)
        cmds.addAttr(leg_option[2], ln='ToeBrake', at='float', defaultValue=0)
        
        cmds.setAttr(leg_option[2] + '.FootRallAngle', e=True, keyable=True) #AttributeをchannelBoxに表示する
        cmds.setAttr(leg_option[2] + '.HeelTiltWeight', e=True, keyable=True) #AttributeをchannelBoxに表示する
        cmds.setAttr(leg_option[2] + '.HeelSwivel', e=True, keyable=True) #AttributeをchannelBoxに表示する
        cmds.setAttr(leg_option[2] + '.BallSwivel', e=True, keyable=True) #AttributeをchannelBoxに表示する
        cmds.setAttr(leg_option[2] + '.ToeSwivel', e=True, keyable=True) #AttributeをchannelBoxに表示する
        cmds.setAttr(leg_option[2] + '.ToeBend', e=True, keyable=True) #AttributeをchannelBoxに表示する
        cmds.setAttr(leg_option[2] + '.ToeTwist', e=True, keyable=True) #AttributeをchannelBoxに表示する
        cmds.setAttr(leg_option[2] + '.ToeBrake', e=True, keyable=True) #AttributeをchannelBoxに表示する
        
        
        leg_poleVector = createNodehijtB('knees_' + chr(part), 'IK_' + chr(part) + '_leg_poleVector', None, 1, 1)
        dis = calculate_distance('knees_' + chr(part), 'ankle_' + chr(part))
        cmds.setAttr(leg_poleVector[0] + '.translateZ', dis)###distanceで距離を図る
        cmds.setAttr(leg_poleVector[0] + '.rotate', 0, 0, 0)
        cmds.setAttr(leg_option[0] + '.rotate', 0, 0, 0)
        cmds.parent(leg_option[0], leg_ctrl[2])
        cmds.parent(leg_hip[0], leg_ctrl[0], leg_poleVector[0], gp)
    
    
def rename_node_and_children(node, new_name):
    # ノードとその子ノードの名前を変更
    new_node = cmds.rename(node, new_name)
    children = cmds.listRelatives(new_node, allDescendents=True, type='transform') or []
    for child in children:
        if 'L' in child:
            new_child_name = child.replace('L', 'R')
            # 末尾に'1'があれば削除
            if new_child_name.endswith('1'):
                new_child_name = new_child_name[:-1]
            cmds.rename(child, new_child_name)
    return new_node

def create_right_arm_ctrl_from_left():
    # 左腕コントローラを作成
    create_arm_ctrl(76)  # 'L'
    create_arm_ctrl(82)  # 'R'

    # 右腕のコントローラを左腕のコントローラから複製
    duplicated_nodes = cmds.duplicate('L_IK_arm_ctrl_grp', renameChildren=True)
    right_arm_ctrl_grp = rename_node_and_children(duplicated_nodes[0], 'R_IK_arm_ctrl_grp')

    # 複製された右腕コントローラに必要な変換を適用
    cmds.setAttr(right_arm_ctrl_grp + '.rotateY', 180)
    cmds.setAttr(right_arm_ctrl_grp + '.scaleZ', -1)
    
    cmds.parent('L_IK_arm_ctrl_grp', 'L_arm_ctrl_grp')
    cmds.parent('R_IK_arm_ctrl_grp', 'R_arm_ctrl_grp')
    
    #指のコントローラまとめる
    finger_ctrl(76)
    finger_ctrl(82)
    
    cmds.select(cl=True)
    
    
def create_right_leg_ctrl_from_left():
    # 左足コントローラを作成
    create_leg_ctrl(76)  # 'L'
    create_leg_ctrl(82)  # 'R'

    # 右足のコントローラを左足のコントローラから複製
    duplicated_nodes = cmds.duplicate('L_IK_leg_ctrl_grp', renameChildren=True)
    right_ctrl_grp = rename_node_and_children(duplicated_nodes[0], 'R_IK_leg_ctrl_grp')

    # 複製された右足コントローラに必要な変換を適用
    cmds.setAttr(right_ctrl_grp + '.rotateY', 180)
    cmds.setAttr(right_ctrl_grp + '.scaleZ', -1)
    
    cmds.parent('L_IK_leg_ctrl_grp', 'L_leg_ctrl_grp')
    cmds.parent('R_IK_leg_ctrl_grp', 'R_leg_ctrl_grp')
    
    cmds.select(cl=True)
    

#ドライバー用のジョイントの生成
def FK_arm_joint(num, position):
    # 関数を呼び出して新しいジョイントを作成
    part = num #L is 76. R is 82.
    a = create_joint('arm_' + chr(part), position + '_arm_jt_' + chr(part), 1)
    b = create_joint('elbow_' + chr(part), position + '_elbow_jt_' + chr(part), 1)
    c = create_joint('wrist_' + chr(part), position + '_wrist_jt_' + chr(part), 1)

    cmds.select(cl=True)
    freeze_rotation([a])
    
def FK_finger_joint(num, position):
    # 関数を呼び出して新しいジョイントを作成
    part = num #L is 76. R is 82.
    finger_parts = ['thoumb', 'finger', 'middle', 'ring', 'little']
    
    for f in finger_parts:
        #aa = create_joint('shoulder_' + chr(part), position + '_arm_jt_top_' + chr(part), 1)
        a = create_joint(f + '_A_' + chr(part), position + '_' + f + '_A_jt_' + chr(part), 1)
        b = create_joint(f + '_B_' + chr(part), position + '_' + f + '_B_jt_' + chr(part), 1)
        c = create_joint(f + '_C_' + chr(part), position + '_' + f + '_C_jt_' + chr(part), 1)
        cmds.select(cl=True)
        freeze_rotation([a])
        
        if position == 'ble':
            cmds.parent(a, 'ble_wrist_jt_' + chr(part))
        
        elif position == 'bin':
            spell = ['A','B','C']
            for s in spell:
                #dm = cmds.createNode('decomposeMatrix')
                #cmds.connectAttr('ble_' + f + '_' + s + '_jt_' + chr(part) + ".xformMatrix", dm + ".inputMatrix")
                #cmds.connectAttr(dm + ".outputTranslate", position + '_' + f + '_' + s + '_jt_' + chr(part) + ".translate")
                #cmds.connectAttr(dm + ".outputRotate", position + '_' + f + '_' + s + '_jt_' + chr(part) + ".rotate")
                cmds.parentConstraint('ble_' + f + '_' + s + '_jt_' + chr(part), position + '_' + f + '_' + s + '_jt_' + chr(part), mo=True)
                cmds.connectAttr('ble_' + f + '_' + s + '_jt_' + chr(part) + ".scale", position + '_' + f + '_' + s + '_jt_' + chr(part) + ".scale")
            

    cmds.select(cl=True)
    #freeze_rotation([a])
    
def IK_arm_joint(num):
    # 関数を呼び出して新しいジョイントを作成
    part = num #L is 76. R is 82.
    a = create_joint('arm_' + chr(part), 'IK_arm_jt_' + chr(part), 1)
    b = create_joint('elbow_' + chr(part), 'IK_elbow_jt_' + chr(part), 1)
    c = create_joint('wrist_' + chr(part), 'IK_wrist_jt_' + chr(part), 1)

    cmds.select(cl=True)
    freeze_rotation([a])
    
def FK_leg_joint(num, position):
    # 関数を呼び出して新しいジョイントを作成
    part = num #L is 76. R is 82.
    a = create_joint('leg_' + chr(part), position + '_leg_jt_' + chr(part), 1)
    b = create_joint('knees_' + chr(part), position + '_knees_jt_' + chr(part), 1)
    c = create_joint('ankle_' + chr(part), position + '_ankle_jt_' + chr(part), 1)
    d = create_joint('ankle_end_' + chr(part), position + '_ankle_end_jt_' + chr(part), 1)
    cmds.select(cl=True)
    e = create_joint('foot_heel_' + chr(part), position + '_foot_heel_jt_' + chr(part), 1)
    f = create_joint('foot_ball_' + chr(part), position + '_foot_ball_jt_' + chr(part), 1)
    g = create_joint('foot_toe_end_' + chr(part), position + '_foot_toe_end_jt_' + chr(part), 1)
    cmds.select(cl=True)
    
    cmds.parent(e, c)
    cmds.select(cl=True)
    freeze_rotation([a])
    
    #################
    
def IK_leg_joint(num):
    # 関数を呼び出して新しいジョイントを作成
    part = num #L is 76. R is 82.
    a = create_joint('leg_' + chr(part), 'IK_leg_jt_' + chr(part), 1)
    b = create_joint('knees_' + chr(part), 'IK_knees_jt_' + chr(part), 1)
    c = create_joint('ankle_' + chr(part), 'IK_ankle_jt_' + chr(part), 1)
    d = create_joint('ankle_end_' + chr(part), 'IK_ankle_end_jt_' + chr(part), 1)
    cmds.select(cl=True)
    e = create_joint('foot_heel_' + chr(part), 'IK_foot_heel_jt_' + chr(part), 1)
    f = create_joint('foot_ball_' + chr(part), 'IK_foot_ball_jt_' + chr(part), 1)
    g = create_joint('foot_toe_end_' + chr(part), 'IK_foot_toe_end_jt_' + chr(part), 1)
    cmds.select(cl=True)
    h = create_joint('leg_' + chr(part), 'IK_revfootPos_leg_jt_' + chr(part), 1)
    create_joint('knees_' + chr(part), 'IK_revfootPos_knees_jt_' + chr(part), 1)
    create_joint('ankle_' + chr(part), 'IK_revfootPos_ankle_jt_' + chr(part), 1)
    cmds.select(cl=True)
    
    cmds.parent(e, c)
    cmds.select(cl=True)
    freeze_rotation([a, h])
    
    return(a, h)
    
def create_revfootPos(num):
    part = num #L is 76. R is 82.
    
    #leg_driverの作成
    la = cmds.createNode('transform', name = chr(num) + '_revFoot_grp')
    cmds.matchTransform(la, 'ankle_' + chr(part), piv=True, pos=True, rot=False)
    cmds.addAttr(la, ln='FootRall', at='float', defaultValue=0)
    cmds.setAttr(la + '.FootRall', e=True, keyable=True) #AttributeをchannelBoxに表示する
    
    lb = cmds.spaceLocator(n=chr(part) + '_revFoot_space_LOC')[0]
    cmds.matchTransform(lb, 'ankle_' + chr(part), piv=True, pos=True, rot=False)
    lc = cmds.spaceLocator(n=chr(part) + '_heel_swivel_LOC')[0]
    cmds.matchTransform(lc, 'heel_swivel_guide_' + chr(part), piv=True, pos=True, rot=False)
    ld = cmds.spaceLocator(n=chr(part) + '_ball_swivel_shortcut_LOC')[0]
    cmds.matchTransform(ld, 'ball_swivel_guide_' + chr(part), piv=True, pos=True, rot=False)
    le = cmds.spaceLocator(n=chr(part) + '_ball_swivel_LOC')[0]
    cmds.matchTransform(le, 'ball_swivel_guide_' + chr(part), piv=True, pos=True, rot=False)
    lf = cmds.spaceLocator(n=chr(part) + '_toe_swivel_LOC')[0]
    cmds.matchTransform(lf, 'toe_swivel_guide_' + chr(part), piv=True, pos=True, rot=False)
    lg = cmds.spaceLocator(n=chr(part) + '_foot_tilt_inner_LOC')[0]
    cmds.matchTransform(lg, 'foot_tilt_inner_guideR_' + chr(part), piv=True, pos=True, rot=False)
    lh = cmds.spaceLocator(n=chr(part) + '_foot_tilt_outer_LOC')[0]
    cmds.matchTransform(lh, 'foot_tilt_inner_guideL_' + chr(part), piv=True, pos=True, rot=False)
    cmds.select(cl=True)
    
    ja = create_joint('heel_swivel_guide_' + chr(part), chr(part) + '_revfoot_heel_drvjnt', 0)
    jb = create_joint('toe_swivel_guide_' + chr(part), chr(part) + '_revfoot_toeRoll_drvjnt', 0)
    cmds.matchTransform(jb, 'ankle_' + chr(part), piv=True, pos=False, rot=True)
    jc = create_joint('foot_ball_' + chr(part), chr(part) + '_revfoot_ballRoll_drvjnt', 0)
    cmds.matchTransform(jc, 'ankle_' + chr(part), piv=True, pos=False, rot=True)
    jd = create_joint('foot_heel_' + chr(part), chr(part) + '_revfoot_loAnkle_drvjnt', 1)
    je = create_joint('ankle_' + chr(part), chr(part) + '_revfoot_hiAnkle_drvjnt', 0)
    cmds.matchTransform(je, 'ankle_' + chr(part), piv=True, pos=False, rot=True)
    cmds.select(cl=True)
    freeze_rotation([ja, jb, jc, jd, je])
    
    li = cmds.spaceLocator(n=chr(part) + 'IK_' + chr(part) + '_foot_ball_hndl_LOC')[0]#IK
    cmds.matchTransform(li, 'foot_ball_' + chr(part), piv=True, pos=True, rot=False)
    cmds.matchTransform(li, 'foot_heel_' + chr(part), piv=True, pos=False, rot=True)
    cmds.parent(li, jc)
    lj = cmds.spaceLocator(n=chr(part) + 'IK_' + chr(part) + '_foot_loAnkle_hndl_LOC')[0]#IK
    cmds.matchTransform(lj, 'foot_heel_' + chr(part), piv=True, pos=True, rot=False)
    cmds.matchTransform(lj, 'ankle_' + chr(part), piv=True, pos=False, rot=True)
    cmds.parent(lj, jd)
    
    jf = create_joint('foot_ball_' + chr(part), chr(part) + '_revfoot_toe_drvjnt', 0)
    cmds.matchTransform(jf, 'ankle_' + chr(part), piv=True, pos=False, rot=True)
    jg = create_joint('foot_toe_end_' + chr(part), chr(part) + '_revfoot_toe_end_drvjnt', 0)
    cmds.matchTransform(jg, 'ankle_' + chr(part), piv=True, pos=False, rot=True)
    cmds.select(cl=True)
    freeze_rotation([jf, jg])
    cmds.parent(jf, jb)
    
    lk = cmds.spaceLocator(n=chr(part) + 'IK_' + chr(part) + '_foot_toe_hndl_LOC')[0]#IK
    cmds.matchTransform(lk, 'foot_toe_end_' + chr(part), piv=True, pos=True, rot=False)
    cmds.parent(lk, jf)
    
    www1 = [la, lb, lc, ld, le, lf, lg, lh, ja]
    for ii in range(len(www1)-1):
        print('jojo')
        cmds.parent(www1[ii+1], www1[ii])
        cmds.select(cl=True)
        
    #leg_toHideの作成
    lla = cmds.createNode('transform', name = chr(num) + '_leg_loc_toHide_grp')
    
    llb = cmds.spaceLocator(n='IK_' + chr(part) + '_leg_handle_root_grp')[0]
    cmds.matchTransform(llb, 'leg_' + chr(part), piv=True, pos=True, rot=False)
    llc = cmds.spaceLocator(n='IK_' + chr(part) + '_leg_handle_aim_grp')[0]
    cmds.matchTransform(llc, 'leg_' + chr(part), piv=True, pos=True, rot=True)
    lld = cmds.spaceLocator(n='IK_' + chr(part) + '_leg_hndl_LOC')[0]#IK
    cmds.matchTransform(lld, 'ankle_' + chr(part), piv=True, pos=True, rot=False)
    
    www2 = [lla, llb, llc, lld]
    for ii in range(len(www2)-1):
        cmds.parent(www2[ii+1], www2[ii])
        cmds.select(cl=True)
    
    lle = cmds.spaceLocator(n='IK_' + chr(part) + '_revfootPos_hndl_LOC')[0]#IK
    cmds.matchTransform(lle, 'ankle_' + chr(part), piv=True, pos=True, rot=False)
    cmds.parent(lle, lla)
    
    #IK作成(優先角度も決めた方がいいかも？)
    ika = cmds.ikHandle(n=chr(part)+'_IK_leg_hndl', sj='IK_leg_jt_' + chr(part), ee='IK_ankle_jt_' + chr(part), sol='ikRPsolver', s='sticky')
    ikb = cmds.ikHandle(n=chr(part)+'_IK_foot_loAnkle_hndl', sj='IK_ankle_jt_' + chr(part), ee='IK_foot_heel_jt_' + chr(part), sol='ikRPsolver', s='sticky')
    ikc = cmds.ikHandle(n=chr(part)+'_IK_foot_ball_hndl', sj='IK_foot_heel_jt_' + chr(part), ee='IK_foot_ball_jt_' + chr(part), sol='ikRPsolver', s='sticky')
    ikd = cmds.ikHandle(n=chr(part)+'_IK_foot_toe_hndl', sj='IK_foot_ball_jt_' + chr(part), ee='IK_foot_toe_end_jt_' + chr(part), sol='ikRPsolver', s='sticky')
    ike = cmds.ikHandle(n=chr(part)+'_IK_revfootPos_hndl', sj='IK_revfootPos_leg_jt_' + chr(part), ee='IK_revfootPos_ankle_jt_' + chr(part), sol='ikRPsolver', s='sticky')
    
    cmds.parent(ika[0], lld)
    cmds.parent(ikb[0], lj)
    cmds.parent(ikc[0], li)
    cmds.parent(ikd[0], lk)
    cmds.parent(ike[0], lle)
    
    cmds.setAttr(ika[0] + '.rotate', 0, 0, 0)
    cmds.setAttr(ikb[0] + '.rotate', 0, 0, 0)
    cmds.setAttr(ikc[0] + '.rotate', 0, 0, 0)
    cmds.setAttr(ikd[0] + '.rotate', 0, 0, 0)
    cmds.setAttr(ike[0] + '.rotate', 0, 0, 0)
    

    #各コントローラから各要素へコンスト
    cmds.pointConstraint('IK_' + chr(part) + '_leg_hip_ctrl', 'IK_leg_jt_' + chr(part), mo=True)
    cmds.pointConstraint('IK_' + chr(part) + '_leg_hip_ctrl', 'IK_revfootPos_leg_jt_' + chr(part), mo=True)
    cmds.parentConstraint('IK_' + chr(part) + '_ankle_ctrl', chr(part) + '_revFoot_grp', mo=True)
    cmds.pointConstraint('IK_' + chr(part) + '_leg_hip_ctrl', llb, mo=True)
    
    cmds.aimConstraint('IK_' + chr(part) + '_ankle_ctrl', llc,
    aim=(1,0,0), u=(0,1,0), wu=(0,1,0), wut='vector', mo=True) #wut='None'
    
    cmds.pointConstraint(je, lld, mo=True)
    cmds.poleVectorConstraint('IK_' + chr(part) + '_leg_poleVector_ctrl', ika[0])
    
    cmds.pointConstraint('IK_' + chr(part) + '_ankle_ctrl', lle, mo=True)
    cmds.poleVectorConstraint('IK_' + chr(part) + '_leg_poleVector_ctrl', ike[0])
    
    
    #ドリブンキーやコネクションしていく
    cmds.connectAttr('IK_' + chr(part) + '_foot_option_ctrl' + '.translateY', lb + '.translateY')
    cmds.connectAttr('IK_' + chr(part) + '_foot_option_ctrl' + '.HeelSwivel', lc + '.rotateY')
    cmds.connectAttr('IK_' + chr(part) + '_foot_option_ctrl' + '.rotateY', ld + '.rotateY')
    cmds.connectAttr('IK_' + chr(part) + '_foot_option_ctrl' + '.BallSwivel', le + '.rotateY')
    cmds.connectAttr('IK_' + chr(part) + '_foot_option_ctrl' + '.ToeSwivel', lf + '.rotateY')
    
    if part == 76:
        cmds.setAttr('IK_' + chr(part) + '_foot_option_ctrl' + '.translateX', 0)
        cmds.setAttr(lh + '.rotateZ', 0)
        cmds.setDrivenKeyframe(lh + '.rotateZ', cd = 'IK_' + chr(part) + '_foot_option_ctrl' + '.translateX')
        cmds.setAttr('IK_' + chr(part) + '_foot_option_ctrl' + '.translateX', 5)
        cmds.setAttr(lh + '.rotateZ', -25)
        cmds.setDrivenKeyframe(lh + '.rotateZ', cd = 'IK_' + chr(part) + '_foot_option_ctrl' + '.translateX')
        
        
        cmds.setAttr('IK_' + chr(part) + '_foot_option_ctrl' + '.translateX', 0)
        cmds.setAttr(lg + '.rotateZ', 0)
        cmds.setDrivenKeyframe(lg + '.rotateZ', cd = 'IK_' + chr(part) + '_foot_option_ctrl' + '.translateX')
        cmds.setAttr('IK_' + chr(part) + '_foot_option_ctrl' + '.translateX', -5)
        cmds.setAttr(lg + '.rotateZ', 25)#
        cmds.setDrivenKeyframe(lg + '.rotateZ', cd = 'IK_' + chr(part) + '_foot_option_ctrl' + '.translateX')
    
    if part == 82:
        cmds.setAttr('IK_' + chr(part) + '_foot_option_ctrl' + '.translateX', 0)
        cmds.setAttr(lh + '.rotateZ', 0)
        cmds.setDrivenKeyframe(lh + '.rotateZ', cd = 'IK_' + chr(part) + '_foot_option_ctrl' + '.translateX')
        cmds.setAttr('IK_' + chr(part) + '_foot_option_ctrl' + '.translateX', -5)
        cmds.setAttr(lh + '.rotateZ', -25)
        cmds.setDrivenKeyframe(lh + '.rotateZ', cd = 'IK_' + chr(part) + '_foot_option_ctrl' + '.translateX')
        
        
        cmds.setAttr('IK_' + chr(part) + '_foot_option_ctrl' + '.translateX', 0)
        cmds.setAttr(lg + '.rotateZ', 0)
        cmds.setDrivenKeyframe(lg + '.rotateZ', cd = 'IK_' + chr(part) + '_foot_option_ctrl' + '.translateX')
        cmds.setAttr('IK_' + chr(part) + '_foot_option_ctrl' + '.translateX', 5)
        cmds.setAttr(lg + '.rotateZ', 25)#
        cmds.setDrivenKeyframe(lg + '.rotateZ', cd = 'IK_' + chr(part) + '_foot_option_ctrl' + '.translateX')
    
    
    cmds.setAttr('IK_' + chr(part) + '_foot_option_ctrl' + '.translateX', 0)
    
    cmds.setAttr('IK_' + chr(part) + '_foot_option_ctrl' + '.translateZ', 0)
    cmds.setAttr(la + '.FootRall', 0)
    cmds.setDrivenKeyframe(la + '.FootRall', cd = 'IK_' + chr(part) + '_foot_option_ctrl' + '.translateZ')
    cmds.setAttr('IK_' + chr(part) + '_foot_option_ctrl' + '.translateZ', 5)#
    cmds.setAttr(la + '.FootRall', 25)
    cmds.setDrivenKeyframe(la + '.FootRall', cd = 'IK_' + chr(part) + '_foot_option_ctrl' + '.translateZ')
    cmds.setAttr('IK_' + chr(part) + '_foot_option_ctrl' + '.translateZ', -5)#
    cmds.setAttr(la + '.FootRall', -25)
    cmds.setDrivenKeyframe(la + '.FootRall', cd = 'IK_' + chr(part) + '_foot_option_ctrl' + '.translateZ')
    
    cmds.setAttr('IK_' + chr(part) + '_foot_option_ctrl' + '.translateZ', 0)
    
    condition1 = cmds.createNode('condition')
    cmds.setAttr(condition1 + '.operation', 3)
    cmds.connectAttr(la + '.FootRall', condition1 + '.firstTerm')
    cmds.connectAttr(la + '.FootRall', condition1 + '.colorIfFalseR')
    cmds.connectAttr(condition1 + '.outColorR', ja + '.rotateX')
    
    cmds.setAttr(la + '_FootRall' + '.preInfinity', 4)###重要！！
    cmds.setAttr(la + '_FootRall' + '.postInfinity', 4)###重要！！
    
    
    average1 = cmds.createNode('plusMinusAverage')
    cmds.setAttr(average1 + '.operation', 2)
    cmds.connectAttr(la + '.FootRall', average1 + '.input1D[0]')
    cmds.setAttr('IK_' + chr(part) + '_foot_option_ctrl' + '.FootRallAngle', 25)
    cmds.connectAttr('IK_' + chr(part) + '_foot_option_ctrl' + '.FootRallAngle', average1 + '.input1D[1]')
    condition2 = cmds.createNode('condition')
    cmds.setAttr(condition2 + '.operation', 3)
    cmds.connectAttr(la + '.FootRall', condition2 + '.firstTerm')
    cmds.connectAttr(la + '.FootRall', condition2 + '.colorIfTrueR')
    condition3 = cmds.createNode('condition')
    cmds.setAttr(condition3 + '.operation', 3)
    cmds.setAttr(condition3 + '.colorIfFalseG', 0)
    cmds.connectAttr(condition2 + '.outColorR', condition3 + '.firstTerm')
    cmds.connectAttr(condition2 + '.outColorR', condition3 + '.colorIfFalseR')
    cmds.connectAttr(average1 + '.output1D', condition3 + '.colorIfTrueG')
    cmds.connectAttr('IK_' + chr(part) + '_foot_option_ctrl' + '.FootRallAngle', condition3 + '.colorIfTrueR')
    cmds.connectAttr('IK_' + chr(part) + '_foot_option_ctrl' + '.FootRallAngle', condition3 + '.secondTerm')
    cmds.connectAttr(condition3 + '.outColorG', jb + '.rotateY')
    cmds.connectAttr(condition3 + '.outColorR', jc + '.rotateY')
    
    multiply1 = cmds.createNode('multiplyDivide')
    cmds.setAttr(multiply1 + '.operation', 1)
    cmds.connectAttr('IK_' + chr(part) + '_foot_option_ctrl' + '.HeelTiltWeight', multiply1 + '.input1X')
    cmds.connectAttr(multiply1 + '.outputX', li + '.rotateX')
    
    cmds.connectAttr('IK_' + chr(part) + '_foot_option_ctrl' + '.rotateZ', jd + '.rotateX')
    
    cmds.connectAttr('IK_' + chr(part) + '_foot_option_ctrl' + '.ToeBend', jf + '.rotateY')
    cmds.connectAttr('IK_' + chr(part) + '_foot_option_ctrl' + '.ToeBrake', jf + '.rotateZ')
    cmds.connectAttr('IK_' + chr(part) + '_foot_option_ctrl' + '.ToeTwist', jf + '.rotateX')
    
    

def arm_create_driver_ctrl(num):
    part = num #L is 76. R is 82.
    
    # 左腕コントローラを作成
    create_joint('shoulder_' + chr(part), 'shoulder_jt_' + chr(part), 1)
    FK_arm_joint(num, 'FK')
    FK_arm_joint(num, 'ble')
    FK_finger_joint(num, 'ble')
    IK_arm_joint(num)
    
    arm_drvjnt = cmds.createNode('transform', name = chr(num) + '_arm_drvjnt_grp')
    set_joint_color(arm_drvjnt, [0.25, 0.63, 1])  # 薄い蒼色
    arm_IKFK_drvjnt = cmds.createNode('transform', name = chr(num) + '_arm_IKFK_drvjnt_grp')
    set_joint_color(arm_IKFK_drvjnt, [1, 0.23, 0.23]) #薄い赤

    # 右腕のコントローラを左腕のコントローラから複製
    cmds.parent('shoulder_jt_' + chr(num), 'FK_arm_jt_' + chr(num), 'IK_arm_jt_' + chr(num), arm_IKFK_drvjnt)
    cmds.parent(arm_IKFK_drvjnt, arm_drvjnt)
    
    cmds.select(cl=True)
    
def leg_create_driver_ctrl(num):
    part = num
    
    FK_leg_joint(num, 'FK')
    FK_leg_joint(num, 'ble')
    #FK_leg_joint(num, 'bin')
    IK_leg_joint(num)
    
    leg_drvjnt = cmds.createNode('transform', name = chr(num) + '_leg_drvjnt_grp')
    set_joint_color(leg_drvjnt, [0.25, 0.63, 1])  # 薄い蒼色
    leg_IKFK_drvjnt = cmds.createNode('transform', name = chr(num) + '_leg_IKFK_drvjnt_grp')
    set_joint_color(leg_IKFK_drvjnt, [1, 0.23, 0.23]) #薄い赤
    
    cmds.parent('FK_leg_jt_' + chr(part), 'IK_leg_jt_' + chr(part), 'IK_revfootPos_leg_jt_' + chr(part), leg_IKFK_drvjnt)
    cmds.parent(leg_IKFK_drvjnt, leg_drvjnt)
    
    cmds.select(cl=True)

def fk_leg_const(num):
    part = num
    cmds.parentConstraint('leg_' + chr(part) + '_ctrl', 'FK_leg_jt_' + chr(part), mo=True)
    cmds.parentConstraint('knees_' + chr(part) + '_ctrl', 'FK_knees_jt_' + chr(part), mo=True)
    cmds.parentConstraint('ankle_' + chr(part) + '_ctrl', 'FK_ankle_jt_' + chr(part), mo=True)
    cmds.parentConstraint('leg_' + chr(part) + '_ctrl', 'FK_leg_jt_' + chr(part), mo=True)
    cmds.parentConstraint('foot_heel_' + chr(part) + '_ctrl', 'FK_foot_heel_jt_' + chr(part), mo=True)
    cmds.parentConstraint('foot_ball_' + chr(part) + '_ctrl', 'FK_foot_ball_jt_' + chr(part), mo=True)
    
    cmds.parentConstraint('leg_' + chr(part) + '_ctrl', 'knees_' + chr(part) + '_offset', mo=True)
    cmds.parentConstraint('knees_' + chr(part) + '_ctrl', 'ankle_' + chr(part) + '_offset', mo=True)
    
def text_curve(x, y, z, name, part):
    gp = cmds.group(n = name + '_' + chr(part) + '_ctrl', em=True)
    p = cmds.textCurves(n= 'first', f='Courier', t=name + '_' + chr(part))
    pg = cmds.ls(p, sl=True)
    cmds.select(pg, hi=True)
    nu1 = cmds.ls(sl=True, typ='nurbsCurve')
    nu2 = cmds.parent(nu1, w=True)
    cmds.makeIdentity(a=True, t=True, r=True, s=True, n=False, pn=True)
    cmds.xform(ws=True, piv=(0,0,0))
    cmds.select(nu2, hi=True)
    nu3 = cmds.ls(sl=True, typ='nurbsCurve')
    nu4 = cmds.parent(nu3, gp, r=True, s=True)[0]
    cmds.select(cmds.ls(gp)) #
    cmds.xform(cpc=True)
    cmds.scale(1.4, 1.4, 1.4)
    cmds.setAttr(gp + '.overrideEnabled', 1)
    cmds.setAttr(gp + '.overrideColor', 17) #13_red, 6_blue, 17_eyllow, 31_wineRed, 30_murasaki
    cmds.setAttr(gp + '.tx', lock=True, keyable=False, channelBox=False)
    cmds.setAttr(gp + '.ty', lock=True, keyable=False, channelBox=False)
    cmds.setAttr(gp + '.tz', lock=True, keyable=False, channelBox=False)
    cmds.setAttr(gp + '.rx', lock=True, keyable=False, channelBox=False)
    cmds.setAttr(gp + '.ry', lock=True, keyable=False, channelBox=False)
    cmds.setAttr(gp + '.rz', lock=True, keyable=False, channelBox=False)
    cmds.setAttr(gp + '.sx', lock=True, keyable=False, channelBox=False)
    cmds.setAttr(gp + '.sy', lock=True, keyable=False, channelBox=False)
    cmds.setAttr(gp + '.sz', lock=True, keyable=False, channelBox=False)
    cmds.setAttr(gp + '.v', lock=True, keyable=False, channelBox=False)
    cmds.delete(pg, nu2)
    return nu4

def create_blend_node(num, p, parts_name, joint_name):
    part = num #L is 76. R is 82.
    
    #IFとFKのブレンド機能追加TranslateRotate
    blend_node = cmds.shadingNode('pairBlend', name= parts_name + '_TR_blend_' + chr(part), asUtility=True)
    cmds.setAttr(blend_node + '.weight', 0)
    
    cmds.connectAttr('FK_' + parts_name + '_jt_' + chr(part) + ".translate", blend_node + ".inTranslate1")
    cmds.connectAttr('IK_' + parts_name + '_jt_' + chr(part) + ".translate", blend_node + ".inTranslate2")
    cmds.connectAttr('FK_' + parts_name + '_jt_' + chr(part) + ".rotate", blend_node + ".inRotate1")
    cmds.connectAttr('IK_' + parts_name + '_jt_' + chr(part) + ".rotate", blend_node + ".inRotate2")
    cmds.connectAttr(blend_node + ".outTranslate", joint_name + '_' + chr(part) + ".translate")
    cmds.connectAttr(blend_node + ".outRotate", joint_name + '_' + chr(part) + ".rotate")
    
    #IFとFKのブレンド機能追加Scale
    S_blend = cmds.shadingNode('blendColors', name= parts_name + '_S_blend_' + chr(part), asUtility=True)
    cmds.setAttr(S_blend + '.blender', 1)
    cmds.connectAttr('FK_' + parts_name + '_jt_' + chr(part) + ".scale", S_blend + ".color2")
    cmds.connectAttr('IK_' + parts_name + '_jt_' + chr(part) + ".scale", S_blend + ".color1")
    cmds.connectAttr(S_blend + ".output", joint_name + '_' + chr(part) + ".scale")
    
    if p == 'arm':
        ikfk_arm_blend = 'IKFK_arm_' + chr(part)+ '_ctrl' + '.blend'
        cmds.connectAttr(ikfk_arm_blend, blend_node + '.weight')
        cmds.connectAttr(ikfk_arm_blend, S_blend + '.blender')
        
    elif p == 'leg':
        ikfk_leg_blend = 'IKFK_leg_' + chr(part)+ '_ctrl' + '.blend'
        cmds.connectAttr(ikfk_leg_blend, blend_node + '.weight')
        cmds.connectAttr(ikfk_leg_blend, S_blend + '.blender')
    
def IK_blend_arm(num):
    part = num #L is 76. R is 82.
    name = ['IKFK_arm']
    c = text_curve(0.0, 0.0, 0.0, name[0], part)
    gp = cmds.group(n = name[0] + '_' + chr(part) + '_offset', em=True)
    cmds.parent(c, gp)
    
    cmds.addAttr('IKFK_arm_' + chr(part)+ '_ctrl', ln='arm_' + chr(part) + '_IKFK', at='enum', en='IK:FK:')
    cmds.setAttr('IKFK_arm_' + chr(part)+ '_ctrl' + '.arm_' + chr(part) + '_IKFK', e=True, keyable=True) #AttributeをchannelBoxに表示する
    cmds.addAttr('IKFK_arm_' + chr(part)+ '_ctrl', ln='blend', at='double', min=0, max=1, dv=0)
    cmds.setAttr('IKFK_arm_' + chr(part)+ '_ctrl' + '.blend', e=True, keyable=True) #AttributeをchannelBoxに表示する
    
    cmds.parentConstraint('arm_' + chr(part) + '_ctrl', 'FK_arm_jt_' + chr(part), mo=True) #FKコントローラからFKボーンにコンスト
    cmds.parentConstraint('elbow_' + chr(part) + '_ctrl', 'FK_elbow_jt_' + chr(part), mo=True)
    cmds.parentConstraint('wrist_' + chr(part) + '_ctrl', 'FK_wrist_jt_' + chr(part), mo=True)
    cmds.parentConstraint('ble_wrist_jt_' + chr(part), 'finger_ctrl_gp_' + chr(part), mo=True)###
    
    cmds.parentConstraint('shoulder_' + chr(part) + '_ctrl', 'arm_' + chr(part) + '_offset', sr=['x','y','z'], mo=True)#
    cmds.parentConstraint('shoulder_' + chr(part) + '_ctrl', 'shoulder_jt_' + chr(part), mo=True)#
    cmds.parentConstraint('shoulder_' + chr(part) + '_ctrl', 'IK_shoulder_' + chr(part) + '_offset', mo=True)

    cmds.setAttr('IK_elbow_jt_' + chr(part) + '.preferredAngleY', -45)
    cmds.ikHandle(n='IK_hand_' + chr(part), sj='IK_arm_jt_' + chr(part), ee='IK_wrist_jt_' + chr(part), sol='ikRPsolver', s='sticky') #solはなくてもいい？
    cmds.setAttr('IK_hand_' + chr(part) + '.visibility', 0)

    cmds.parent('IK_hand_' + chr(part), 'IK_hand_' + chr(part) + '_ctrl')
    cmds.orientConstraint('IK_hand_' + chr(part) + '_ctrl', 'IK_wrist_jt_' + chr(part), mo=True)
    cmds.pointConstraint('IK_shoulder_' + chr(part) + '_ctrl', 'IK_arm_jt_' + chr(part), mo=True)
    cmds.poleVectorConstraint('IK_hand_twist_' + chr(part) + '_ctrl', 'IK_hand_' + chr(part))
    
    
    create_blend_node(part, 'arm', 'arm', 'ble_arm_jt')
    create_blend_node(part, 'arm', 'elbow', 'ble_elbow_jt')
    create_blend_node(part, 'arm', 'wrist', 'ble_wrist_jt')
    
    
    ###IKの時のスイッチ###
    #IKコントローラの表示
    ik_A = 'IK_hand_' + chr(part) + '_offset' + '.visibility'
    ikfk_arm_A = 'IKFK_arm_' + chr(part)+ '_ctrl' + '.arm_' + chr(part) + '_IKFK' #切り替えスイッチ
    cmds.setDrivenKeyframe(ik_A, cd = ikfk_arm_A) #IK_offsetの視認とIK切り替えスイッチを連動させる
    cmds.setAttr(ikfk_arm_A, 1)
    cmds.setAttr(ik_A, 0)
    cmds.setDrivenKeyframe(ik_A, cd = ikfk_arm_A) #もう一度、IK_offsetの視認とIK切り替えスイッチを連動させる
    cmds.setAttr(ikfk_arm_A, 0)
    #hand_twist
    hand_A = 'IK_hand_twist_' + chr(part) + '_offset' + '.visibility'
    cmds.setDrivenKeyframe(hand_A, cd = ikfk_arm_A)
    cmds.setAttr(ikfk_arm_A, 1)
    cmds.setAttr(hand_A, 0)
    cmds.setDrivenKeyframe(hand_A, cd = ikfk_arm_A)
    cmds.setAttr(ikfk_arm_A, 0)
    
    #FKコントローラの非表示
    #arm
    arm_v = 'arm_' + chr(part) + '_offset' + '.visibility'
    cmds.setAttr(ikfk_arm_A, 1)
    cmds.setDrivenKeyframe(arm_v, cd = ikfk_arm_A)
    cmds.setAttr(ikfk_arm_A, 0)
    cmds.setAttr(arm_v, 0)
    cmds.setDrivenKeyframe(arm_v, cd = ikfk_arm_A)
    
    cmds.setAttr(ikfk_arm_A, 1) #初期はFK表示にする
    
    
def IK_blend_leg(num):
    part = num #L is 76. R is 82.
    name = ['IKFK_leg']
    c = text_curve(0.0, 0.0, 0.0, name[0], part)
    gp = cmds.group(n = name[0] + '_' + chr(part) + '_offset', em=True)
    cmds.parent(c, gp)
    
    cmds.addAttr('IKFK_leg_' + chr(part)+ '_ctrl', ln='leg_' + chr(part) + '_IKFK', at='enum', en='IK:FK:')
    cmds.setAttr('IKFK_leg_' + chr(part)+ '_ctrl' + '.leg_' + chr(part) + '_IKFK', e=True, keyable=True) #AttributeをchannelBoxに表示する
    cmds.addAttr('IKFK_leg_' + chr(part)+ '_ctrl', ln='blend', at='double', min=0, max=1, dv=0)
    cmds.setAttr('IKFK_leg_' + chr(part)+ '_ctrl' + '.blend', e=True, keyable=True) #AttributeをchannelBoxに表示する
    
    create_blend_node(part, 'leg', 'leg', 'ble_leg_jt')
    create_blend_node(part, 'leg', 'knees', 'ble_knees_jt')
    create_blend_node(part, 'leg', 'ankle', 'ble_ankle_jt')
    create_blend_node(part, 'leg', 'foot_heel', 'ble_foot_heel_jt')
    create_blend_node(part, 'leg', 'foot_ball', 'ble_foot_ball_jt')
    
    
    ###IKの時のスイッチ###
    #IKコントローラの表示
    ik_A = chr(part) + '_IK_leg_ctrl_grp' + '.visibility'
    ikfk_leg_A = 'IKFK_leg_' + chr(part)+ '_ctrl' + '.leg_' + chr(part) + '_IKFK' #切り替えスイッチ
    cmds.setDrivenKeyframe(ik_A, cd = ikfk_leg_A) #IK_offsetの視認とIK切り替えスイッチを連動させる
    cmds.setAttr(ikfk_leg_A, 1)
    cmds.setAttr(ik_A, 0)
    cmds.setDrivenKeyframe(ik_A, cd = ikfk_leg_A) #もう一度、IK_offsetの視認とIK切り替えスイッチを連動させる
    cmds.setAttr(ikfk_leg_A, 0)
    
    #FKコントローラの非表示
    leg_v = chr(part) + '_IK_leg_ctrl_grp' + '.visibility'
    cmds.setAttr(ikfk_leg_A, 1)
    cmds.setDrivenKeyframe(leg_v, cd = ikfk_leg_A)
    cmds.setAttr(ikfk_leg_A, 0)
    cmds.setAttr(leg_v, 0)
    cmds.setDrivenKeyframe(leg_v, cd = ikfk_leg_A)
    
    cmds.setAttr('IKFK_leg_' + chr(part)+ '_ctrl' + '.blend', 1) #初期はIK表示にする
    

def finger_const(num):
    part = num #L is 76. R is 82.
    
    finger_parts = ['thoumb', 'finger', 'middle', 'ring', 'little']
    
    for f in finger_parts:
        cmds.parentConstraint(f + '_A_' + chr(part) + '_ctrl', 'ble_' + f + '_A_jt_' + chr(part), mo=True)
        cmds.parentConstraint(f + '_B_' + chr(part) + '_ctrl', 'ble_' + f + '_B_jt_' + chr(part), mo=True)
        cmds.parentConstraint(f + '_C_' + chr(part) + '_ctrl', 'ble_' + f + '_C_jt_' + chr(part), mo=True)
    
def all_ctrl_option(num, main_parts):
    part = num #L is 76. R is 82.
    if not cmds.objExists('rig_grp'):
        rig_gp = cmds.createNode('transform', n='rig_grp')
        set_joint_color(rig_gp, [1, 0, 0])
        cmds.addAttr(rig_gp, ln='globalScale', at='double', min=0, dv=1)
        cmds.setAttr(rig_gp + '.globalScale', e=True, keyable=True) #AttributeをchannelBoxに表示する
        #cmds.connectAttr(rig_gp + '.globalScale', 'globalScale_grp.globalScale')
        

    if not cmds.objExists('driver_jnt_grp'):
        driver_jnt_gp = cmds.createNode('transform', n='driver_jnt_grp')
        set_joint_color(driver_jnt_gp, [0.26, 0.62, 1])
        cmds.connectAttr('rig_grp' + '.globalScale', driver_jnt_gp + '.scaleX')
        cmds.connectAttr('rig_grp' + '.globalScale', driver_jnt_gp + '.scaleY')
        cmds.connectAttr('rig_grp' + '.globalScale', driver_jnt_gp + '.scaleZ')
        cmds.parent(driver_jnt_gp, rig_gp)
        
    if not cmds.objExists('controls_grp'):
        ctrl_gp = cmds.createNode('transform', n='controls_grp')
        set_joint_color(ctrl_gp, [0.26, 0.62, 1])
        cmds.connectAttr('rig_grp' + '.globalScale', ctrl_gp + '.scaleX')
        cmds.connectAttr('rig_grp' + '.globalScale', ctrl_gp + '.scaleY')
        cmds.connectAttr('rig_grp' + '.globalScale', ctrl_gp + '.scaleZ')
        cmds.parent(ctrl_gp, rig_gp)
        
    if not cmds.objExists('null_grp'):
        null_gp = cmds.createNode('transform', n='null_grp')
        set_joint_color(null_gp, [1, 0.23, 0.23])
        cmds.parent(null_gp, rig_gp)
        
    if not cmds.objExists('null_toHide_grp'):
        null_toHide_gp = cmds.createNode('transform', n='null_toHide_grp')
        set_joint_color(null_toHide_gp, [1, 0.23, 0.23])
        cmds.parent(null_toHide_gp, null_gp)
    
    if not cmds.objExists('arm_ctrl_grp'):
        arm_ctrl_gp = cmds.createNode('transform', n='arm_ctrl_grp')
        set_joint_color(arm_ctrl_gp, [1, 1, 0.39])
        cmds.parent(arm_ctrl_gp, 'controls_grp')
        
    if not cmds.objExists('leg_ctrl_grp'):
        leg_ctrl_gp = cmds.createNode('transform', n='leg_ctrl_grp')
        set_joint_color(leg_ctrl_gp, [1, 1, 0.39])
        cmds.parent(leg_ctrl_gp, 'controls_grp')
        
    if not cmds.objExists('arm_drvjnt_grp'):
        arm_drvjnt_gp = cmds.createNode('transform', n='arm_drvjnt_grp')
        set_joint_color(arm_drvjnt_gp, [1, 1, 0.39])
        cmds.parent(arm_drvjnt_gp, 'driver_jnt_grp')
        
    if not cmds.objExists('leg_drvjnt_grp'):
        leg_drvjnt_gp = cmds.createNode('transform', n='leg_drvjnt_grp')
        set_joint_color(leg_drvjnt_gp, [1, 1, 0.39])
        cmds.parent(leg_drvjnt_gp, 'driver_jnt_grp')
        
    
    if main_parts == 'arm':
        cmds.parent('ble_arm_jt_' + chr(part), chr(part) + '_arm_drvjnt_grp')
        
        cmds.parent(chr(part) + '_arm_ctrl_grp', 'arm_ctrl_grp')
        cmds.parent('IKFK_arm_' + chr(part) + '_offset', 'arm_ctrl_grp')
        
        #cmds.parent(chr(part) + '_arm_toHide_grp', 'null_toHide_grp')
        
        cmds.parent(chr(part) + '_arm_drvjnt_grp', 'arm_drvjnt_grp')
        #cmds.parent(chr(part) + '_finger_drvjnt_grp', 'arm_drvjnt_grp')
        
    if main_parts == 'leg':
        cmds.parent('ble_leg_jt_' + chr(part), chr(part) + '_leg_drvjnt_grp')
        
        cmds.parent(chr(part) + '_leg_ctrl_grp', 'leg_ctrl_grp')
        cmds.parent('IKFK_leg_' + chr(part) + '_offset', 'leg_ctrl_grp')
        
        #cmds.parent(chr(part) + '_leg_toHide_grp', 'null_toHide_grp')
        
        cmds.parent(chr(part) + '_leg_drvjnt_grp', 'leg_drvjnt_grp')
        #cmds.parent(chr(part) + '_finger_drvjnt_grp', 'leg_drvjnt_grp')
        
        
        
    cmds.select(cl=True)
    

###バインド用のジョイントを作り、接続している。###
def create_bind_joint(num, main_parts):
    part = num #L is 76. R is 82.
    if main_parts == 'arm':
        create_joint('shoulder_jt_' + chr(part), 'bin_shoulder_jt_' + chr(part), 1)#ガイドのジョイントではなく、ドライバー用のジョイントで生成する。
        #create_joint(chr(part) + '_hand_drvjnt', 'bin_hand_jt_' + chr(part), 1)
        
        #ここでバインドジョイントとコネクトしていいかも
        driver_j = ['shoulder_jt_' + chr(part)]
        driven_j = ['bin_shoulder_jt_' + chr(part)]
        
        cmds.parentConstraint(driver_j[0], driven_j[0], mo=True)
        cmds.connectAttr(driver_j[0] + ".scale", driven_j[0] + ".scale")
        cmds.select(cl=True)
        '''
        for i in range(len(driver_j)):
            dm = cmds.createNode('decomposeMatrix')
            cmds.connectAttr(driver_j[i] + ".worldMatrix[0]", dm + ".inputMatrix") #階層トップのジョイントはworldMatrixでそれ以降はxformMatrixで接続する
            cmds.connectAttr(dm + ".outputTranslate", driven_j[i] + ".translate")
            cmds.connectAttr(dm + ".outputRotate", driven_j[i] + ".rotate")
            cmds.connectAttr(driver_j[i] + ".scale", driven_j[i] + ".scale")
        '''
            
        FK_finger_joint(num, 'bin')

    if main_parts == 'leg':
        create_joint('ble_ankle_jt_' + chr(part), 'bin_ankle_jt_' + chr(part), 1)
        create_joint('ble_foot_heel_jt_' + chr(part), 'bin_foot_heel_jt_' + chr(part), 1)
        create_joint('ble_foot_ball_jt_' + chr(part), 'bin_foot_ball_jt_' + chr(part), 1)
        
        driver_j = ['ble_ankle_jt_' + chr(part), 'ble_foot_heel_jt_' + chr(part), 'ble_foot_ball_jt_' + chr(part)]
        driven_j = ['bin_ankle_jt_' + chr(part), 'bin_foot_heel_jt_' + chr(part), 'bin_foot_ball_jt_' + chr(part)]
        
        for i in range(len(driver_j)):
            cmds.parentConstraint(driver_j[i], driven_j[i], mo=True)
            cmds.connectAttr(driver_j[i] + ".scale", driven_j[i] + ".scale")
        
        '''
        for i in range(len(driver_j)):
            dm = cmds.createNode('decomposeMatrix')
            if i == 0:
                cmds.connectAttr(driver_j[i] + ".worldMatrix[0]", dm + ".inputMatrix") #階層トップのジョイントはworldMatrixでそれ以降はxformMatrixで接続する
            else:
                cmds.connectAttr(driver_j[i] + ".xformMatrix", dm + ".inputMatrix") #階層トップのジョイントはworldMatrixでそれ以降はxformMatrixで接続する
            cmds.connectAttr(dm + ".outputTranslate", driven_j[i] + ".translate")
            cmds.connectAttr(dm + ".outputRotate", driven_j[i] + ".rotate")
            cmds.connectAttr(driver_j[i] + ".scale", driven_j[i] + ".scale")
        '''
        
        
    cmds.select(cl=True)

# 実行部分
def arm_main():
    create_right_arm_ctrl_from_left()
    arm_create_driver_ctrl(76)
    arm_create_driver_ctrl(82)
    
    IK_blend_arm(76)
    IK_blend_arm(82)
    
    finger_const(76)
    finger_const(82)
    
    all_ctrl_option(76, 'arm')
    all_ctrl_option(82, 'arm')
    
    create_bind_joint(76, 'arm')
    create_bind_joint(82, 'arm')

def leg_main():
    create_right_leg_ctrl_from_left()
    leg_create_driver_ctrl(76)
    leg_create_driver_ctrl(82)
    create_revfootPos(76)
    create_revfootPos(82)
    
    fk_leg_const(76)
    fk_leg_const(82)
    
    IK_blend_leg(76)
    IK_blend_leg(82)
    
    all_ctrl_option(76, 'leg')
    all_ctrl_option(82, 'leg')
    
    create_bind_joint(76, 'leg')
    create_bind_joint(82, 'leg')