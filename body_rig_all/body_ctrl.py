# -*- coding: UTF-8 -*-

'''
ボディのコントローラを作成
tag_spine_S, tag_spine_E, の二つのジョイントがあると機能する。
'''

'''
import sys

absolute_path = "C:/Users/meidm/Desktop/body_rig_all/body_ctrl_all"
sys.path.append(absolute_path)

import body_ctrl
import importlib
importlib.reload(body_ctrl)
body_ctrl.body_main()
body_ctrl.neck_main()
'''

import maya.cmds as cmds
import math

def freeze_rotation(joints):
    for joint in joints:
        cmds.makeIdentity(joint, apply=True, rotate=True)

def set_joint_color(joint_name, color):
    # ジョイントの表示オーバーライドを有効にする
    cmds.setAttr(joint_name + '.overrideEnabled', 1)
    cmds.setAttr(joint_name + '.overrideRGBColors', 1)
    cmds.setAttr(joint_name + '.useOutlinerColor', 1)

    # RGB値で色を設定（値は0から1の範囲）
    cmds.setAttr(joint_name + '.overrideColorRGB', color[0], color[1], color[2])
    cmds.setAttr(joint_name + '.outlinerColor', color[0], color[1], color[2])

def createNodehijt(source, name, parent, num, flag):
    for i in range(num):
        o = cmds.createNode('transform', n=name + '_offset', p=parent)
        cp = cmds.createNode('transform', n=name + '_ctrlSpace', p=o)
        c = cmds.createNode('transform', n=name + '_ctrl', p=cp)
        #cmds.matchTransform(o, n, piv=True, pos=True, rot=True)
        
        # デバッグ用ログ
        print("Creating nodes: {}, {}, {} with source {}".format(o, cp, c, source))
        print(source)
        
        if cmds.objExists(source):
            cmds.matchTransform(o, source, piv=True, pos=True, rot=True)
        else:
            cmds.warning("Source object {} does not exist".format(source))
        
        if flag==0:
            cmds.parent(source, c)
    return(o, cp, c)

def createNodehijtA(n, parent):
    # ジョイントが非表示の場合、何もしない
    if not cmds.getAttr(n + ".visibility"):
        return

    original_string = n
    modified_string = original_string.replace('_drvjnt', '')
    name = modified_string
    
    o = cmds.createNode('transform', n=name+'_offset', p=parent)
    cp = cmds.createNode('transform', n=name+'_ctrlSpace', p=o)
    c = cmds.createNode('transform', n=name+'_ctrl', p=cp)
    cmds.matchTransform(o, n, piv=True, pos=True, rot=True)

    for child in cmds.listRelatives(
        n, c=True, pa=True, type='transform'
    ) or []:
        dupchild = createNodehijtA(child, c)
        
    return (o, cp, c)
        
def create_joint(src_joint, new_joint_name):
    # ジョイントの位置を取得
    position = cmds.xform(src_joint, query=True, translation=True, worldSpace=True)
    
    # ジョイントのワールド座標での回転を取得
    rotation = cmds.xform(src_joint, query=True, rotation=True, worldSpace=True)

    # 同じ位置で新しいジョイントを作成
    new_joint = cmds.joint(name=new_joint_name, position=position)
    
    # 新しいジョイントのワールド座標での回転を設定
    cmds.xform(new_joint, rotation=rotation, worldSpace=True)

    return new_joint

def create_joints_between(start_joint, end_joint, bend_joint, num_joints, j):
    # スタートとエンドのジョイントの位置を取得
    start_pos = cmds.xform(start_joint, query=True, worldSpace=True, translation=True)
    end_pos = cmds.xform(end_joint, query=True, worldSpace=True, translation=True)

    # 間隔を計算
    dx = (end_pos[0] - start_pos[0]) / (num_joints - 1)
    dy = (end_pos[1] - start_pos[1]) / (num_joints - 1)
    dz = (end_pos[2] - start_pos[2]) / (num_joints - 1)

    # ジョイントの配置
    x = start_pos[0] + dx * j
    y = start_pos[1] + dy * j
    z = start_pos[2] + dz * j
    position=(x, y, z)
    cmds.xform(bend_joint, translation=(x, y, z), worldSpace=True)

def create_base_joint(upjoint, lojoint, num):
    
    joints = []
    
    for j in range(num):
        cmds.select(cl=True)
        base_joint = create_joint(upjoint, 'base_spine_' + str(j) + '_drvjnt')
        cmds.setAttr(base_joint + '.radius', 0.3)#
        create_joints_between(upjoint, lojoint , base_joint, num, j)
        freeze_rotation([base_joint])
        
        joints.append(base_joint)
        
    return joints

def create_center_ctrl(joints):
    center_main = createNodehijt(joints[1], 'center_main', None, 1, 1)
    center_sub = createNodehijt(joints[1], 'center_sub', None, 1, 1)
    
    cmds.addAttr(center_sub[2], ln='maintainVolume', at='double', min=0, max=1, dv=1)
    cmds.addAttr(center_sub[2], ln='IK_ctrl', at='enum', en='OFF:ON:')
    cmds.addAttr(center_sub[2], ln='FK_ctrl', at='enum', en='OFF:ON:')
    cmds.addAttr(center_sub[2], ln='Micro_ctrl', at='enum', en='OFF:ON:')
    cmds.setAttr(center_sub[2] + '.maintainVolume', e=True, keyable=True) #AttributeをchannelBoxに表示する
    cmds.setAttr(center_sub[2] + '.IK_ctrl', e=True, keyable=True) #AttributeをchannelBoxに表示する
    cmds.setAttr(center_sub[2] + '.FK_ctrl', e=True, keyable=True) #AttributeをchannelBoxに表示する
    cmds.setAttr(center_sub[2] + '.Micro_ctrl', e=True, keyable=True) #AttributeをchannelBoxに表示する
    
    cmds.parent(center_sub[0], center_main[2])
    cmds.parent(center_main[0], 'center_ctrl_grp')

def single_bend_joint(upjoint, lojoint):
    joint_num = 5
    jnt_gp = cmds.createNode('transform', n='spine_drvjnt_grp')
    micro_gp = cmds.createNode('transform', n='spine_micro_ctrl_grp')
    set_joint_color(jnt_gp, [0.26, 0.62, 1.0])  
    set_joint_color(micro_gp, [1, 0.44, 0.7])  # ピンクに近い色
    for j in range(joint_num):
        cmds.select(cl=True)
        bend_joint = create_joint(upjoint, 'spine_' + str(j) + '_drvjnt')
        cmds.setAttr(bend_joint + '.radius', 0.2)#
        create_joints_between(upjoint, lojoint , bend_joint, joint_num, j)
        freeze_rotation([bend_joint])
        #micro_ctrlの作成
        up = createNodehijt(bend_joint, 'spine' + '_micro_' + str(j), None, 1, 1)
        cmds.parent(up[0], micro_gp)
        cmds.parent(bend_joint, jnt_gp)
        set_joint_color(bend_joint, [1, 1, 0.4])  # 黄色に近い色
        cmds.select(cl=True) #これをしないと、ここのジョイントを選択した状態で次に行ってしまう。
        
    cmds.parent(micro_gp, 'spine_ctrl_grp')
        
def create_FK_joint(upjoint, lojoint):
    joint_num = 5
    hide_gp = cmds.createNode('transform', n='spine_toHide_grp')
    ribbon_gp = cmds.createNode('transform', n='spine_ribbon_system_grp')
    fk_gp = cmds.createNode('transform', n='FK_spine_ctrl_grp')
    set_joint_color(hide_gp, [1, 0, 0])  
    set_joint_color(fk_gp, [0, 1, 0])
    cmds.select(cl=True)
    for j in range(joint_num):
        fk_joint = create_joint(upjoint, 'FK_spine_' + str(j) + '_drvjnt')
        cmds.setAttr(fk_joint + '.radius', 0.4)#
        create_joints_between(upjoint, lojoint , fk_joint, joint_num, j)
        freeze_rotation([fk_joint])
        
    cmds.parent('FK_spine_0_drvjnt', ribbon_gp)
    cmds.parent(ribbon_gp, hide_gp)
    
    createNodehijtA('FK_spine_0_drvjnt', None)
    
    cmds.parent('FK_spine_1_offset', fk_gp)
    cmds.parent('FK_spine_0_offset', fk_gp)
    
    cmds.parent(fk_gp, 'spine_ctrl_grp')

def create_IK_joint(lojoint, upjoint, joints):
    cmds.select(cl=True)
    ik_ctrl_gp = cmds.createNode('transform', n='IK_spine_ctrl_grp')
    hip_gp = cmds.createNode('transform', n='hip_ctrl_grp')
    set_joint_color(ik_ctrl_gp, [0.26, 0.62, 1.0])
    
    #コントローラ作成
    ik_upper_ctrl = createNodehijt(upjoint, 'IK_spine_upper', None, 1, 1)
    ik_lower_ctrl = createNodehijt(lojoint, 'IK_spine_lower', None, 1, 1)
    ik_mid_ctrl = createNodehijt(joints[2], 'IK_spine_mid', None, 1, 1)
    cmds.setAttr(ik_upper_ctrl[0] + '.rotate', 0, 0, 0)
    cmds.setAttr(ik_lower_ctrl[0] + '.rotate', 0, 0, 0)
    cmds.setAttr(ik_mid_ctrl[0] + '.rotate', 0, 0, 0)
    
    hip_ctrl = createNodehijt(joints[2], 'hip', None, 1, 1)
    
    # 2つのオブジェクトの位置を取得
    pos1 = cmds.xform(joints[1], query=True, worldSpace=True, translation=True)
    pos2 = cmds.xform(joints[2], query=True, worldSpace=True, translation=True)

    # 中間点の計算
    midpoint = [(p1 + p2) / 2 for p1, p2 in zip(pos1, pos2)]

    # 新たなオブジェクトを中間点に移動
    cmds.move(midpoint[0], midpoint[1], midpoint[2], hip_ctrl)
    
    #カラー変更
    set_joint_color(ik_upper_ctrl[0], [1.0, 1.0, 0.39])
    set_joint_color(ik_lower_ctrl[0], [1.0, 1.0, 0.39])
    set_joint_color(ik_mid_ctrl[0], [1.0, 1.0, 0.39])
    
    cmds.parent(ik_upper_ctrl[0], ik_lower_ctrl[0], ik_mid_ctrl[0], ik_ctrl_gp)
    cmds.parent(hip_ctrl[0], hip_gp)
    
    cmds.select(cl=True)
    
    #ジョイントを作成
    ik_lower = create_joint(lojoint, 'IK_spine_lower_drvjnt')
    ik_mid = create_joint(joints[2], 'IK_spine_mid_drvjnt')
    ik_upper = create_joint(upjoint, 'IK_spine_upper_drvjnt')
    
    set_joint_color(ik_lower, [0.26, 0.62, 1.0])
    set_joint_color(ik_mid, [0.26, 0.62, 1.0])
    set_joint_color(ik_upper, [0.26, 0.62, 1.0])
    
    cmds.setAttr(ik_lower + '.radius', 0.6)#
    cmds.setAttr(ik_mid + '.radius', 0.6)#
    cmds.setAttr(ik_upper + '.radius', 0.6)#
    
    ik_joints = [ik_lower, ik_mid, ik_upper]
    
    cmds.parent('IK_spine_ctrl_grp', 'spine_ctrl_grp')
    cmds.parent('hip_ctrl_grp', 'spine_ctrl_grp')

def calculate_distance(joint1, joint2):
    # ジョイントのワールド座標を取得
    pos1 = cmds.xform(joint1, query=True, worldSpace=True, translation=True)
    pos2 = cmds.xform(joint2, query=True, worldSpace=True, translation=True)

    # ユークリッド距離を計算
    distance = math.sqrt((pos2[0] - pos1[0]) ** 2 + (pos2[1] - pos1[1]) ** 2 + (pos2[2] - pos1[2]) ** 2)
    return distance

def position_cv_to_joint(joint_root, joint_end, plane_shape, i, offset):
    # ジョイントの距離を計算
    distance = calculate_distance(joint_root, joint_end)

    # 指定された CV の位置をジョイントの位置に合わせる
    for j in range(4):
        cmds.setAttr(plane_shape + '.controlPoints[' + str(i + j) + '].xValue', distance - offset)

def set_cv_to_interpolated_position(plane_shape, cv1, cv2, cv_target, ratio):
    # 2つのジョイントの位置を取得して補間する
    for j in range(4):
        cv1_pos = cmds.getAttr(plane_shape + '.controlPoints[' + str(cv1 + j) + '].xValue')
        cv2_pos = cmds.getAttr(plane_shape + '.controlPoints[' + str(cv2 + j) + '].xValue')
        d = cv2_pos - cv1_pos
        point = cv1_pos + d * ratio
        cmds.setAttr(plane_shape + '.controlPoints[' + str(cv_target + j) + '].xValue', point)
        
def create_follicles_on_surface(num_follicles, follicle_name_prefix, surface_name):
    '''
    指定されたNURBSサーフェスにフォリクルを生成する関数

    :param num_follicles: 生成するフォリクルの数
    :param follicle_name_prefix: フォリクルに付ける名前のプレフィックス
    :param surface_name: 操作するNURBSサーフェスの名前
    '''
    # フォリクルを生成
    
    fol = []
    
    for i in range(num_follicles):
        # フォリクルの作成
        follicleShape = cmds.createNode('follicle', name=follicle_name_prefix + 'Shape' + str(i))
        follicleTransform = cmds.listRelatives(follicleShape, parent=True)[0]
        cmds.rename(follicleTransform, follicle_name_prefix + str(i))

        # parameterU を等間隔に設定（フォリクルが1つの場合は中央に配置）
        if num_follicles == 1:
            parameterU = 0.5
        else:
            parameterU = float(i) / (num_follicles - 1)

        # フォリクルのパラメータを設定
        cmds.setAttr(follicleShape + '.parameterU', parameterU)
        cmds.setAttr(follicleShape + '.parameterV', 0.5)

        # フォリクルをNURBSサーフェスに接続
        cmds.connectAttr(surface_name + '.local', follicleShape + '.inputSurface')
        cmds.connectAttr(surface_name + '.worldMatrix[0]', follicleShape + '.inputWorldMatrix')
        cmds.connectAttr(follicleShape + '.outTranslate', follicleTransform + '.translate')
        cmds.connectAttr(follicleShape + '.outRotate', follicleTransform + '.rotate')
        
        if i == 0:
            cmds.createNode('transform', name=follicle_name_prefix + '_gp')
            cmds.parent(follicleTransform, follicle_name_prefix + '_gp')
        else:
            cmds.parent(follicleTransform, follicle_name_prefix + '_gp')
            
        fol.append(follicleTransform)
        
    return fol

def create_nurbs(joints, upper): #ジョイントの数によって変えるようにする
    
    # NURBS プレーンの作成
    nrb1 = upper + '_ribbon_driver_nrb'
    upPlane = cmds.nurbsPlane(name = nrb1, width=1, lengthRatio=1, patchesU=len(joints)-1, patchesV=1, ax=(0,1,0))[0]
    # NURBSプレーンのピボットを移動
    cmds.move(-0.5, 0, 0, upPlane + '.scalePivot', upPlane + '.rotatePivot', relative=True)
    upPlane_shape = cmds.listRelatives(upPlane, pa = True)
    
    # ジョイントAの位置と回転をプレーンに合わせる
    up = joints[0]
    cmds.matchTransform(upPlane, up)
    
    # 各ジョイントに対して CV を配置
    position_cv_to_joint(joints[0], joints[0], upPlane_shape[0], 0, 0)

    y = len(joints)
    for i in range(y-2):
        x = 4 * (y - ((y-2)-i))
        position_cv_to_joint(joints[0], joints[i+1], upPlane_shape[0], x, (i+1)/(y-1))
        
    position_cv_to_joint(joints[0], joints[-1], upPlane_shape[0], 4*(y+1), 1)
    
    # CV[1][0:3] を [0][0:3] と [2][0:3] の間の 1/3 の位置に設定
    set_cv_to_interpolated_position(upPlane_shape[0], 0, 8, 4, 1.0/3.0)
    # CV[4][0:3] を [3][0:3] と [5][0:3] の間の 2/3 の位置に設定
    set_cv_to_interpolated_position(upPlane_shape[0], 4*(y+1)-8, 4*(y+1), 4*(y+1)-4, 2.0/3.0)
    
    base_fol = create_follicles_on_surface(y, upper + '_base_follicle', upPlane) ###
    
    nrb2 = cmds.duplicate(upPlane, name = 'IK_' + upper + '_mid_ribbon_driver_nrb')[0]
    mid_fol = create_follicles_on_surface(1, upper + '_IKmid_follicle', nrb2)
    
    nrb3 = cmds.duplicate(upPlane, name = 'IK_' + upper + '_tip_ribbon_driver_nrb')[0]
    tip_fol = create_follicles_on_surface(2, upper + '_IKtip_follicle', nrb3)
    
    cmds.setAttr(upPlane + '.rotateX', 90)
    cmds.setAttr(nrb2 + '.rotateX', 90)
    cmds.setAttr(nrb3 + '.rotateX', 90)
    
    cmds.parent(upPlane, nrb2, nrb3, 'spine_ribbon_system_grp')
    
    #follicleにジョイントを親子付する。
    for w in range(y):
        cmds.parent(joints[w], base_fol[w])
        add_ctrl_spaces(base_fol[w], '_fol')
        
    cmds.parent('IK_spine_mid_drvjnt', mid_fol[0])
    add_ctrl_spaces(mid_fol[0], '_fol')
    
    cmds.parent('IK_spine_lower_drvjnt', tip_fol[1])
    add_ctrl_spaces(tip_fol[1], '_fol')
    cmds.parent('IK_spine_upper_drvjnt', tip_fol[0])
    add_ctrl_spaces(tip_fol[0], '_fol')
        
        

def add_ctrl_space_for_node(parent_node, rename):
    # 子ノードの名前を取得
    child_node = cmds.listRelatives(parent_node, children=True, type='transform')
    if not child_node:
        cmds.warning("'{}'には子ノードがありません。".format(parent_node))
        return

    child_node = child_node[0]
    
    # 新しいノードの名前を生成
    base_name = child_node.replace('_drvjnt', rename)
    ctrl_space_name = '{}_ctrlSpace'.format(base_name)
    
    # 既存の同名ノードが存在する場合、末尾に番号を追加して一意の名前を生成
    i = 1
    while cmds.objExists(ctrl_space_name):
        ctrl_space_name = "{}_ctrlSpace{}".format(base_name, i)
        i += 1

    # 1. 新しいノードを作成します。
    ctrl_space = cmds.group(em=True, name=ctrl_space_name)

    # 2. 新しいノードのワールド変換を元の子ノードのワールド変換と同じに設定します。
    cmds.matchTransform(ctrl_space, child_node)

    # 3. 元の子ノードを新しいノードの子としてペアレントします。
    cmds.parent(child_node, ctrl_space)

    # 4. 新しいノードを元の親ノードの子としてペアレントします。
    cmds.parent(ctrl_space, parent_node)

def add_ctrl_spaces(node, rename):
    # ユーザーの選択を取得
    #selected_nodes = cmds.ls(selection=True)
    selected_nodes = node
    add_ctrl_space_for_node(selected_nodes, rename)

        
# 距離測定ノードを作成
def create_mesure(start_name, end_name, mesure_name, upjoint):
    
    start_point = cmds.createNode('locator', name=start_name + 'Shape')
    start_point_T = cmds.listRelatives(start_point, parent=True)[0]
    end_point = cmds.createNode('locator', name=end_name + 'Shape')
    end_point_T = cmds.listRelatives(end_point, parent=True)[0]
    
    distance_node = cmds.createNode('distanceDimShape', name=mesure_name + 'Shape')
    cmds.connectAttr(start_point + '.worldPosition[0]', distance_node + '.startPoint')
    cmds.connectAttr(end_point + '.worldPosition[0]', distance_node + '.endPoint')
    distance_node_T = cmds.listRelatives(distance_node, parent=True)[0]
    
    #cmds.parent(start_point_T, end_point_T, distance_node_T, upjoint + '_distance_grp')
    
    return(start_point_T, end_point_T, distance_node, distance_node_T)

def create_distance_LOC(joints, name):
    gp = cmds.createNode('transform', name = name + '_volume_distance_grp')
    
    upS, upE, upD, upDT = create_mesure('spine_upper_volume_distance_LOCa', 'spine_upper_volume_distance_LOCb', 'spine_upper_volume_distance', 'spine_upper')
    cmds.matchTransform(upS, joints[-1], piv=True, pos=True, rot=True)
    cmds.matchTransform(upE, joints[2], piv=True, pos=True, rot=True)
    cmds.pointConstraint('IK_spine_upper_ctrl', upS)
    cmds.pointConstraint('IK_spine_mid_ctrl', upE)
    
    loS, loE, loD, loDT = create_mesure('spine_lower_volume_distance_LOCa', 'spine_lower_volume_distance_LOCb', 'spine_lower_volume_distance', 'spine_lower')
    cmds.matchTransform(loS, joints[2], piv=True, pos=True, rot=True)
    cmds.matchTransform(loE, joints[0], piv=True, pos=True, rot=True)
    cmds.pointConstraint('IK_spine_mid_ctrl', loS)
    cmds.pointConstraint('IK_spine_lower_ctrl', loE)
    
    miS, miE, miD, miDT = create_mesure('spine_mid_volume_distance_LOCa', 'spine_mid_volume_distance_LOCb', 'spine_mid_volume_distance', 'spine_mid')
    cmds.matchTransform(miS, joints[-1], piv=True, pos=True, rot=True)
    cmds.matchTransform(miE, joints[0], piv=True, pos=True, rot=True)
    cmds.pointConstraint('IK_spine_upper_ctrl', miS)
    cmds.pointConstraint('IK_spine_lower_ctrl', miE)
    
    cmds.parent(upS, upE, upDT, loS, loE, loDT, miS, miE, miDT, gp)
    
    cmds.parent(gp, 'spine_toHide_grp')

def const_ctrl():
    www=0
    cmds.parentConstraint('center_sub_ctrl', 'spine_ctrl_grp', mo=True)
    
    cmds.parentConstraint('hip_ctrl', 'FK_spine_0_offset', mo=True)
    
    cmds.parentConstraint('FK_spine_4_ctrl', 'IK_spine_upper_offset', mo=True)
    cmds.parentConstraint('hip_ctrl', 'IK_spine_lower_offset', mo=True)
    cmds.parentConstraint('IK_spine_upper_ctrl', 'IK_spine_mid_offset', mo=True)
    cmds.parentConstraint('IK_spine_lower_ctrl', 'IK_spine_mid_offset', mo=True)
    
    cmds.parentConstraint('IK_spine_lower_ctrl', 'spine_micro_0_offset', mo=True)
    cmds.parentConstraint('base_spine_1_drvjnt', 'spine_micro_1_offset', mo=True)
    cmds.parentConstraint('base_spine_2_drvjnt', 'spine_micro_2_offset', mo=True)
    cmds.parentConstraint('base_spine_3_drvjnt', 'spine_micro_3_offset', mo=True)
    cmds.parentConstraint('base_spine_4_drvjnt', 'spine_micro_4_offset', mo=True)
    
    
    #スケール接続
    cmds.parentConstraint('spine_micro_0_ctrl', 'spine_0_drvjnt', mo=True)
    cmds.scaleConstraint('spine_micro_0_ctrl', 'spine_0_drvjnt', mo=True)
    cmds.parentConstraint('spine_micro_1_ctrl', 'spine_1_drvjnt', mo=True)#スケール接続
    cmds.parentConstraint('spine_micro_2_ctrl', 'spine_2_drvjnt', mo=True)#スケール接続
    cmds.parentConstraint('spine_micro_3_ctrl', 'spine_3_drvjnt', mo=True)#スケール接続
    cmds.parentConstraint('spine_micro_4_ctrl', 'spine_4_drvjnt', mo=True)#スケール接続
    
    cmds.parentConstraint('FK_spine_0_ctrl', 'FK_spine_0_drvjnt', mo=True)
    cmds.parentConstraint('FK_spine_1_ctrl', 'FK_spine_1_drvjnt', mo=True)
    cmds.parentConstraint('FK_spine_2_ctrl', 'FK_spine_2_drvjnt', mo=True)
    cmds.parentConstraint('FK_spine_3_ctrl', 'FK_spine_3_drvjnt', mo=True)
    cmds.parentConstraint('FK_spine_4_ctrl', 'FK_spine_4_drvjnt', mo=True)
    
    cmds.parentConstraint('IK_spine_lower_ctrl', 'IK_spine_lower_drvjnt', mo=True)
    cmds.parentConstraint('IK_spine_upper_ctrl', 'IK_spine_upper_drvjnt', mo=True)
    cmds.parentConstraint('IK_spine_mid_ctrl', 'IK_spine_mid_drvjnt', mo=True)
    cmds.scaleConstraint('IK_spine_lower_ctrl', 'IK_spine_lower_drvjnt', mo=True)
    cmds.scaleConstraint('IK_spine_upper_ctrl', 'IK_spine_upper_drvjnt', mo=True)
    cmds.scaleConstraint('IK_spine_mid_ctrl', 'IK_spine_mid_drvjnt', mo=True)
    
    
    #スケール用の接続
    cmds.connectAttr('spine_micro_1_ctrl' + '.scaleX', 'spine_1_drvjnt' + '.scaleX')
    cmds.connectAttr('spine_micro_2_ctrl' + '.scaleX', 'spine_2_drvjnt' + '.scaleX')
    cmds.connectAttr('spine_micro_3_ctrl' + '.scaleX', 'spine_3_drvjnt' + '.scaleX')
    cmds.connectAttr('spine_micro_4_ctrl' + '.scale', 'spine_4_drvjnt' + '.scale')
    
    mult_spine_gs = cmds.shadingNode("multiplyDivide", asUtility=True, name="muldiv_spine_globalScale")
    mult_spine_vc = cmds.shadingNode("multiplyDivide", asUtility=True, name="muldiv_spine_volume_compare")
    mult_spine_vp = cmds.shadingNode("multiplyDivide", asUtility=True, name="muldiv_spine_volume_power")
    mult_spine_vd = cmds.shadingNode("multiplyDivide", asUtility=True, name="muldiv_spine_volume_divideByOne")
    bc_spine_vs = cmds.shadingNode('blendColors', name='bc_spineMaintainVolume_switch', asUtility=True)
    mult_spine_01_s = cmds.shadingNode("multiplyDivide", asUtility=True, name="muldiv_spine_01_scaleMix")
    mult_spine_02_s = cmds.shadingNode("multiplyDivide", asUtility=True, name="muldiv_spine_02_scaleMix")
    mult_spine_03_s = cmds.shadingNode("multiplyDivide", asUtility=True, name="muldiv_spine_03_scaleMix")
    
    a = cmds.getAttr('spine_upper_volume_distance' + '.distance')
    b = cmds.getAttr('spine_mid_volume_distance' + '.distance')
    c = cmds.getAttr('spine_lower_volume_distance' + '.distance')
    cmds.setAttr(mult_spine_gs + '.input2', a, b, c) #
    
    cmds.setAttr(mult_spine_vc + '.operation', 2)
    cmds.connectAttr(mult_spine_gs + '.output', mult_spine_vc + '.input2')
    cmds.connectAttr('spine_upper_volume_distance' + '.distance', mult_spine_vc + '.input1X')
    cmds.connectAttr('spine_mid_volume_distance' + '.distance', mult_spine_vc + '.input1Y')
    cmds.connectAttr('spine_lower_volume_distance' + '.distance', mult_spine_vc + '.input1Z')
    cmds.connectAttr(mult_spine_vc + '.output', mult_spine_vp + '.input1')
    
    cmds.setAttr(mult_spine_vp + '.operation', 3)
    cmds.setAttr(mult_spine_vp + '.input2', 0.5, 0.5, 0.5) #kari
    cmds.connectAttr(mult_spine_vp + '.output', mult_spine_vd + '.input2')
    
    cmds.setAttr(mult_spine_vd + '.input1', 1, 1, 1)
    cmds.setAttr(mult_spine_vd + '.operation', 2)
    
    cmds.setAttr(bc_spine_vs + '.color2', 1, 1, 1)
    cmds.connectAttr('center_sub_ctrl' + '.maintainVolume', bc_spine_vs + '.blender')#
    cmds.connectAttr(mult_spine_vd + '.output', bc_spine_vs + '.color1')
    
    cmds.connectAttr('spine_micro_1_ctrl' + '.scale', mult_spine_01_s + '.input1')
    cmds.connectAttr(bc_spine_vs + '.outputB', mult_spine_01_s + '.input2Y')
    cmds.connectAttr(bc_spine_vs + '.outputB', mult_spine_01_s + '.input2Z')
    cmds.connectAttr('spine_micro_2_ctrl' + '.scale', mult_spine_02_s + '.input1')
    cmds.connectAttr(bc_spine_vs + '.outputG', mult_spine_02_s + '.input2Y')
    cmds.connectAttr(bc_spine_vs + '.outputG', mult_spine_02_s + '.input2Z')
    cmds.connectAttr('spine_micro_3_ctrl' + '.scale', mult_spine_03_s + '.input1')
    cmds.connectAttr(bc_spine_vs + '.outputR', mult_spine_03_s + '.input2Y')
    cmds.connectAttr(bc_spine_vs + '.outputR', mult_spine_03_s + '.input2Z')
    
    cmds.connectAttr(mult_spine_01_s + '.outputY', 'spine_1_drvjnt' + '.scaleY')
    cmds.connectAttr(mult_spine_01_s + '.outputZ', 'spine_1_drvjnt' + '.scaleZ')
    cmds.connectAttr(mult_spine_02_s + '.outputY', 'spine_2_drvjnt' + '.scaleY')
    cmds.connectAttr(mult_spine_02_s + '.outputZ', 'spine_2_drvjnt' + '.scaleZ')
    cmds.connectAttr(mult_spine_03_s + '.outputY', 'spine_3_drvjnt' + '.scaleY')
    cmds.connectAttr(mult_spine_03_s + '.outputZ', 'spine_3_drvjnt' + '.scaleZ')

    
    
def bindskin():
    joint1 = ['IK_spine_upper_drvjnt', 'IK_spine_lower_drvjnt', 'IK_spine_mid_drvjnt']
    cmds.skinCluster(joint1, 'spine_ribbon_driver_nrb', toSelectedBones=True, mi=3)
    joint2 = ['FK_spine_0_drvjnt', 'FK_spine_1_drvjnt', 'FK_spine_2_drvjnt', 'FK_spine_3_drvjnt', 'FK_spine_4_drvjnt']
    cmds.skinCluster(joint2, 'IK_spine_tip_ribbon_driver_nrb', toSelectedBones=True, mi=2)
    joint3 = ['IK_spine_upper_drvjnt', 'IK_spine_lower_drvjnt']
    cmds.skinCluster(joint3, 'IK_spine_mid_ribbon_driver_nrb', toSelectedBones=True, mi=2)

def all_ctrl_option():
    if not cmds.objExists('rig_grp'):
        rig_gp = cmds.createNode('transform', n='rig_grp')
        set_joint_color(rig_gp, [1, 0, 0])
        #cmds.addAttr(rig_gp, ln='globalScale', at='double', min=0, max=1, dv=1)
        cmds.addAttr(rig_gp, ln='globalScale', at='double', min=0, dv=1)
        cmds.setAttr(rig_gp + '.globalScale', e=True, keyable=True) #AttributeをchannelBoxに表示する
        
    cmds.connectAttr('rig_grp' + '.globalScale', "muldiv_spine_globalScale" + '.input1X')#
    cmds.connectAttr('rig_grp' + '.globalScale', "muldiv_spine_globalScale" + '.input1Y')#
    cmds.connectAttr('rig_grp' + '.globalScale', "muldiv_spine_globalScale" + '.input1Z')#

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
        #cmds.parent('globalScale_grp', null_gp)
        
    if not cmds.objExists('null_toHide_grp'):
        null_toHide_gp = cmds.createNode('transform', n='null_toHide_grp')
        set_joint_color(null_toHide_gp, [1, 0.23, 0.23])
        cmds.parent(null_toHide_gp, null_gp)
        
    cmds.parent('spine_drvjnt_grp', 'driver_jnt_grp')
    cmds.parent('center_ctrl_grp', 'controls_grp')
    cmds.parent('spine_ctrl_grp', 'controls_grp')
    cmds.parent('spine_toHide_grp', 'null_toHide_grp')
    
    cmds.parent('spine_base_follicle_gp', 'spine_ribbon_system_grp')
    cmds.parent('spine_IKmid_follicle_gp', 'spine_ribbon_system_grp')
    cmds.parent('spine_IKtip_follicle_gp', 'spine_ribbon_system_grp')

def create_root_ctrl():
    root_c = createNodehijt('gide_all', 'root', None, 1, 1)
    cmds.parent(root_c[0], 'controls_grp')
    cmds.parentConstraint(root_c[2], 'center_main_offset', mo=True)


#バインド用のジョイントを生成かつ、ドライバージョイントと接続    
def create_bind_bend_joint(parts, joint_num):
    
    cmds.select(cl=True)
    for j in range(joint_num):
        drv_joint = parts + '_' + str(j) + '_drvjnt'
        bin_joint = 'bin_' + parts + '_' + str(j) + '_jt'
        create_joint(drv_joint, bin_joint)
        print('www')
    
    cmds.select(cl=True)
    
    #ドライバー用のジョイントとバインドジョイントの接続    
    for j in range(joint_num):
        drv_joint = parts + '_' + str(j) + '_drvjnt'
        bin_joint = 'bin_' + parts + '_' + str(j) + '_jt'
        cmds.parentConstraint(drv_joint, bin_joint, mo=True)
        cmds.connectAttr(drv_joint + ".scale", bin_joint + ".scale")
        print('www')
        
    cmds.select(cl=True)


def body_main():
    center_ctrl_gp = cmds.createNode('transform', n='center_ctrl_grp')
    set_joint_color(center_ctrl_gp, [1, 1, 0.39])
    
    spine_ctrl_gp = cmds.createNode('transform', n='spine_ctrl_grp')
    set_joint_color(spine_ctrl_gp, [1, 1, 0.39])
    
    joints = create_base_joint('tag_spine_S', 'tag_spine_E', 5)
    
    create_center_ctrl(joints)
    
    single_bend_joint(joints[0], joints[-1])
    create_FK_joint(joints[0], joints[-1])
    create_IK_joint(joints[0], joints[-1], joints)
    create_nurbs(joints, 'spine')
    create_distance_LOC(joints, 'spine')
    const_ctrl()
    all_ctrl_option()
    bindskin()
    
    create_root_ctrl()
    
    #バインド用のジョイント作成
    create_bind_bend_joint('spine', 5)


#首と頭は4つのターゲットを使って、頭のリグを構築していく。
#霊夢リグは首にもスケールやベンドの仕組みを使用しているが今回は無視
def neck_main():
    neck_ctrl_gp = cmds.createNode('transform', n='neck_ctrl_grp')
    neck_joint_gp = cmds.createNode('transform', n='neck_drvjnt')
    set_joint_color(neck_ctrl_gp, [1, 1, 0.39])
    
    head_ctrl_gp = cmds.createNode('transform', n='head_ctrl_grp')
    head_joint_gp = cmds.createNode('transform', n='head_drvjnt')
    set_joint_color(head_ctrl_gp, [1, 1, 0.39])
    
    tag_neck = ['tag_neck_0', 'tag_neck_1', 'tag_neck_2']#ターゲット
    
    joints = []
    i = 0
    
    for j in tag_neck:
        neck_joint = create_joint(j, 'neck_' + str(i) + '_drvjnt')
        freeze_rotation([neck_joint])
        i += 1
        
        joints.append(neck_joint)
    
    neck0 = createNodehijt(joints[0], 'neck_' + str(0), None, 1, 1)
    neck1 = createNodehijt(joints[1], 'neck_' + str(1), None, 1, 1)
    
    cmds.parent(neck0[0], neck1[0], neck_ctrl_gp)
    cmds.parent(joints[0], neck_joint_gp)
    
    cmds.parentConstraint(neck0[2], joints[0], mo=True)
    cmds.parentConstraint(neck1[2], joints[1], mo=True)
    cmds.parentConstraint(neck0[2], neck1[0], mo=True) #今回は首コン１から首コン２のオフセットにコンストしている。
    
    
    #head
    head_joint = create_joint('tag_neck_2', 'head_0_drvjnt')
    freeze_rotation([head_joint])
    
    head0 = createNodehijt('tag_neck_2', 'head', None, 1, 1)
    
    cmds.parent(head0[0], head_ctrl_gp)
    cmds.parent(head_joint, head_joint_gp)
    
    cmds.parentConstraint(head0[2], head_joint, mo=True)
    
    #まとめてグループに入れる
    cmds.parent(neck_joint_gp, head_joint_gp, 'driver_jnt_grp')
    cmds.parent(neck_ctrl_gp, head_ctrl_gp, 'controls_grp')
    
    #バインド用のジョイント作成
    create_bind_bend_joint('neck', 2)
    create_bind_bend_joint('head', 1)
